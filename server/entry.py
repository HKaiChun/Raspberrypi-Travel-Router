from __future__ import annotations

from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import TypedDict, Literal

import json

from . import api, session


class _ResponseInit(TypedDict, total=False):
    status: int
    headers: dict[str, str]


class Request(TypedDict):
    method: Literal["GET"] | Literal["POST"]
    request: EntryHandler


def buildResponse(resp: EntryHandler, bodyInit: str, responseInit: _ResponseInit):
    resp.send_response(responseInit.get("status", 200))

    if (header := responseInit.get("headers", None)) is not None and len(header):
        for k, v in header.items():
            resp.send_header(k, v)

    resp.end_headers()

    resp.wfile.write(bodyInit.encode())


def pathHandler(request: Request):
    method = request["method"]
    req = request["request"]

    print(f"GET: {req.path}")

    path = req.path
    reqIp = req.client_address[0]

    match path:
        case "/current_status":
            if not session.LOGIN_SESSION.isValid(reqIp):
                buildResponse(req, "", {"status": 403})
                return

            buildResponse(req, json.dumps(api.currentStatusHandler()), {"status": 200})

        case "/scan_network":
            if not session.LOGIN_SESSION.isValid(reqIp):
                buildResponse(req, "", {"status": 403})
                return

            buildResponse(req, json.dumps(api.scanNetworkHandler()), {"status": 200})

        case "/get_wpa_config":
            if not session.LOGIN_SESSION.isValid(reqIp):
                buildResponse(req, "", {"status": 403})
                return

            with open("database/db.json") as f:
                buildResponse(req, f.read(), {"status": 200})

        case "/apply_wpa_config":
            if not session.LOGIN_SESSION.isValid(reqIp):
                buildResponse(req, "", {"status": 403})
                return

            if api.applyWpaSettingHandler():
                buildResponse(req, "", {"status": 200})
            else:
                buildResponse(req, "", {"status": 400})

        case "/save_wpa_config":
            if not session.LOGIN_SESSION.isValid(reqIp):
                buildResponse(req, "", {"status": 403})
                return

            if method != "POST":
                buildResponse(req, "", {"status": 405})
                return

            if req.headers.get("Content-Type", "") != "application/json":
                buildResponse(req, "", {"status": 400})
                return

            contentLength = int(req.headers.get("Content-Length", 0))

            if contentLength == 0:
                buildResponse(req, "", {"status": 403})
                return

            try:
                with open("database/db.json", "w") as f:
                    f.write(
                        json.dumps(
                            json.loads(req.rfile.read(contentLength).decode("utf-8")),
                            indent=4,
                            ensure_ascii=False,
                        )
                    )
            except json.decoder.JSONDecodeError as e:
                print(e)
                buildResponse(req, "", {"status": 400})
                return

            buildResponse(req, "", {"status": 200})

        case "/select_network":
            if not session.LOGIN_SESSION.isValid(reqIp):
                buildResponse(req, "", {"status": 403})
                return

            if method != "POST":
                buildResponse(req, "", {"status": 405})
                return

            contentLength = int(req.headers.get("Content-Length", 0))

            if contentLength == 0:
                buildResponse(req, "", {"status": 403})
                return

            clientPayload: dict[str, str] = json.loads(req.rfile.read(contentLength).decode("utf-8"))
            selectId = clientPayload.get("net_id", None)

            if selectId is None or not selectId.isdigit():
                buildResponse(req, "", {"status": 400})
                return

            with open("database/choose.json", "w") as f:
                f.write(json.dumps(clientPayload, indent=4, ensure_ascii=False))

            if api.selectNetworkHandler(int(selectId)):
                buildResponse(req, "", {"status": 200})
            else:
                buildResponse(req, "", {"status": 400})

        case "/get_select_network":
            if not session.LOGIN_SESSION.isValid(reqIp):
                buildResponse(req, "", {"status": 403})
                return

            with open("database/choose.json") as f:
                buildResponse(req, f.read(), {"status": 200})

        # Session Control
        case "/login":
            if method != "POST":
                buildResponse(req, "", {"status": 405})
                return

            contentLength = int(req.headers.get("Content-Length", 0))

            if contentLength == 0:
                buildResponse(req, "", {"status": 403})
                return

            if not api.loginHandler(reqIp, req.rfile.read(contentLength).decode("utf-8")):
                buildResponse(req, "", {"status": 403})
            else:
                buildResponse(req, "", {"status": 202})

        case "/logout":
            session.LOGIN_SESSION.removeSession(reqIp)
            buildResponse(req, "", {"status": 202})

        case "/":
            respContent: str = ""

            if not session.LOGIN_SESSION.isValid(reqIp):
                with open("website/login.html") as f:
                    respContent = f.read()
            else:
                session.LOGIN_SESSION.updateSession(reqIp)
                with open("website/index.html") as f:
                    respContent = f.read()

            buildResponse(req, respContent, {"status": 200, "headers": {"Content-type": "text/html"}})

        case _:
            buildResponse(req, "", {"status": 404})


class EntryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pathHandler({"method": "GET", "request": self})

    def do_POST(self):
        pathHandler({"method": "POST", "request": self})


_SERVER = HTTPServer(("192.168.5.1", 9999), EntryHandler)


def launch_server():
    print("server launched")
    _SERVER.serve_forever()
    _SERVER.server_close()

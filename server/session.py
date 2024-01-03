from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ConnectSession:
    pool: dict[str, str]

    def isValid(self, ip: str):
        sessionLastAccessTime = self.pool.get(ip)
        if sessionLastAccessTime is None:
            return False

        interval = datetime.now() - datetime.fromtimestamp(float(sessionLastAccessTime))

        if interval.seconds < 1800:
            return True

        return False

    def updateSession(self, ip: str):
        if self.pool.get(ip) is None:
            self.pool[ip] = str(datetime.now().timestamp())
        else:
            self.pool.setdefault(ip, str(datetime.now().timestamp()))

    def removeSession(self, ip: str):
        self.pool.pop(ip, None)


LOGIN_SESSION = ConnectSession({})

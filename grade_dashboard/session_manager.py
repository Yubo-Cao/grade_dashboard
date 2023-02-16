import aiohttp

from .exception import LoginFailedException
from .constants import DASHBOARD_URL


class SessionManager:
    def __init__(self):
        self.sessions = {}

    async def get_session(self, username: str, password: str) -> aiohttp.ClientSession:
        session_key = f"{username}:{password}"
        if session_key in self.sessions:
            return self.sessions[session_key]

        cookie_jar = aiohttp.CookieJar(unsafe=True)
        session = aiohttp.ClientSession(
            cookie_jar=cookie_jar,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            },
        )
        async with session.post(
            DASHBOARD_URL / "pkmslogin.form",
            data={
                "forgotpass": "p0/IZ7_3AM0I440J8GF30AIL6LB453082=CZ6_3AM0I440J8GF30AIL6LB4530G6=LA0=OC=Eaction!ResetPasswd==/#Z7_3AM0I440J8GF30AIL6LB453082",
                "login-form-type": "pwd",
                "username": username,
                "password": password,
            },
        ) as r:
            if not r.ok:
                await session.close()
                raise LoginFailedException("Failed to login", r)

        self.sessions[session_key] = session
        return session

    async def cleanup_session(self, username: str, password: str):
        session_key = f"{username}:{password}"
        if session_key in self.sessions:
            await self.sessions[session_key].close()
            del self.sessions[session_key]

    async def cleanup(self):
        for session in self.sessions.values():
            await session.close()
        self.sessions = {}


manager = SessionManager()

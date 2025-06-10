import secrets
import uuid

from miro_api.miro_api_wrapper import Miro
from miro_api.storage import InMemoryStorage
from pydantic import BaseModel, Field
from tinydb import Query, TinyDB

from package.util import get_logger, get_settings

settings = get_settings()
logger = get_logger()

CSRF_TOKEN_LENGTH = 64


class Session(BaseModel):
    user_id: str = Field(default="")
    session_id: str = Field(default="")
    csrf_token: str = Field(default="")
    token: str = Field(default="")

    model_config = {"arbitrary_types_allowed": True}


class SessionManager:
    """セッション管理クラス."""

    def __init__(self):
        self.db = TinyDB("./db/session.json")

    def get_session_by_user_id(self, user_id: str) -> Session:
        """指定したuser_idのセッションを取得."""
        query = Query()
        sessions = self.db.search(query["user_id"] == user_id)
        session = sessions[0] if sessions else None
        if not session:
            return Session(
                user_id=user_id,
                session_id=uuid.uuid4(),
                csrf_token="",
                token="",
            )
        return Session(
            user_id=session["user_id"],
            session_id=session["session_id"],
            csrf_token=session["csrf_token"],
            token=session["token"],
        )

    def get_session_by_csrf_token(self, csrf_token: str) -> Session | None:
        """指定したcsrf_tokenのセッションを取得."""
        query = Query()
        sessions = self.db.search(query["csrf_token"] == csrf_token)
        session = sessions[0] if sessions else None
        if not session:
            return None
        return Session(
            user_id=session["user_id"],
            session_id=session["session_id"],
            csrf_token=session["csrf_token"],
            token=session["token"],
        )

    def get_miro_client(self, user_id: str) -> Miro | None:
        """指定したuser_idのMiroクライアントを取得."""
        session = self.get_session_by_user_id(user_id)
        return Miro(
            client_id=settings.MIRO_CLIENT_ID,
            client_secret=settings.MIRO_CLIENT_SECRET,
            redirect_url=settings.MIRO_REDIRECT_URI,
            storage=InMemoryStorage().set(session["token"]),
        )

    def get_auth_status(self, user_id: str) -> bool:
        """指定したuser_idの認証状態を取得."""
        # session = self.get_session_by_user_id(user_id)
        miro = self.get_miro_client(user_id)
        return miro.is_authorized

    def get_auth_url(self, user_id: str) -> str:
        """指定したuser_idの認証URLを取得."""
        query = Query()

        # CSRFトークンを生成してセッションに保存
        csrf_token = secrets.token_urlsafe(CSRF_TOKEN_LENGTH)[:CSRF_TOKEN_LENGTH]
        self.db.update({"csrf_token": csrf_token}, query["user_id"] == user_id)

        # CSRFトークンを含む認証URLを生成
        miro = self.get_miro_client(user_id)
        return miro.get_auth_url(state=csrf_token)

    def get_redirect_url(
        self, code: str = "", state: str = "", team_id: str = ""
    ) -> str:
        """指定したuser_idのリダイレクトURLを取得."""
        query = Query()
        session = self.get_session_by_csrf_token(state)
        if not session:
            miro = Miro(
                client_id=settings.MIRO_CLIENT_ID,
                client_secret=settings.MIRO_CLIENT_SECRET,
                redirect_url=settings.MIRO_REDIRECT_URI,
                storage=InMemoryStorage(),
            )
            token = miro.exchange_code_for_access_token(code)
            self.db.update({token: miro._storage.get()}, query["csrf_token"] == state)
            logger.info("Token: %s", token)
            return (
                "https://miro.com/app-install-completed"
                f"?client_id={settings.MIRO_CLIENT_ID}"
                f"&team_id={team_id}"
            )
        miro = self.get_miro_client(session.user_id)
        token = miro.exchange_code_for_access_token(code)
        return f"{settings.FRONTEND_URL}/api/auth/2-signed"

    def clear_session(self, user_id: str) -> None:
        """指定したuser_idのセッションを削除."""
        query = Query()
        self.db.update({"csrf_token": "", "token": ""}, query["user_id"] == user_id)

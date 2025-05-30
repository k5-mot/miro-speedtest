import secrets
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from miro_api.miro_api_wrapper import Miro
from miro_api.storage import InMemoryStorage, Storage
from pydantic import BaseModel, Field

from package.util import get_logger, get_settings

settings = get_settings()
logger = get_logger()
router = APIRouter()


class Session(BaseModel):
    user_id: str = Field(default="")
    session_id: str = Field(default="")
    csrf_token: str = Field(default="")
    storage: Storage = Field(default=InMemoryStorage())

    model_config = {"arbitrary_types_allowed": True}


# セッション管理用のdict (本番はDB等を推奨)
sessions: list[Session] = []

CSRF_TOKEN_LENGTH = 32


def find_session_by_csrf_token(csrf_token: str) -> Session | None:
    """指定したCSRFトークンに一致するセッションを返す."""
    return next((s for s in sessions if s.csrf_token == csrf_token), None)


def find_sessions_by_user_id(user_id: str) -> Session | None:
    """指定したuser_idのセッションをすべて返すのだ。なければNoneを返すのだ."""
    return next((s for s in sessions if s.user_id == user_id), None)


def get_miro_client_by_user_id(user_id: str) -> Miro | None:
    """指定したuser_idのセッションを取得するのだ。なければNoneを返すのだ."""
    session = find_sessions_by_user_id(user_id)
    if not session:
        return None
    return Miro(
        client_id=settings.MIRO_CLIENT_ID,
        client_secret=settings.MIRO_CLIENT_SECRET,
        redirect_url=settings.MIRO_REDIRECT_URI,
        storage=session.storage,
    )


def clear_csrf_by_user_id(user_id: str) -> None:
    """指定したuser_idのセッション(state)をsessionsから削除する."""
    for session in sessions:
        if session.user_id == user_id:
            session.csrf_token = ""


def upsert_session(session: Session) -> Session:
    """sessionsにsessionを追加する."""
    for s in sessions:
        # すでに存在するセッションの場合は更新
        if s.user_id == session.user_id:
            s.session_id = session.session_id
            s.csrf_token = session.csrf_token
            s.storage = session.storage
    sessions.append(session)
    return session


@router.get("/status")
def status(user_id: Annotated[str, Query(...)] = "") -> dict:
    """セッションの状態を取得するのだ."""
    session = find_sessions_by_user_id(user_id)
    if not session:
        session = Session(
            user_id=user_id,
            session_id="",
            csrf_token="",
            storage=InMemoryStorage(),
        )
        upsert_session(session)
    else:
        session = Session(
            user_id=user_id,
            session_id=session.session_id,
            csrf_token=session.csrf_token,
            storage=session.storage,
        )
        upsert_session(session)

    miro = Miro(
        client_id=settings.MIRO_CLIENT_ID,
        client_secret=settings.MIRO_CLIENT_SECRET,
        redirect_url=settings.MIRO_REDIRECT_URI,
        storage=session.storage,
    )
    logger.info(
        """
        [OAUTH2] /status: userId = %s
        [OAUTH2] /status: status = %s
        [OAUTH2] /status: session_id = %s
        [OAUTH2] /status: csrf_token = %s
        """,
        user_id,
        miro.is_authorized,
        session.session_id,
        session.csrf_token,
    )
    # logger.info("[OAUTH2] /status: status = %s", miro.is_authorized)
    # logger.info("[OAUTH2] /status: session_id = %s", session.session_id)
    # logger.info("[OAUTH2] /status: csrf_token = %s", session.csrf_token)
    return {
        "user_id": session.user_id,
        "status": miro.is_authorized,
        "session_id": session.session_id,
        "csrf_token": session.csrf_token,
    }


@router.api_route("/authorize", methods=["GET", "POST"])
def login(response: Response, user_id: Annotated[str, Query(...)] = "") -> JSONResponse:
    """セッションを確立し、Miro OAuth画面の認証URLを返すのだ."""
    session = find_sessions_by_user_id(user_id)
    session = upsert_session(
        Session(
            user_id=user_id,
            session_id=str(uuid.uuid4()),
            csrf_token=secrets.token_urlsafe(CSRF_TOKEN_LENGTH),
            storage=InMemoryStorage(),
        )
    )
    miro = Miro(
        client_id=settings.MIRO_CLIENT_ID,
        client_secret=settings.MIRO_CLIENT_SECRET,
        redirect_url=settings.MIRO_REDIRECT_URI,
        storage=session.storage,
    )

    auth_url = f"{miro.auth_url}&state={session.csrf_token}"
    logger.info(
        """
        [OAUTH2] /authorize: user_id = %s
        [OAUTH2] /authorize: session_id = %s
        [OAUTH2] /authorize: csrf_token = %s
        [OAUTH2] /authorize: auth_url = %s
        """,
        user_id,
        session.session_id,
        session.csrf_token,
        auth_url,
    )
    # logger.info("[OAUTH2] /authorize: user_id = %s", user_id)
    # logger.info("[OAUTH2] /authorize: session_id = %s", session.session_id)
    # logger.info("[OAUTH2] /authorize: csrf_token = %s", session.csrf_token)
    # logger.info("[OAUTH2] /authorize: auth_url = %s", auth_url)
    response.set_cookie(
        key="session_id", value=session.session_id, httponly=True, samesite="lax"
    )
    return JSONResponse({"url": auth_url})


@router.api_route("/redirect", methods=["GET", "POST"])
def callback(
    code: str = "",
    state: str = "",
    client_id: str = "",
    team_id: str = "",
) -> RedirectResponse:
    """Miroからのリダイレクトを受けてアクセストークンを取得する."""
    logger.info(
        "[OAUTH2] /redirect: callback received",
        extra={
            "code": code,
            "state": state,
            "client_id": client_id,
            "team_id": team_id,
        },
    )
    session = find_session_by_csrf_token(state)
    if not session:
        logger.error(
            "[OAUTH2] /redirect: CSRF token mismatch or session not found",
            extra={"state": state, "sessions": [s.csrf_token for s in sessions]},
        )
        return RedirectResponse("http://localhost:3000/signin?error=csrf")
    logger.info(
        "[OAUTH2] /redirect: CSRF token matched",
        extra={"user_id": session.user_id, "csrf_token": session.csrf_token},
    )
    miro = Miro(
        client_id=settings.MIRO_CLIENT_ID,
        client_secret=settings.MIRO_CLIENT_SECRET,
        redirect_url=settings.MIRO_REDIRECT_URI,
        storage=session.storage,
    )
    access_token = miro.exchange_code_for_access_token(code)
    # logger.info("Access token received", extra={"access_token": access_token})
    # clear_csrf_by_user_id(session.user_id)
    logger.info(
        """
        [OAUTH2] /redirect: team_id = %s
        [OAUTH2] /redirect: session_id = %s
        [OAUTH2] /redirect: csrf_token = %s
        [OAUTH2] /redirect: access_token = %s
        [OAUTH2] /redirect: client_id = %s
        """,
        team_id,
        session.session_id,
        session.csrf_token,
        access_token,
        settings.MIRO_CLIENT_ID,
    )
    # url = (
    #     "https://miro.com/app-install-completed"
    #     f"?client_id={settings.MIRO_CLIENT_ID}"
    #     f"&team_id={team_id}"
    # )
    url = "http://localhost:3000/auth/2-signed"
    return RedirectResponse(url)


@router.post("/refresh")
def logout(
    response: Response, user_id: Annotated[str, Query(...)] = ""
) -> JSONResponse:
    """セッションを削除してログアウトするのだ."""
    session = find_sessions_by_user_id(user_id)
    session.csrf_token = ""
    session.storage = InMemoryStorage()
    return JSONResponse({"message": "Logged out successfully"})

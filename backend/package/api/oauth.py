from typing import Annotated

from fastapi import APIRouter, Query, Response
from fastapi.responses import JSONResponse, RedirectResponse
from miro_api.miro_api_wrapper import Miro
from miro_api.storage import InMemoryStorage

# from pydantic import BaseModel, Field
from package.db.session import SessionManager
from package.util import get_logger, get_settings

settings = get_settings()
logger = get_logger()
router = APIRouter()


session_manager = SessionManager()


@router.get("/status")
def status(user_id: Annotated[str, Query(...)] = "") -> dict:
    """セッションの状態を取得."""
    session = session_manager.get_session_by_user_id(user_id)
    return {
        "user_id": session.user_id,
        "status": session_manager.get_auth_status(user_id),
        "session_id": session.session_id,
        "csrf_token": session.csrf_token,
    }


@router.api_route("/authorize", methods=["GET", "POST"])
def authorize(
    response: Response, user_id: Annotated[str, Query(...)] = ""
) -> JSONResponse:
    """セッションを確立し、Miro OAuth画面の認証URLを返す."""
    session = session_manager.get_session_by_user_id(user_id)
    auth_url = session_manager.get_auth_url(user_id)
    response.set_cookie(
        key="session_id", value=session.session_id, httponly=True, samesite="lax"
    )
    return JSONResponse({"url": auth_url})


@router.api_route("/redirect", methods=["GET", "POST"])
def redirect(
    code: str = "",
    state: str = "",
    team_id: str = "",
) -> RedirectResponse:
    """Miroからのリダイレクトを受けてアクセストークンを取得する."""
    session = session_manager.get_session_by_csrf_token(state)
    if not session:
        logger.error(
            "[OAUTH2] /redirect: CSRF token not found or session expired",
            extra={"state": state},
        )
        return RedirectResponse(f"{settings.FRONTEND_URL}/signin?error=csrf")
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
    session = session_manager.find_sessions_by_user_id(user_id)
    session.csrf_token = ""
    session.storage = InMemoryStorage()
    return JSONResponse({"message": "Logged out successfully"})

from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from package.common import get_logger, get_settings
from package.util.session import SessionManager

settings = get_settings()
logger = get_logger()
router = APIRouter()
session_manager = SessionManager()


class OAuthStatusResponse(BaseModel):
    user_id: str = Field(default="", description="User ID")
    status: bool = Field(default=False, description="Authorization status")
    session_id: str = Field(default="", description="Session ID")
    csrf_token: str = Field(default="", description="CSRF token")


@router.api_route("/status", methods=["GET", "POST"])
def status(user_id: Annotated[str, Query(...)] = "") -> OAuthStatusResponse:
    """ユーザーセッションの状態を取得."""
    # status = session_manager.refresh_auth(user_id)s
    status = session_manager.get_auth_status(user_id)
    session = session_manager.get_session(user_id)
    logger.info(
        "user_id: %s, status: %s, session_id: %s, csrf_token: %s",
        user_id,
        status,
        session.get("session_id", ""),
        session.get("csrf_token", ""),
    )
    return OAuthStatusResponse(
        user_id=user_id,
        status=status,
        session_id=session.get("session_id", ""),
        csrf_token=session.get("csrf_token", ""),
    )


class OAuthResponse(BaseModel):
    auth_url: str = Field(..., description="Authorization URL")


@router.api_route("/authorize", methods=["GET", "POST"])
def authorize(
    user_id: Annotated[str, Query(...)] = "",
    team_id: Annotated[str, Query(...)] = "",
) -> OAuthResponse:
    """ユーザーセッションの認証・認可リクエストURLを取得."""
    auth_url = session_manager.get_auth_url(user_id=user_id, team_id=team_id)
    logger.info(
        "user_id: %s, auth_url: %s",
        user_id,
        auth_url,
    )
    return OAuthResponse(auth_url=auth_url)


@router.api_route("/redirect", methods=["GET", "POST"])
def redirect(
    code: Annotated[str, Query(...)] = "",
    state: Annotated[str, Query(...)] = "",
    team_id: Annotated[str, Query(...)] = "",
) -> RedirectResponse:
    """ユーザーセッションの認証・認可後のページにリダイレクト."""
    redirect_url = session_manager.get_redirect_url(
        code=code,
        state=state,
        team_id=team_id,
    )
    logger.info(
        "code: %s, state: %s, team_id: %s, redirect_url: %s",
        code,
        state,
        team_id,
        redirect_url,
    )
    return RedirectResponse(redirect_url)


class OAuthRevokeResponse(BaseModel):
    status: bool = Field(default=False, description="Revoke status")


@router.api_route("/revoke", methods=["GET", "POST"])
def revoke(
    user_id: Annotated[str, Query(...)] = "",
) -> OAuthRevokeResponse:
    """ユーザーセッションの認証・認可を削除."""
    status = session_manager.revoke_auth(user_id)
    logger.info(
        "user_id: %s, revoke_status: %s",
        user_id,
        status,
    )
    return OAuthRevokeResponse(status=status)


class OAuthRefreshResponse(BaseModel):
    status: bool = Field(default=False, description="Refresh status")


@router.api_route("/refresh", methods=["GET", "POST"])
def refresh(
    user_id: Annotated[str, Query(...)] = "",
) -> OAuthRefreshResponse:
    """ユーザーセッションの認証・認可を更新."""
    status = session_manager.refresh_auth(user_id)
    logger.info(
        "user_id: %s, refresh_status: %s",
        user_id,
        status,
    )
    return OAuthRefreshResponse(status=status)

from miro_api.miro_api_wrapper import Miro
from miro_api.storage import InMemoryStorage

from package.common.logger import get_logger
from package.common.settings import get_settings
from package.db.sqlite_storage import SQLiteStorage

settings = get_settings()
logger = get_logger()


class SessionManager:
    """ユーザーセッション管理クラス."""

    # https://developers.miro.com/docs/getting-started-with-oauth
    # https://developers.miro.com/docs/enable_api_authentication_from_sdk_authorization

    def get_session(self, user_id: str) -> dict[str, str]:
        """指定したuser_idのユーザーセッション情報を取得."""
        storage = self.get_storage(user_id=user_id)
        session = storage.get_session()
        return {
            "user_id": user_id,
            "session_id": session.session_id,
            "csrf_token": session.csrf_token,
        }

    def get_storage(self, user_id: str) -> SQLiteStorage:
        """指定したuser_idのStorageを取得."""
        return SQLiteStorage(user_id=user_id)

    def get_miro_client(self, user_id: str) -> Miro:
        """指定したuser_idのMiroクライアントを取得."""
        return Miro(
            client_id=settings.MIRO_CLIENT_ID,
            client_secret=settings.MIRO_CLIENT_SECRET,
            redirect_url=settings.MIRO_REDIRECT_URI,
            storage=self.get_storage(user_id=user_id),
        )

    def get_auth_status(self, user_id: str) -> bool:
        """ユーザーセッションの認証状態を取得."""
        miro = self.get_miro_client(user_id=user_id)
        return miro.is_authorized

    def get_auth_url(self, user_id: str, team_id: str | None) -> str:
        """ユーザーセッションの認証・認可リクエストURLを取得."""
        # https://developers.miro.com/reference/create-authorization-request-link
        # https://developers.miro.com/reference/request-user-for-authorization

        # csrf_tokenを生成.
        storage = self.get_storage(user_id=user_id)
        csrf_token = storage.generate_csrf_token()

        # 認証・認可リクエストURLを取得.
        miro = self.get_miro_client(user_id=user_id)
        return miro.get_auth_url(state=csrf_token, team_id=team_id)

    def get_redirect_url(
        self,
        code: str = "",
        state: str = "",
        team_id: str = "",
    ) -> str:
        """認証・認可後のリダイレクトURLを取得."""
        # https://developers.miro.com/reference/exchange-authorization-code-with-access-token
        # https://developers.miro.com/reference/use-access-token-for-rest-api-requests

        # アプリインストールの認証・認可フロー.
        if not state:
            # 1. 認可サーバからauthorization_codeを受け取る.
            # 2. 認可サーバへauthorization_codeを送信する.
            # 3. 認可サーバからaccess_token/refresh_token/expires_inを受信する.
            miro = Miro(
                client_id=settings.MIRO_CLIENT_ID,
                client_secret=settings.MIRO_CLIENT_SECRET,
                redirect_url=settings.MIRO_REDIRECT_URI,
                storage=InMemoryStorage(),  # 一時的なストレージを使用.
                # アプリインストールの認証・認可フローでは、ユーザーIDは不要.
            )
            logger.info("Installing Miro app with code: %s", code)
            miro.exchange_code_for_access_token(code)
            return (
                # MiroのダッシュボードURL.
                "https://miro.com/app-install-completed"
                f"?client_id={settings.MIRO_CLIENT_ID}"
                f"&team_id={team_id}"
            )

        # ユーザごとの認証・認可フロー.
        # 0. state(=csrf_token)からuser_idを取得.
        user_id = SQLiteStorage.get_user_id(csrf_token=state)
        miro = self.get_miro_client(user_id=user_id)
        miro.exchange_code_for_access_token(code)
        return (
            # 認証・認可後のアプリURL.
            f"{settings.FRONTEND_URL}/auth/2-signed"
        )

    def revoke_auth(self, user_id: str) -> bool:
        """ユーザーセッションの認証情報を無効化."""
        storage = self.get_storage(user_id=user_id)
        # miro = self.get_miro_client(user_id=user_id)
        # miro.revoke_token()
        return storage.revoke_auth()

    def refresh_auth(self, user_id: str) -> bool:
        """ユーザーセッションの認証情報を更新."""
        miro = self.get_miro_client(user_id=user_id)
        try:
            token = miro.access_token
            logger.info("Refreshed auth for user %s: %s", user_id, token)
        except Exception as e:
            logger.exception("Unexpected error %s: %s", user_id, e)
            return False
        return True

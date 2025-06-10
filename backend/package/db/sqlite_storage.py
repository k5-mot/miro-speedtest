import datetime
import secrets
import sqlite3
import uuid

from miro_api.storage import State, Storage
from pydantic import BaseModel, Field

from package.common.logger import get_logger

SQLITE_PATH = "./db/user_sessions.sqlite3"
logger = get_logger()


class UserSession(BaseModel):
    """ユーザーセッション情報を表すモデル."""

    user_id: str = Field(default="")
    session_id: str = Field(default="")
    csrf_token: str = Field(default="")
    access_token: str = Field(default="")
    refresh_token: str | None = Field(default=None)
    token_expires_at: datetime.datetime | None = Field(default=None)

    model_config = {"arbitrary_types_allowed": True}


class SQLiteStorage(Storage):
    """SQLiteベースのStorage実装."""

    def __init__(
        self,
        user_id: str,
    ) -> None:
        """SQLiteStorageの初期化."""
        self.user_id = user_id
        self._init_db()
        self._init_user()

    def _init_db(self) -> None:
        """データベースとテーブルを初期化."""
        conn = sqlite3.connect(SQLITE_PATH)
        try:
            # データベースとテーブルが存在しない場合は作成.
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    user_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    csrf_token TEXT,
                    access_token TEXT,
                    refresh_token TEXT,
                    token_expires_at TEXT
                )
                """,
                (),
            )
            conn.commit()
        finally:
            conn.close()

    def _init_user(self) -> None:
        """ユーザーセッション情報を初期化."""
        record = self.get_session()

        # 指定されたuser_idのユーザーセッション情報が存在しない場合、
        # 未認証・非認可のユーザーセッションを作成.
        if not record:
            self._create_session(
                State(
                    access_token="",
                    refresh_token=None,
                    token_expires_at=None,
                ),
            )

    def get_session(self) -> UserSession | None:
        """指定されたuser_idのユーザーセッション情報を取得."""
        db_client = sqlite3.connect(SQLITE_PATH)
        try:
            # 指定されたuser_idのユーザーセッション情報を取得.
            cursor = db_client.execute(
                """
                SELECT
                    user_id,
                    session_id,
                    csrf_token,
                    access_token,
                    refresh_token,
                    token_expires_at
                FROM user_sessions
                WHERE user_id = ?
                """,
                (self.user_id,),
            )
            record = cursor.fetchone()

            # レコードが存在しない場合、空の辞書を返す.
            if not record:
                return None
            # レコードが存在する場合、ユーザーセッション情報をUserSession型で返す.
            return UserSession(
                user_id=str(record[0]),
                session_id=str(record[1]),
                csrf_token=str(record[2]),
                access_token=str(record[3]),
                refresh_token=str(record[4]) if record[4] else None,
                # ISO形式文字列をdatetime型に変換.
                token_expires_at=(
                    (record[5] and datetime.datetime.fromisoformat(record[5])) or None
                ),
            )
        except sqlite3.Error as e:
            logger.log(f"SQLite error: {e}")
            return None
        finally:
            db_client.close()

    def get(self) -> State | None:
        """ユーザーセッション情報を取得."""
        # レコードが存在しない場合、Noneを返す.
        record = self.get_session()
        if not record:
            return None

        return State(
            access_token=record.access_token or "",
            refresh_token=record.refresh_token or None,
            token_expires_at=record.token_expires_at or None,
        )

    def _create_session(self, state: State) -> None:
        """ユーザーセッションを新規作成."""
        conn = sqlite3.connect(SQLITE_PATH)
        try:
            conn.execute(
                """
                INSERT INTO user_sessions (
                    user_id,
                    session_id,
                    csrf_token,
                    access_token,
                    refresh_token,
                    token_expires_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    self.user_id,
                    str(uuid.uuid4()),
                    "",
                    state.access_token,
                    state.refresh_token or "",
                    (
                        # datetime型をISO形式文字列に変換.
                        (state.token_expires_at and state.token_expires_at.isoformat())
                        or ""
                    ),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _update_session(self, state: State) -> None:
        """ユーザーセッションを更新."""
        conn = sqlite3.connect(SQLITE_PATH)
        try:
            conn.execute(
                """
                UPDATE user_sessions
                SET
                    access_token = ?,
                    refresh_token = ?,
                    token_expires_at = ?
                WHERE user_id = ?
                """,
                (
                    state.access_token,
                    state.refresh_token or "",
                    (
                        # datetime型をISO形式文字列に変換.
                        (state.token_expires_at and state.token_expires_at.isoformat())
                        or ""
                    ),
                    self.user_id,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def set(self, state: State) -> None:
        """ユーザーのセッション状態を保存."""
        # 指定されたuser_idのユーザーセッション情報を取得.
        record = self.get_session()

        # レコードが存在しない場合、新規作成.
        if not record:
            self._create_session(state)
            return

        # レコードが存在する場合、更新.
        self._update_session(state)
        return

    def generate_csrf_token(self) -> str:
        """csrf_tokenを生成."""
        # csrf_tokenを生成.
        csrf_token_length = 64
        csrf_token = secrets.token_urlsafe(csrf_token_length)[:csrf_token_length]

        # csrf_tokenを保存.
        conn = sqlite3.connect(SQLITE_PATH)
        try:
            conn.execute(
                """
                UPDATE user_sessions
                SET csrf_token = ?
                WHERE user_id = ?
                """,
                (
                    csrf_token,
                    self.user_id,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return csrf_token

    @staticmethod
    def get_user_id(csrf_token: str) -> str | None:
        """csrf_tokenからuser_idを取得."""
        db_client = sqlite3.connect(SQLITE_PATH)
        try:
            # 指定されたcsrf_tokenのuser_idを取得.
            cursor = db_client.execute(
                """
                SELECT user_id
                FROM user_sessions
                WHERE csrf_token = ?
                """,
                (csrf_token,),
            )
            record = cursor.fetchone()

            # レコードが存在しない場合、Noneを返す.
            if not record:
                return None
            return record[0]
        finally:
            db_client.close()

    def revoke_auth(self) -> bool:
        """指定されたuser_idのユーザーセッション情報を削除."""
        # 指定されたuser_idのユーザーセッション情報が存在するか確認.
        session = self.get_session()
        if not session:
            return False

        # 指定されたuser_idの認証・認可情報を削除.
        self._update_session(
            State(
                access_token="",
                refresh_token=None,
                token_expires_at=None,
            ),
        )
        return True

import datetime
import secrets
import string
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter

# from miro_api.miro_api_wrapper import Miro
from miro_api.models.sticky_note_create_request import StickyNoteCreateRequest
from miro_api.models.tag_create_request import TagCreateRequest
from pydantic import BaseModel

from package.api.oauth import session_manager
from package.util import get_logger, get_settings

settings = get_settings()
logger = get_logger()
router = APIRouter()

START_X = 0
START_Y = 0
OFFSET_X = 200
OFFSET_Y = 200
NUM_X = 10
NUM_Y = 10
STICKY_COLORS = [
    "yellow",
    "green",
    "blue",
    "pink",
    "orange",
    "gray",
    "red",
    "violet",
    "light_yellow",
    "light_green",
    "dark_green",
    "cyan",
    "light_pink",
    "light_blue",
    "dark_blue",
    "black",
]


def get_random_letter() -> str:
    """ランダムな英字を取得する."""
    return secrets.choice(string.ascii_letters)


def get_random_color() -> str:
    """ランダムな色を取得する."""
    return secrets.choice(STICKY_COLORS)


class CreateRequest(BaseModel):
    """付箋作成リクエスト."""

    user_id: str
    board_id: str


class StickyNoteRequest(BaseModel):
    """付箋作成リクエスト."""

    user_id: str
    board_id: str
    tag_id: str
    item_ids: list[str]


class CreateResponse(BaseModel):
    """付箋作成レスポンス."""

    tag_id: str
    item_ids: list[str] = []


@router.post("/post")
def create_sticky_notes(request: CreateRequest) -> CreateResponse:
    """付箋を作成する."""
    miro = session_manager.get_miro_client(request.user_id)
    nowtime = datetime.datetime.now(tz=datetime.UTC)
    nowtime = nowtime.strftime("%Y%m%d%H%M%S")
    tag = miro.api.create_tag(
        board_id=request.board_id,
        tag_create_request=TagCreateRequest(title=f"speedtest-{nowtime}"),
    )

    def create_sticky_note(i: int, j: int) -> str:
        logger.info("create_sticky_note: %s, %s", i, j)
        sticky_note = miro.api.create_sticky_note_item(
            request.board_id,
            StickyNoteCreateRequest(
                data={
                    "content": get_random_letter(),
                },
                style={
                    "fillColor": get_random_color(),
                },
                position={
                    "x": START_X + j * OFFSET_X,
                    "y": START_Y + i * OFFSET_Y,
                },
            ),
        )
        miro.api.attach_tag_to_item(
            board_id_platform_tags=request.board_id,
            item_id=sticky_note.id,
            tag_id=tag.id,
        )
        return sticky_note.id

    with ThreadPoolExecutor() as executor:
        notes = executor.map(
            lambda pos: create_sticky_note(*pos),
            [(i, j) for i in range(NUM_Y) for j in range(NUM_X)],
        )

    return CreateResponse(tag_id=tag.id, item_ids=notes)


@router.get("/get")
def get_sticky_notes(request: StickyNoteRequest) -> CreateResponse:
    """付箋を取得."""
    miro = session_manager.get_miro_client(request.user_id)
    nowtime = datetime.datetime.now(tz=datetime.UTC)
    nowtime = nowtime.strftime("%Y%m%d%H%M%S")
    # tag = miro.api.create_tag(
    #     board_id=request.board_id,
    #     tag_create_request=TagCreateRequest(title=f"speedtest-{nowtime}"),
    # )

    def create_sticky_note(i: int, j: int) -> str:
        logger.info("create_sticky_note: %s, %s", i, j)
        sticky_note = miro.api.get_sticky_note_item(
            request.board_id, StickyNoteRequest()
        )
        sticky_note = miro.api.create_sticky_note_item(
            request.board_id,
        )
        # miro.api.attach_tag_to_item(
        #     board_id_platform_tags=request.board_id,
        #     item_id=sticky_note.id,
        #     tag_id=tag.id,
        # )
        logger.info(sticky_note.data)
        return sticky_note.id

    with ThreadPoolExecutor() as executor:
        notes = executor.map(
            lambda pos: create_sticky_note(*pos),
            [(i, j) for i in range(NUM_Y) for j in range(NUM_X)],
        )

    return CreateResponse(tag_id=request.tag_id, item_ids=notes)

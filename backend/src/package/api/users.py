from fastapi import APIRouter

router = APIRouter()


@router.get("/users")
def get_users() -> dict:
    """Get a list of users."""
    return {"message": "Hello, World!"}

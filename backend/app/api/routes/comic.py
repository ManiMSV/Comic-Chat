"""Comic render endpoints (T014, FR-008).

Stateless: ``POST /comic/render`` turns a transient conversation into a typed
``ComicResponse`` and ``GET /comic/demos`` lists the fixed demo dialogues. Both
endpoints sit behind the existing auth. Unknown ``speaker_id`` values surface as
HTTP 422 via the composer's ``ValueError``.
"""

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser
from app.schemas.comic import ComicRequest, ComicResponse, DemosResponse
from app.services import demos
from app.services.composer import compose

router = APIRouter(prefix="/comic", tags=["comic"])


@router.post("/render", response_model=ComicResponse)
def render_comic(payload: ComicRequest, _: CurrentUser) -> ComicResponse:
    """
    Render a conversation into a typed comic instruction (deterministic, SC-002).
    """
    try:
        comic = compose(payload.messages)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ComicResponse(comic=comic)


@router.get("/demos", response_model=DemosResponse)
def list_demos(_: CurrentUser) -> DemosResponse:
    """
    List the three ready-made demo dialogues (FR-011).
    """
    return DemosResponse(demos=list(demos.DEMOS))

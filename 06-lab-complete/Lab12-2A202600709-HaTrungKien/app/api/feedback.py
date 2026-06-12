from __future__ import annotations

from fastapi import APIRouter, Request, Response, status

from app.models.request import FeedbackRequest
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/api", tags=["feedback"])


def _get_service(request: Request) -> FeedbackService:
    return request.app.state.feedback_service


@router.post("/feedback", status_code=status.HTTP_204_NO_CONTENT)
def submit_feedback(request: Request, payload: FeedbackRequest) -> Response:
    service = _get_service(request)
    service.log_feedback(payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


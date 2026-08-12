from fastapi import APIRouter, HTTPException, status
from app.models.audit_models import AuditRequest, AuditResponse, AuditPlannerResponse, AuditRetrievalResponse
from app.services.audit_graph import audit_graph_service
from app.utils.logger import logger

router = APIRouter()


@router.post("/audit", response_model=AuditResponse, status_code=status.HTTP_200_OK)
def run_compliance_audit(request: AuditRequest):
    """Start the compliance audit workflow using LangGraph orchestration."""
    logger.info(f"API Audit request received for question: '{request.question}'")

    question_stripped = request.question.strip()
    if not question_stripped:
        logger.error("Audit request failed validation: empty question.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty or whitespace."
        )

    try:
        # Execute the compiled StateGraph
        final_state = audit_graph_service.run_audit(question_stripped)

        # Handle errors recorded in state
        if final_state.get("errors"):
            logger.error(f"Audit workflow recorded errors: {final_state['errors']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Audit workflow encountered errors: {', '.join(final_state['errors'])}"
            )

        # Ensure planner and retrieval outputs are present
        retrieval_result = final_state.get("retrieval_result")
        if not retrieval_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Retrieve node failed to return a retrieval result."
            )

        # Construct structured response
        response = AuditResponse(
            question=question_stripped,
            planner=AuditPlannerResponse(
                audit_type=final_state.get("audit_type"),
                subject=final_state.get("subject"),
                regulation=final_state.get("regulation"),
                intent=final_state.get("intent", f"Evaluate compliance for {final_state.get('subject')}")
            ),
            retrieval=AuditRetrievalResponse(
                company_policy=retrieval_result.company_policy,
                regulations=retrieval_result.regulations,
                confidence=final_state.get("confidence"),
                confidence_level=final_state.get("confidence_level")
            )
        )
        return response

    except ValueError as ve:
        logger.error(f"Validation or user-input error in compliance audit: {ve}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Failed to process compliance audit query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance audit failed: {str(e)}"
        )

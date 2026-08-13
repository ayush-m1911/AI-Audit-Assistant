import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.schema import HumanReview
from app.models.audit_models import AuditRequest
from app.services.audit_graph import audit_graph_service
from app.utils.logger import logger

router = APIRouter()


@router.post("/audit", status_code=status.HTTP_200_OK)
def run_compliance_audit(request: AuditRequest, db: Session = Depends(get_db)):
    """Start the compliance audit workflow using LangGraph orchestration."""
    logger.info(f"API Audit request received for question: '{request.question}'")

    question_stripped = request.question.strip()
    if not question_stripped:
        logger.error("Audit request failed validation: empty question.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty or whitespace."
        )

    # Generate session/thread and review identifiers
    thread_id = str(uuid.uuid4())
    review_id = str(uuid.uuid4())

    try:
        # Execute the compiled StateGraph
        final_state = audit_graph_service.run_audit(question_stripped, thread_id)

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

        # Check if confidence gate triggered human review request (Requirement 19)
        if final_state.get("review_required"):
            logger.info(f"Gate Triggered: human review required for review_id={review_id}. Saving request...")

            reasons_list = final_state.get("review_reasons", [])
            ret_conf = final_state.get("retrieval_confidence") or 0.0
            comp_conf = final_state.get("compliance_confidence") or 0.0
            r_level = final_state.get("risk_analysis").overall_risk_level if final_state.get("risk_analysis") else "low"
            r_score = final_state.get("risk_analysis").overall_risk_score if final_state.get("risk_analysis") else 0

            # Persist review metadata in database (Requirement 17 & 21)
            db_review = HumanReview(
                review_id=review_id,
                thread_id=thread_id,
                question=question_stripped,
                status="pending",
                reasons=",".join(reasons_list),
                retrieval_confidence=ret_conf,
                compliance_confidence=comp_conf,
                risk_level=r_level,
                risk_score=r_score
            )
            db.add(db_review)
            db.commit()

            return {
                "status": "review_required",
                "review_id": review_id,
                "thread_id": thread_id,
                "question": question_stripped,
                "reasons": reasons_list,
                "retrieval_confidence": ret_conf,
                "compliance_confidence": comp_conf,
                "risk_level": r_level
            }

        # Otherwise return completed audit response (Requirement 20)
        return {
            "status": "completed",
            "question": question_stripped,
            "planner": {
                "audit_type": final_state.get("audit_type"),
                "subject": final_state.get("subject"),
                "regulation": final_state.get("regulation"),
                "intent": final_state.get("intent", f"Evaluate compliance for {final_state.get('subject')}")
            },
            "retrieval": {
                "company_policy": retrieval_result.company_policy,
                "regulations": retrieval_result.regulations,
                "confidence": final_state.get("retrieval_confidence") if final_state.get("retrieval_confidence") is not None else retrieval_result.confidence,
                "confidence_level": final_state.get("confidence_level")
            },
            "compliance": final_state.get("compliance_analysis"),
            "risk": final_state.get("risk_analysis"),
            "recommendations": final_state.get("recommendation_analysis")
        }

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


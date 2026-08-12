from typing import Dict, Any
from app.graph.workflow import audit_graph
from app.utils.logger import logger


class AuditGraphService:
    """Service to execute the compiled LangGraph compliance audit workflow."""

    def run_audit(self, question: str) -> Dict[str, Any]:
        """Execute the compliance audit workflow for a given question.

        Args:
            question (str): The compliance question.

        Returns:
            Dict[str, Any]: The final compiled state of the graph.
        """
        logger.info(f"Audit workflow started for question: '{question[:60]}...'")

        # Validate question
        if not question.strip():
            logger.error("Audit workflow failed validation: empty question.")
            raise ValueError("Question cannot be empty or whitespace.")

        # Initialize AuditState
        initial_state = {
            "question": question,
            "audit_type": None,
            "subject": None,
            "regulation": None,
            "intent": None,
            "retrieval_result": None,
            "confidence": None,
            "confidence_level": None,
            "errors": [],
            "compliance_analysis": None,
            "retrieval_confidence": None,
            "compliance_confidence": None,
            "compliance_findings": None,
            "risk_assessment": None,
            "recommendations": None,
            "review_status": None,
            "final_report": None
        }

        try:
            # Invoke LangGraph workflow
            final_state = audit_graph.invoke(initial_state)
            logger.info("Audit workflow completed successfully.")
            return final_state
        except Exception as e:
            logger.error(f"Audit workflow execution failed: {e}", exc_info=True)
            raise e


# Create singleton service instance
audit_graph_service = AuditGraphService()

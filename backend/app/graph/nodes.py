from typing import Dict, Any
from app.graph.state import AuditState
from app.agents.planner import PlannerAgent
from app.agents.compliance import ComplianceAgent
from app.services.retriever import retrieval_service
from app.utils.logger import logger

# Instantiate Agents
planner_agent = PlannerAgent()
compliance_agent = ComplianceAgent()


def planner_node(state: AuditState) -> Dict[str, Any]:
    """LangGraph node representing the planning and intent parsing stage.

    Uses PlannerAgent to parse user compliance query metadata.
    """
    logger.info("Planner node started")
    question = state.get("question", "")

    if not question.strip():
        err_msg = "Question cannot be empty."
        logger.error(f"Planner node error: {err_msg}")
        return {"errors": state.get("errors", []) + [err_msg]}

    try:
        planner_output = planner_agent.plan(question)
        logger.info("Planner node completed successfully")
        return {
            "audit_type": planner_output.audit_type,
            "subject": planner_output.subject,
            "regulation": planner_output.regulation,
            "intent": planner_output.intent,
        }
    except Exception as e:
        err_msg = f"Planner failure: {str(e)}"
        logger.error(err_msg, exc_info=True)
        raise ValueError(err_msg)


def retrieval_node(state: AuditState) -> Dict[str, Any]:
    """LangGraph node representing the evidence retrieval stage.

    Directly queries the existing RetrievalService for policies and regulations.
    """
    logger.info("Retrieval node started")
    question = state.get("question", "")

    if not question.strip():
        err_msg = "Question cannot be empty for retrieval."
        logger.error(f"Retrieval node error: {err_msg}")
        return {"errors": state.get("errors", []) + [err_msg]}

    try:
        # Directly call the internal RetrievalService (never an HTTP call)
        retrieval_result = retrieval_service.retrieve(question=question)

        logger.info("Retrieval node completed successfully")
        return {
            "retrieval_result": retrieval_result,
            "confidence": retrieval_result.confidence,
            "confidence_level": retrieval_result.confidence_level,
            "retrieval_confidence": retrieval_result.confidence,  # Store separately in state (Phase 4B)
        }
    except Exception as e:
        err_msg = f"Retrieval failure: {str(e)}"
        logger.error(err_msg, exc_info=True)
        raise ValueError(err_msg)


def compliance_node(state: AuditState) -> Dict[str, Any]:
    """LangGraph node representing the compliance analysis stage.

    Uses ComplianceAgent to compare policy against regulation and evaluate compliance.
    """
    logger.info("Compliance analysis node started")

    retrieval_result = state.get("retrieval_result")
    if not retrieval_result:
        err_msg = "Critical error in compliance node: retrieval_result is missing from graph state."
        logger.error(err_msg)
        raise ValueError(err_msg)

    try:
        compliance_analysis = compliance_agent.analyze(retrieval_result)
        logger.info("Compliance analysis node completed successfully")
        return {
            "compliance_analysis": compliance_analysis,
            "compliance_confidence": compliance_analysis.confidence
        }
    except Exception as e:
        err_msg = f"Compliance analysis failure: {str(e)}"
        logger.error(err_msg, exc_info=True)
        raise ValueError(err_msg)

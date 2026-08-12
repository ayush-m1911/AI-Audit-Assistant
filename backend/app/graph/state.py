from typing import TypedDict, List, Optional, Any, Dict
from app.models.evidence_models import RetrievalResult


class AuditState(TypedDict):
    """LangGraph state schema for the AuditFlow AI compliance audit assistant."""

    # Core Phase 4A fields
    question: str
    audit_type: Optional[str]
    subject: Optional[str]
    regulation: Optional[str]
    intent: Optional[str]
    retrieval_result: Optional[RetrievalResult]
    confidence: Optional[float]
    confidence_level: Optional[str]
    errors: List[str]

    # Reserved fields for future agent phases (Phase 4B - 4F)
    compliance_findings: Optional[List[Any]]
    risk_assessment: Optional[Dict[str, Any]]
    recommendations: Optional[List[Any]]
    review_status: Optional[str]
    final_report: Optional[Dict[str, Any]]

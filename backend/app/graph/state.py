from typing import TypedDict, List, Optional, Any, Dict
from app.models.evidence_models import RetrievalResult
from app.models.compliance_models import ComplianceAnalysis


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

    # Core Phase 4B fields
    compliance_analysis: Optional[ComplianceAnalysis]
    retrieval_confidence: Optional[float]
    compliance_confidence: Optional[float]

    # Reserved fields for future agent phases (Phase 4C - 4F)
    compliance_findings: Optional[List[Any]]
    risk_assessment: Optional[Dict[str, Any]]
    recommendations: Optional[List[Any]]
    review_status: Optional[str]
    final_report: Optional[Dict[str, Any]]

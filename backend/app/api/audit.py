from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.document_models import SearchRequest, RetrieveRequest, RetrieveResponse, EvidenceResponse
from app.services.retriever import retrieval_service
from app.utils.logger import logger

router = APIRouter()


@router.post("/search", response_model=List[EvidenceResponse], status_code=status.HTTP_200_OK)
def search_evidence(request: SearchRequest, db: Session = Depends(get_db)):
    """Search for matching evidence based on query and optional filters."""
    logger.info(f"API Search request received: query='{request.query}', type='{request.document_type}', version='{request.document_version}'")

    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty."
        )

    try:
        filters = {}
        if request.document_type:
            filters["document_type"] = request.document_type
        if request.document_version:
            filters["document_version"] = request.document_version

        results = retrieval_service.search(db, request.query, filters=filters)
        return results
    except Exception as e:
        logger.error(f"API Search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {e}"
        )


@router.post("/retrieve", response_model=RetrieveResponse, status_code=status.HTTP_200_OK)
def retrieve_evidence(request: RetrieveRequest, db: Session = Depends(get_db)):
    """Retrieve partitioned evidence packages (company policies vs regulations) for compliance audits."""
    logger.info(f"API Retrieve request received: question='{request.question}'")

    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question string cannot be empty."
        )

    try:
        evidence_package = retrieval_service.retrieve(db, request.question)
        return evidence_package
    except Exception as e:
        logger.error(f"API Retrieve failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evidence retrieval failed: {e}"
        )

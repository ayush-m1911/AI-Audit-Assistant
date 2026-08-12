import uuid
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session

from app.models.document_models import EvidenceResponse as Evidence
from app.services.postgres import postgres_service
from app.services.vectordb import vectordb_service
from app.services.reranker import BaseReranker, default_reranker
from app.utils.logger import logger


class RetrievalService:
    """Service responsible for query embedding, vector search, version-aware filtering, and reranking."""

    def __init__(self, reranker: Optional[BaseReranker] = None) -> None:
        """Initialize the RetrievalService with an optional custom reranker.

        Args:
            reranker (Optional[BaseReranker]): Reranking engine (defaults to SimilarityReranker).
        """
        self.reranker = reranker or default_reranker

    def search(
        self,
        db: Session,
        query: str,
        filters: Optional[dict] = None,
        limit: int = 5
    ) -> List[Evidence]:
        """Perform semantic search on Qdrant with filters, defaulting to latest document versions.

        Args:
            db (Session): Database session.
            query (str): The search query text.
            filters (Optional[dict]): Dictionary of filters (e.g. document_type, document_version).
            limit (int): Maximum number of evidence elements to return.

        Returns:
            List[Evidence]: Ordered and reranked list of Evidence objects.
        """
        logger.info(f"Embedding Query: '{query[:60]}...'")

        resolved_filters = (filters or {}).copy()

        # If no specific version or ID is requested, default to only the latest uploaded documents
        if "document_version" not in resolved_filters and "document_id" not in resolved_filters:
            latest_docs = postgres_service.get_latest_documents(db)
            latest_ids = [doc.id for doc in latest_docs]
            if latest_ids:
                resolved_filters["document_ids"] = latest_ids
            else:
                logger.info("No active documents found in PostgreSQL metadata database.")
                return []

        # Query Qdrant
        raw_hits = vectordb_service.search_with_filter(
            query=query,
            filters=resolved_filters,
            limit=limit
        )

        # Convert raw vector hits to structured Evidence objects
        evidence_list = []
        for hit in raw_hits:
            payload = hit["payload"]
            evidence_list.append(
                Evidence(
                    document_id=uuid.UUID(payload["document_id"]),
                    document_version=payload["document_version"],
                    filename=payload["filename"],
                    document_type=payload["document_type"],
                    page_number=payload.get("page_number"),
                    chunk_index=payload["chunk_index"],
                    similarity_score=hit["score"],
                    text=payload["text"]
                )
            )

        # Apply reranking
        logger.info("Reranking starts...")
        reranked_evidence = self.reranker.rerank(query, evidence_list)

        logger.info(f"Evidence Returned: {len(reranked_evidence)} items.")
        return reranked_evidence

    def search_by_document_type(
        self,
        db: Session,
        query: str,
        document_type: str,
        limit: int = 5
    ) -> List[Evidence]:
        """Perform semantic search filtered by a specific document type.

        Args:
            db (Session): Database session.
            query (str): The search query text.
            document_type (str): Type of the document to search within.
            limit (int): Max number of results.

        Returns:
            List[Evidence]: Reranked evidence list.
        """
        filters = {"document_type": document_type}
        return self.search(db, query, filters=filters, limit=limit)

    def retrieve(
        self,
        db: Session,
        question: str
    ) -> Dict[str, List[Evidence]]:
        """Retrieve partitioned evidence packages (company policies vs regulations) for audits.

        Args:
            db (Session): Database session.
            question (str): The compliance audit question.

        Returns:
            Dict[str, List[Evidence]]: Dictionary containing company_policy and regulations lists.
        """
        logger.info(f"Starting retrieve workflow for question: '{question[:60]}...'")

        # 1. Retrieve company documents (policies, SOPs, contracts)
        logger.info("Searching Company Documents...")
        company_evidence = []
        for doc_type in ["company_policy", "sop", "contract"]:
            results = self.search(db, question, filters={"document_type": doc_type}, limit=5)
            company_evidence.extend(results)
        # Rerank the combined company evidence and slice to top 5
        company_evidence = self.reranker.rerank(question, company_evidence)[:5]

        # 2. Retrieve regulations
        logger.info("Searching Regulations...")
        regulations_evidence = self.search(
            db,
            question,
            filters={"document_type": "regulation"},
            limit=5
        )

        return {
            "company_policy": company_evidence,
            "regulations": regulations_evidence
        }


# Singleton service instance
retrieval_service = RetrievalService()

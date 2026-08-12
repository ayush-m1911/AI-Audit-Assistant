from abc import ABC, abstractmethod
from typing import List

from app.models.document_models import EvidenceResponse as Evidence
from app.utils.logger import logger


class BaseReranker(ABC):
    """Abstract base class for evidence reranking engines."""

    @abstractmethod
    def rerank(self, query: str, evidence_list: List[Evidence]) -> List[Evidence]:
        """Rerank a list of Evidence items against a query string.

        Args:
            query (str): The search query.
            evidence_list (List[Evidence]): The list of evidence to rerank.

        Returns:
            List[Evidence]: The sorted, reranked list of evidence.
        """
        pass


class SimilarityReranker(BaseReranker):
    """Simple similarity-based reranker that sorts evidence by vector distance score."""

    def rerank(self, query: str, evidence_list: List[Evidence]) -> List[Evidence]:
        """Rerank using the similarity scores directly.

        Args:
            query (str): The search query.
            evidence_list (List[Evidence]): List of evidence.

        Returns:
            List[Evidence]: Sorted evidence by similarity score descending.
        """
        logger.info(f"Reranking: Sorting {len(evidence_list)} evidence items by similarity score.")
        return sorted(evidence_list, key=lambda x: x.similarity_score, reverse=True)


# Expose standard/default reranker instance
default_reranker = SimilarityReranker()

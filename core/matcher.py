"""Matching logic between Excel projects and cluster documents

This module:
- Matches Excel projects with cluster projects
- Calculates similarity scores
- Identifies common keywords and project codes
"""

from typing import List, Dict, Tuple, Set
from .models import ProjectMatch
from .document_processor import ClusterDocumentManager, ClusterProject
from config.keywords import (
    BLOCKCHAIN_KEYWORDS,
    PRIVACY_KEYWORDS,
    DATA_GOVERNANCE_KEYWORDS,
    AI_KEYWORDS,
    IOT_KEYWORDS
)
import re


class MatchResult:
    """Result of matching Excel project with cluster project"""
    
    def __init__(self, cluster_project: ClusterProject, score: int, matched_terms: List[str]):
        self.cluster_project = cluster_project
        self.score = score
        self.matched_terms = matched_terms
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'cluster_project': self.cluster_project.to_dict(),
            'similarity_score': self.score,
            'matched_terms': self.matched_terms
        }


class ClusterMatcher:
    """Matches Excel projects with cluster documents"""
    
    def __init__(self, cluster_manager: ClusterDocumentManager):
        self.cluster_manager = cluster_manager
        self.all_keywords = self._collect_all_keywords()
    
    def _collect_all_keywords(self) -> List[str]:
        """Collect all keywords from all categories"""
        return (
            list(BLOCKCHAIN_KEYWORDS) +
            list(PRIVACY_KEYWORDS) +
            list(DATA_GOVERNANCE_KEYWORDS) +
            list(AI_KEYWORDS) +
            list(IOT_KEYWORDS)
        )
    
    def match_excel_with_clusters(self, excel_match: ProjectMatch) -> Dict:
        """Match an Excel project with cluster projects
        
        Args:
            excel_match: ProjectMatch object from Excel analysis
        
        Returns:
            Dictionary with matching results
        """
        excel_text = self._extract_excel_text(excel_match)
        excel_codes = self._extract_project_codes(excel_text)
        
        matching_clusters = []
        
        # Check each cluster project
        for doc in self.cluster_manager.documents:
            for cluster_project in doc.projects:
                score, matched_terms = self._calculate_match_score(
                    excel_text,
                    excel_codes,
                    cluster_project
                )
                
                if score > 0:
                    match_result = MatchResult(cluster_project, score, matched_terms)
                    matching_clusters.append(match_result)
        
        # Sort by score (highest first)
        matching_clusters.sort(key=lambda x: x.score, reverse=True)
        
        return {
            'excel_match': excel_match,
            'cluster_matches': matching_clusters[:10],  # Top 10 matches
            'total_matches': len(matching_clusters),
            'has_matches': len(matching_clusters) > 0
        }
    
    def _extract_excel_text(self, excel_match: ProjectMatch) -> str:
        """Extract searchable text from Excel project"""
        text_parts = []
        
        for key, value in excel_match.project_data.items():
            if value and str(value).strip() and str(value) != 'nan':
                text_parts.append(str(value))
        
        return ' '.join(text_parts).lower()
    
    def _extract_project_codes(self, text: str) -> Set[str]:
        """Extract Horizon project codes from text"""
        pattern = r'HORIZON-[A-Z0-9-]+'
        codes = re.findall(pattern, text.upper())
        return set(code.lower() for code in codes)
    
    def _calculate_match_score(
        self, 
        excel_text: str, 
        excel_codes: Set[str], 
        cluster_project: ClusterProject
    ) -> Tuple[int, List[str]]:
        """Calculate match score between Excel and cluster project
        
        Scoring:
        - Exact code match: +20 points
        - Each keyword match: +2 points
        
        Returns:
            (score, list of matched terms)
        """
        score = 0
        matched_terms = []
        
        # Check for exact code match (highest priority)
        cluster_code = cluster_project.code.lower()
        if cluster_code in excel_codes:
            score += 20
            matched_terms.append(f"CODE:{cluster_project.code}")
        
        # Check keyword matches
        cluster_text = cluster_project.full_text.lower()
        
        for keyword in self.all_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in excel_text and keyword_lower in cluster_text:
                score += 2
                if keyword not in matched_terms:
                    matched_terms.append(keyword)
        
        return score, matched_terms
    
    def batch_match_all(self, excel_matches: List[ProjectMatch]) -> Dict:
        """Match all Excel projects with clusters
        
        Args:
            excel_matches: List of ProjectMatch objects
        
        Returns:
            Summary statistics and results
        """
        results = []
        total_cluster_matches = 0
        projects_with_matches = 0
        
        for excel_match in excel_matches:
            match_result = self.match_excel_with_clusters(excel_match)
            results.append(match_result)
            
            if match_result['has_matches']:
                projects_with_matches += 1
                total_cluster_matches += match_result['total_matches']
        
        return {
            'results': results,
            'summary': {
                'total_excel_projects': len(excel_matches),
                'projects_with_cluster_matches': projects_with_matches,
                'total_cluster_matches': total_cluster_matches,
                'avg_matches_per_project': (
                    total_cluster_matches / len(excel_matches) 
                    if excel_matches else 0
                )
            }
        }
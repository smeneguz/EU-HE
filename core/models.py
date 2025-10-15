"""Data models for project analysis"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ProjectMatch:
    """Represents a matched project opportunity"""
    
    row_index: int
    sheet_name: str
    score: int
    matched_keywords: Dict[str, List[str]]
    technologies: List[str]
    potential_roles: List[str]
    contributions: List[str]
    project_data: Dict
    
    @property
    def priority_level(self) -> str:
        """Get priority level based on score"""
        from config.keywords import HIGH_PRIORITY_THRESHOLD, MEDIUM_PRIORITY_THRESHOLD
        
        if self.score >= HIGH_PRIORITY_THRESHOLD:
            return "HIGH"
        elif self.score >= MEDIUM_PRIORITY_THRESHOLD:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_project_title(self) -> str:
        """Extract project title from data"""
        for key in ['Title', 'title', 'Project Title', 'PROJECT_TITLE', 'Call title']:
            if key in self.project_data and self.project_data[key]:
                return str(self.project_data[key])[:100]
        return f"Project at row {self.row_index + 1}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'row_index': self.row_index,
            'sheet_name': self.sheet_name,
            'score': self.score,
            'priority': self.priority_level,
            'title': self.get_project_title(),
            'matched_keywords': self.matched_keywords,
            'technologies': self.technologies,
            'potential_roles': self.potential_roles,
            'contributions': self.contributions,
            'project_data': self.project_data
        }
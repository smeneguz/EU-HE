"""Filter components"""

import streamlit as st
from typing import List, Tuple
from core.models import ProjectMatch


def display_filters(matches: List[ProjectMatch]) -> Tuple[List[str], List[str], List[str]]:
    """Display filter controls and return selected filters"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        priority_filter = st.multiselect(
            "Filter by Priority",
            ["HIGH", "MEDIUM", "LOW"],
            default=["HIGH", "MEDIUM", "LOW"]
        )
    
    with col2:
        tech_options = list(set(
            tech 
            for match in matches 
            for tech in match.technologies
        ))
        tech_filter = st.multiselect(
            "Filter by Technology",
            tech_options,
            default=tech_options
        )
    
    with col3:
        sheet_options = list(set(match.sheet_name for match in matches))
        sheet_filter = st.multiselect(
            "Filter by Sheet",
            sheet_options,
            default=sheet_options
        )
    
    return priority_filter, tech_filter, sheet_filter


def apply_filters(matches: List[ProjectMatch], 
                 priority_filter: List[str],
                 tech_filter: List[str],
                 sheet_filter: List[str]) -> List[ProjectMatch]:
    """Apply filters to matches"""
    filtered = [
        m for m in matches
        if m.priority_level in priority_filter
        and any(tech in tech_filter for tech in m.technologies)
        and m.sheet_name in sheet_filter
    ]
    return filtered
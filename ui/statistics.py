"""Statistics display component"""

import streamlit as st
import re
from typing import List
from core.models import ProjectMatch
from utils.project_info import extract_project_info


def display_statistics(matches: List[ProjectMatch]):
    """Display analysis statistics"""
    high_priority = sum(1 for m in matches if m.priority_level == "HIGH")
    medium_priority = sum(1 for m in matches if m.priority_level == "MEDIUM")
    low_priority = sum(1 for m in matches if m.priority_level == "LOW")
    
    # Calculate total partners if available
    total_partners = 0
    partners_found = 0
    
    # Count by sheet
    sheet_counts = {}
    for match in matches:
        sheet_counts[match.sheet_name] = sheet_counts.get(match.sheet_name, 0) + 1
        
        info = extract_project_info(match)
        if info['partners']:
            try:
                numbers = re.findall(r'\d+', info['partners'])
                if numbers:
                    total_partners += int(numbers[0])
                    partners_found += 1
            except:
                pass
    
    # Main metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Matches", len(matches))
    with col2:
        st.metric("High Priority", high_priority, help="Coordinator/Tech Lead potential")
    with col3:
        st.metric("Medium Priority", medium_priority, help="WP/Task Leader potential")
    with col4:
        st.metric("Low Priority", low_priority, help="Partner potential")
    with col5:
        if partners_found > 0:
            avg_partners = total_partners / partners_found
            st.metric("Avg Partners", f"{avg_partners:.1f}", 
                     help=f"Average consortium size ({partners_found} projects)")
        else:
            st.metric("Avg Partners", "N/A", help="Partner information not available")
    
    # Sheet breakdown
    if len(sheet_counts) > 1:
        st.divider()
        st.subheader("Matches by Sheet")
        sheet_cols = st.columns(len(sheet_counts))
        for idx, (sheet_name, count) in enumerate(sorted(sheet_counts.items(), 
                                                         key=lambda x: x[1], reverse=True)):
            with sheet_cols[idx]:
                st.metric(sheet_name, count)
"""Project card display component"""

import streamlit as st
from core.models import ProjectMatch
from utils.project_info import extract_project_info


def get_priority_color(priority: str) -> str:
    """Get color for priority level"""
    colors = {
        "HIGH": "#90EE90",
        "MEDIUM": "#FFD700",
        "LOW": "#87CEEB"
    }
    return colors.get(priority, "#FFFFFF")


def display_match_card(match: ProjectMatch, index: int):
    """Display a match as a card with detailed information"""
    priority_color = get_priority_color(match.priority_level)
    info = extract_project_info(match)
    
    with st.expander(
        f"#{index} - {info['title'] or match.get_project_title()} - Score: {match.score} ({match.priority_level})",
        expanded=False
    ):
        # Header with colored background
        st.markdown(f"""
        <div style="background-color: {priority_color}; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
            <h4 style="margin: 0;">{info['title'] or match.get_project_title()}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Project metadata
        _display_project_metadata(match, info)
        
        st.divider()
        
        # Technologies and matching
        _display_technology_matching(match)
        
        # Additional details
        _display_additional_details(info)
        
        # Raw data viewer
        with st.expander("🔧 View Raw Data"):
            st.json(match.project_data)


def _display_project_metadata(match: ProjectMatch, info: dict):
    """Display project metadata section"""
    st.subheader("📋 Project Information")
    
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    
    with meta_col1:
        st.write(f"**Sheet:** {match.sheet_name}")
        st.write(f"**Excel Row:** {match.row_index}")
        st.write(f"**Score:** {match.score}")
        st.write(f"**Priority:** {match.priority_level}")
    
    with meta_col2:
        if info['call_id']:
            st.write(f"**Call ID:** {info['call_id']}")
        if info['opening_date']:
            st.write(f"**Opening:** {info['opening_date']}")
        if info['deadline']:
            st.write(f"**Deadline:** {info['deadline']}")
        if info['type_of_action']:
            st.write(f"**Action Type:** {info['type_of_action']}")
    
    with meta_col3:
        if info['budget']:
            st.write(f"**Budget:** {info['budget']}")
        if info['partners']:
            st.write(f"**Partners:** {info['partners']}")
        if info['coordinator']:
            st.write(f"**Coordinator:** {info['coordinator']}")
        if info['url']:
            st.markdown(f"**[📎 Call Link]({info['url']})**")


def _display_technology_matching(match: ProjectMatch):
    """Display technology matching section"""
    st.subheader("🔍 Technology Matching")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Technologies:**")
        for tech in match.technologies:
            st.write(f"- {tech}")
        
        st.write("")
        st.write("**Matched Keywords:**")
        for category, keywords in match.matched_keywords.items():
            st.write(f"*{category.replace('_', ' ').title()}:*")
            st.write(f"{', '.join(keywords)}")
    
    with col2:
        st.write("**Potential Roles:**")
        for role in match.potential_roles:
            st.write(f"- {role}")
        
        st.write("")
        st.write("**Suggested Contributions:**")
        for contrib in match.contributions:
            st.write(f"- {contrib}")


def _display_additional_details(info: dict):
    """Display additional project details"""
    if info['description'] or info['scope'] or info['expected_outcomes'] or info['topics']:
        st.divider()
        st.subheader("📝 Additional Details")
        
        if info['topics']:
            with st.container():
                st.write("**Topics/Destination:**")
                st.info(info['topics'])
        
        if info['description']:
            with st.container():
                st.write("**Description:**")
                st.info(info['description'][:1000] + "..." 
                       if len(info['description']) > 1000 else info['description'])
        
        if info['scope']:
            with st.container():
                st.write("**Scope:**")
                st.info(info['scope'][:1000] + "..." 
                       if len(info['scope']) > 1000 else info['scope'])
        
        if info['expected_outcomes']:
            with st.container():
                st.write("**Expected Outcomes:**")
                st.info(info['expected_outcomes'][:1000] + "..." 
                       if len(info['expected_outcomes']) > 1000 else info['expected_outcomes'])
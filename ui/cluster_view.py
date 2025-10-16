"""UI components for cluster document visualization

This module provides:
- Cluster statistics display
- Cluster project cards
- Search interface
- Match visualization
"""

import streamlit as st
from typing import List, Dict
from core.document_processor import ClusterDocumentManager, ClusterProject
from core.matcher import ClusterMatcher, MatchResult


def display_cluster_statistics(cluster_manager: ClusterDocumentManager):
    """Display overview statistics for cluster documents"""
    if not cluster_manager.documents:
        st.warning("No cluster documents loaded")
        return
    
    stats = cluster_manager.get_statistics()
    
    st.subheader("Cluster Documents Overview")
    
    # Main metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Cluster Documents", stats['total_documents'])
    with col2:
        st.metric("Total Projects", stats['total_projects'])
    with col3:
        avg = stats['total_projects'] / stats['total_documents'] if stats['total_documents'] > 0 else 0
        st.metric("Avg Projects/Doc", f"{avg:.1f}")
    
    # Document details
    with st.expander("View Document Details"):
        for detail in stats['document_details']:
            st.write(f"**{detail['name']}** ({detail['file']}): {detail['projects']} projects")


def display_cluster_project_card(project: ClusterProject, index: int = None):
    """Display a single cluster project as a card"""
    header = f"#{index} - " if index else ""
    header += f"{project.code}: {project.title}"
    
    with st.expander(header, expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Code:** {project.code}")
            st.write(f"**Title:** {project.title}")
            st.write(f"**Cluster:** {project.cluster_name}")
        
        with col2:
            st.write(f"**Text Length:** {len(project.full_text)} chars")
        
        st.divider()
        
        st.write("**Description:**")
        st.info(project.description[:800] + "..." if len(project.description) > 800 else project.description)
        
        with st.expander("🔧 View Full Text"):
            st.text(project.full_text)


def display_cluster_search(cluster_manager: ClusterDocumentManager):
    """Display search interface for cluster documents"""
    st.subheader("Search in Cluster Documents")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Enter keywords (comma-separated)",
            placeholder="e.g., blockchain, privacy, AI"
        )
    
    with col2:
        max_results = st.number_input("Max results", min_value=5, max_value=50, value=10)
    
    if search_query:
        keywords = [k.strip() for k in search_query.split(',') if k.strip()]
        results = cluster_manager.search_by_keywords(keywords)
        
        st.write(f"**Found {len(results)} matching projects** (showing top {max_results})")
        
        if results:
            for idx, result in enumerate(results[:max_results], 1):
                project = result['project']
                
                with st.expander(
                    f"{idx}. {project.code} - {project.title} "
                    f"({result['match_count']} keyword matches)",
                    expanded=False
                ):
                    st.write(f"**Cluster:** {project.cluster_name}")
                    st.write(f"**Matched Keywords:** {', '.join(result['matched_keywords'])}")
                    st.write(f"**Description:** {project.description[:400]}...")
        else:
            st.info("No projects found matching your keywords")


def display_cluster_matches_for_excel(match_result: Dict):
    """Display cluster matches for a specific Excel project"""
    if not match_result['has_matches']:
        st.info("No matching cluster projects found")
        return
    
    st.write(f"**{match_result['total_matches']} cluster matches found** (showing top 10)")
    
    for idx, match in enumerate(match_result['cluster_matches'][:10], 1):
        cluster_proj = match.cluster_project
        
        # Color code by score
        if match.score >= 20:
            color = "🟢"  # Green for high match (code match)
        elif match.score >= 10:
            color = "🟡"  # Yellow for medium match
        else:
            color = "🔵"  # Blue for low match
        
        with st.expander(
            f"{color} #{idx} - {cluster_proj.code}: {cluster_proj.title} "
            f"(Score: {match.score})",
            expanded=(idx == 1)  # Expand first match
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Code:** {cluster_proj.code}")
                st.write(f"**Cluster:** {cluster_proj.cluster_name}")
                st.write(f"**Match Score:** {match.score}")
            
            with col2:
                if match.matched_terms:
                    st.write("**Matched Terms:**")
                    for term in match.matched_terms[:10]:
                        st.write(f"- {term}")
            
            st.divider()
            st.write("**Description:**")
            st.info(cluster_proj.description[:500] + "..." 
                   if len(cluster_proj.description) > 500 
                   else cluster_proj.description)


def display_cluster_browser(cluster_manager: ClusterDocumentManager):
    """Display interactive browser for all cluster projects"""
    st.subheader("Browse All Cluster Projects")
    
    all_projects = cluster_manager.get_all_projects()
    
    if not all_projects:
        st.warning("No cluster projects available")
        return
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        clusters = list(set(p.cluster_name for p in all_projects))
        selected_clusters = st.multiselect(
            "Filter by Cluster",
            clusters,
            default=clusters
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Code", "Title", "Cluster"]
        )
    
    # Filter and sort
    filtered_projects = [
        p for p in all_projects 
        if p.cluster_name in selected_clusters
    ]
    
    if sort_by == "Code":
        filtered_projects.sort(key=lambda x: x.code)
    elif sort_by == "Title":
        filtered_projects.sort(key=lambda x: x.title)
    else:
        filtered_projects.sort(key=lambda x: x.cluster_name)
    
    st.write(f"**Showing {len(filtered_projects)} projects**")
    
    # Display projects
    for idx, project in enumerate(filtered_projects, 1):
        display_cluster_project_card(project, idx)
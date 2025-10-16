"""Streamlit web application for Horizon Europe Project Analyzer

Main application orchestrating:
- Excel project analysis
- Cluster document management
- Project matching
"""
import streamlit as st
import pandas as pd
from pathlib import Path

from core.analyzer import ProjectAnalyzer
from core.document_processor import ClusterDocumentManager
from core.matcher import ClusterMatcher
# REMOVED: from core.llm_integration import LLMAnalyzer, LLMConfig

from ui.statistics import display_statistics
from ui.project_card import display_match_card
from ui.pagination import display_pagination, get_paginated_items
from ui.filters import display_filters, apply_filters
from ui.cluster_view import (
    display_cluster_statistics,
    display_cluster_search,
    display_cluster_matches_for_excel,
    display_cluster_browser
)

from utils.export import export_to_csv, export_to_json


def init_session_state():
    """Initialize session state variables"""
    defaults = {
        # Excel analysis
        'analyzer': None,
        'matches': [],
        'analyzed': False,
        
        # Pagination
        'current_page': 1,
        'items_per_page': 10,
        'last_filter_count': 0,
        
        # Cluster documents
        'cluster_manager': None,
        'cluster_matcher': None,
        'clusters_loaded': False,
        # REMOVED LLM for now
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_cluster_documents() -> bool:
    """Load cluster documents from clusters/ folder
    
    Returns:
        True if documents were loaded successfully
    """
    clusters_path = Path(__file__).parent / "clusters"
    
    try:
        cluster_manager = ClusterDocumentManager(str(clusters_path))
        st.session_state.cluster_manager = cluster_manager
        
        if cluster_manager.documents:
            st.session_state.cluster_matcher = ClusterMatcher(cluster_manager)
            st.session_state.clusters_loaded = True
            return True
        else:
            st.warning("Clusters folder found but no valid documents loaded")
            return False
    except Exception as e:
        st.error(f"Error loading cluster documents: {e}")
        return False


def display_sidebar():
    """Display sidebar with configuration and statistics"""
    with st.sidebar:
        st.header("Configuration")
        
        # Cluster documents section
        st.divider()
        st.subheader("Cluster Documents")
        
        if st.button("Load/Reload Clusters", use_container_width=True):
            with st.spinner("Loading cluster documents..."):
                if load_cluster_documents():
                    stats = st.session_state.cluster_manager.get_statistics()
                    st.success(f"Loaded {stats['total_documents']} documents "
                             f"with {stats['total_projects']} projects")
                    st.rerun()
                else:
                    st.error("Failed to load cluster documents")
        
        if st.session_state.clusters_loaded:
            stats = st.session_state.cluster_manager.get_statistics()
            st.metric("Documents", stats['total_documents'])
            st.metric("Projects", stats['total_projects'])
        
        # Keywords section
        with st.expander("View Keywords"):
            from config.keywords import (
                BLOCKCHAIN_KEYWORDS,
                PRIVACY_KEYWORDS,
                DATA_GOVERNANCE_KEYWORDS,
                AI_KEYWORDS,
                IOT_KEYWORDS
            )
            
            st.subheader("Blockchain/DLT")
            st.caption(", ".join(BLOCKCHAIN_KEYWORDS))
            
            st.subheader("Privacy-Preserving")
            st.caption(", ".join(PRIVACY_KEYWORDS))
            
            st.subheader("Data Governance")
            st.caption(", ".join(DATA_GOVERNANCE_KEYWORDS))
            
            st.subheader("AI/ML")
            st.caption(", ".join(AI_KEYWORDS))
            
            st.subheader("IoT")
            st.caption(", ".join(IOT_KEYWORDS))
        
        # Scoring thresholds
        with st.expander("Scoring Thresholds"):
            from config.keywords import (
                HIGH_PRIORITY_THRESHOLD,
                MEDIUM_PRIORITY_THRESHOLD,
                MIN_SCORE_THRESHOLD
            )
            
            st.write(f"**High Priority:** >= {HIGH_PRIORITY_THRESHOLD}")
            st.write(f"**Medium Priority:** >= {MEDIUM_PRIORITY_THRESHOLD}")
            st.write(f"**Minimum Score:** >= {MIN_SCORE_THRESHOLD}")
        
        # Quick stats (if analyzed)
        if st.session_state.analyzed:
            st.divider()
            st.subheader("Quick Stats")
            st.metric("Total Matches", len(st.session_state.matches))
            
            sheets = set(m.sheet_name for m in st.session_state.matches)
            with st.expander(f" Sheets ({len(sheets)})"):
                for sheet in sorted(sheets):
                    count = sum(1 for m in st.session_state.matches if m.sheet_name == sheet)
                    st.write(f"{sheet}: {count}")
            
            all_techs = set()
            for m in st.session_state.matches:
                all_techs.update(m.technologies)
            st.metric("Technologies", len(all_techs))


def display_file_upload():
    """Display file upload section"""
    st.header("Upload Excel File")
    
    uploaded_file = st.file_uploader(
        "Choose your Horizon Europe Excel file",
        type=['xlsx', 'xls'],
        help="Upload the Excel file containing project information (all sheets will be analyzed)"
    )
    
    if uploaded_file is not None:
        temp_path = Path("/tmp") / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"File uploaded: {uploaded_file.name}")
        
        # Show available sheets
        try:
            xls = pd.ExcelFile(temp_path)
            st.info(f" Found {len(xls.sheet_names)} sheet(s): {', '.join(xls.sheet_names)}")
        except Exception as e:
            st.error(f"Error reading file: {e}")
        
        # Analyze button
        if st.button("Analyze Projects", type="primary", use_container_width=True):
            with st.spinner("Analyzing all sheets..."):
                try:
                    analyzer = ProjectAnalyzer(str(temp_path))
                    matches = analyzer.analyze_all()
                    
                    st.session_state.analyzer = analyzer
                    st.session_state.matches = matches
                    st.session_state.analyzed = True
                    st.session_state.current_page = 1
                    
                    st.success(f"Analysis complete! Found {len(matches)} matching projects")
                    
                    # Auto-load clusters if not loaded
                    if not st.session_state.clusters_loaded:
                        with st.spinner("Loading cluster documents..."):
                            load_cluster_documents()
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())


def display_excel_results():
    """Display Excel analysis results"""
    st.divider()
    st.header("Analysis Results")
    
    display_statistics(st.session_state.matches)
    
    st.divider()
    
    # Filters
    priority_filter, tech_filter, sheet_filter = display_filters(st.session_state.matches)
    
    # Apply filters
    filtered_matches = apply_filters(
        st.session_state.matches,
        priority_filter,
        tech_filter,
        sheet_filter
    )
    
    # Reset page if filter changes
    if st.session_state.last_filter_count != len(filtered_matches):
        st.session_state.current_page = 1
        st.session_state.last_filter_count = len(filtered_matches)
    
    st.write(f"**Showing {len(filtered_matches)} of {len(st.session_state.matches)} projects**")
    
    # Pagination settings
    st.divider()
    col1, col2 = st.columns([1, 3])
    with col1:
        st.session_state.items_per_page = st.selectbox(
            "Items per page",
            [5, 10, 20, 50],
            index=1
        )
    with col2:
        show_clusters = st.checkbox(
            "Show cluster matches",
            value=st.session_state.clusters_loaded,
            disabled=not st.session_state.clusters_loaded
        )
    
    # Display matches
    st.divider()
    st.header("Matched Projects")
    
    if filtered_matches:
        current_page = display_pagination(len(filtered_matches), st.session_state.items_per_page)
        page_items, start_idx = get_paginated_items(
            filtered_matches, 
            current_page, 
            st.session_state.items_per_page
        )
        
        for idx, match in enumerate(page_items, start=start_idx + 1):
            display_match_card(match, idx, show_cluster_matches=False)
            
            # Show cluster matches if enabled
            if show_clusters and st.session_state.cluster_matcher:
                with st.expander("Cluster Matches", expanded=False):
                    cluster_result = st.session_state.cluster_matcher.match_excel_with_clusters(match)
                    display_cluster_matches_for_excel(cluster_result)
        
        st.divider()
        display_pagination(len(filtered_matches), st.session_state.items_per_page)
    else:
        st.warning("No projects match the current filters.")
    
    # Export section
    display_export_section(filtered_matches)


def display_cluster_tab():
    """Display cluster documents tab"""
    st.header("Cluster Documents")
    
    if not st.session_state.clusters_loaded:
        st.warning("No cluster documents loaded")
        st.info("Click 'Load/Reload Clusters' in the sidebar to load documents from the clusters/ folder")
        
        if st.button("Load Clusters Now", type="primary"):
            if load_cluster_documents():
                st.success("Clusters loaded!")
                st.rerun()
        return
    
    # Statistics
    display_cluster_statistics(st.session_state.cluster_manager)
    
    st.divider()
    
    # Tabs within cluster view
    cluster_tab1, cluster_tab2 = st.tabs(["Search", "Browse All"])
    
    with cluster_tab1:
        display_cluster_search(st.session_state.cluster_manager)
    
    with cluster_tab2:
        display_cluster_browser(st.session_state.cluster_manager)


def display_export_section(filtered_matches):
    """Display export buttons"""
    st.divider()
    st.header("Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Filtered Results")
        csv_data = export_to_csv(filtered_matches)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="horizon_europe_filtered.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        json_data = export_to_json(filtered_matches)
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name="horizon_europe_filtered.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        st.subheader("All Results")
        csv_all = export_to_csv(st.session_state.matches)
        st.download_button(
            label="Download CSV",
            data=csv_all,
            file_name="horizon_europe_all.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        json_all = export_to_json(st.session_state.matches)
        st.download_button(
            label="Download JSON",
            data=json_all,
            file_name="horizon_europe_all.json",
            mime="application/json",
            use_container_width=True
        )


def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Horizon Europe Analyzer",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    
    # Header
    st.title("Horizon Europe Project Analyzer")
    st.caption("Advanced Technology Matching for EU Projects")
    
    st.markdown("""
    **Technology Focus:** Blockchain/DLT · Privacy-Preserving (ZK, TEE) · Data Governance · AI/ML · IoT
    """)
    
    # Main content tabs
    tab1, tab2 = st.tabs(["Excel Analysis", "Cluster Documents"])
    
    with tab1:
        display_file_upload()
        
        if st.session_state.analyzed and st.session_state.matches:
            display_excel_results()
        else:
            st.info("👆 Upload an Excel file to begin analysis")
    
    with tab2:
        display_cluster_tab()
    
    # Sidebar
    display_sidebar()
    
    # Footer
    st.divider()
    st.caption("Made with ❤️ for Links Foundation | by Silvio")


if __name__ == "__main__":
    main()
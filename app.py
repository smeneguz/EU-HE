"""Streamlit web application for Horizon Europe Project Analyzer"""

import streamlit as st
import pandas as pd
from pathlib import Path

from core.analyzer import ProjectAnalyzer
from ui.statistics import display_statistics
from ui.project_card import display_match_card
from ui.pagination import display_pagination, get_paginated_items
from ui.filters import display_filters, apply_filters
from utils.export import export_to_csv, export_to_json


def init_session_state():
    """Initialize session state variables"""
    defaults = {
        'analyzer': None,
        'matches': [],
        'analyzed': False,
        'current_page': 1,
        'items_per_page': 10,
        'last_filter_count': 0
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def display_sidebar():
    """Display sidebar with configuration"""
    with st.sidebar:
        st.header("Configuration")
        
        with st.expander("View Keywords"):
            from config.keywords import (
                BLOCKCHAIN_KEYWORDS,
                PRIVACY_KEYWORDS,
                DATA_GOVERNANCE_KEYWORDS,
                AI_KEYWORDS,
                IOT_KEYWORDS
            )
            
            st.subheader("Blockchain/DLT")
            st.write(", ".join(BLOCKCHAIN_KEYWORDS))
            
            st.subheader("Privacy-Preserving")
            st.write(", ".join(PRIVACY_KEYWORDS))
            
            st.subheader("Data Governance")
            st.write(", ".join(DATA_GOVERNANCE_KEYWORDS))
            
            st.subheader("AI/ML")
            st.write(", ".join(AI_KEYWORDS))
            
            st.subheader("IoT")
            st.write(", ".join(IOT_KEYWORDS))
        
        with st.expander("Scoring Thresholds"):
            from config.keywords import (
                HIGH_PRIORITY_THRESHOLD,
                MEDIUM_PRIORITY_THRESHOLD,
                MIN_SCORE_THRESHOLD
            )
            
            st.write(f"**High Priority:** >= {HIGH_PRIORITY_THRESHOLD}")
            st.write(f"**Medium Priority:** >= {MEDIUM_PRIORITY_THRESHOLD}")
            st.write(f"**Minimum Score:** >= {MIN_SCORE_THRESHOLD}")
        
        if st.session_state.analyzed:
            st.divider()
            st.subheader("Quick Stats")
            st.write(f"Total Projects: {len(st.session_state.matches)}")
            
            sheets = set(m.sheet_name for m in st.session_state.matches)
            st.write(f"Sheets Analyzed: {len(sheets)}")
            for sheet in sorted(sheets):
                count = sum(1 for m in st.session_state.matches if m.sheet_name == sheet)
                st.write(f"  - {sheet}: {count}")
            
            all_techs = set()
            for m in st.session_state.matches:
                all_techs.update(m.technologies)
            st.write(f"Technologies Found: {len(all_techs)}")


def display_file_upload():
    """Display file upload section"""
    st.header("1. Upload Excel File")
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
            st.info(f"📑 Found {len(xls.sheet_names)} sheet(s): {', '.join(xls.sheet_names)}")
        except:
            pass
        
        # Analyze button
        if st.button("🔍 Analyze Projects", type="primary"):
            with st.spinner("Analyzing all sheets..."):
                try:
                    analyzer = ProjectAnalyzer(str(temp_path))
                    matches = analyzer.analyze_all()
                    
                    st.session_state.analyzer = analyzer
                    st.session_state.matches = matches
                    st.session_state.analyzed = True
                    st.session_state.current_page = 1
                    
                    st.success(f"Analysis complete! Found {len(matches)} matching projects across all sheets")
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())


def display_results():
    """Display analysis results"""
    st.divider()
    st.header("2. Analysis Results")
    
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
    items_per_page_col, _ = st.columns([1, 3])
    with items_per_page_col:
        st.session_state.items_per_page = st.selectbox(
            "Items per page",
            [5, 10, 20, 50],
            index=1
        )
    
    # Display matches
    st.divider()
    st.header("3. Matched Projects")
    
    if filtered_matches:
        current_page = display_pagination(len(filtered_matches), st.session_state.items_per_page)
        page_items, start_idx = get_paginated_items(filtered_matches, current_page, st.session_state.items_per_page)
        
        for idx, match in enumerate(page_items, start=start_idx + 1):
            display_match_card(match, idx)
        
        st.divider()
        display_pagination(len(filtered_matches), st.session_state.items_per_page)
    else:
        st.warning("No projects match the current filters.")
    
    # Export section
    display_export_section(filtered_matches)


def display_export_section(filtered_matches):
    """Display export buttons"""
    st.divider()
    st.header("4. Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = export_to_csv(filtered_matches)
        st.download_button(
            label="Download Filtered Results (CSV)",
            data=csv_data,
            file_name="horizon_europe_matches_filtered.csv",
            mime="text/csv"
        )
    
    with col2:
        json_data = export_to_json(filtered_matches)
        st.download_button(
            label="Download Filtered Results (JSON)",
            data=json_data,
            file_name="horizon_europe_matches_filtered.json",
            mime="application/json"
        )
    
    st.divider()
    col3, col4 = st.columns(2)
    
    with col3:
        csv_all = export_to_csv(st.session_state.matches)
        st.download_button(
            label="Download All Results (CSV)",
            data=csv_all,
            file_name="horizon_europe_matches_all.csv",
            mime="text/csv"
        )
    
    with col4:
        json_all = export_to_json(st.session_state.matches)
        st.download_button(
            label="Download All Results (JSON)",
            data=json_all,
            file_name="horizon_europe_matches_all.json",
            mime="application/json"
        )


def main():
    """Main application"""
    st.set_page_config(
        page_title="Horizon Europe Project Analyzer",
        page_icon="🔬",
        layout="wide"
    )
    
    init_session_state()
    
    st.title("Horizon Europe Project Analyzer")
    st.subheader("Silvio - Technology Matching Tool")
    
    st.markdown("""
    **Technology Focus:** Blockchain/DLT, Privacy-Preserving (ZK, TEE), Data Governance, AI/ML, IoT
    """)
    
    st.divider()
    
    display_file_upload()
    
    if st.session_state.analyzed and st.session_state.matches:
        display_results()
    
    display_sidebar()


if __name__ == "__main__":
    main()
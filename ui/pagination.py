"""Pagination component"""

import streamlit as st
import math
from typing import List, Tuple


def display_pagination(total_items: int, items_per_page: int) -> int:
    """Display pagination controls"""
    total_pages = math.ceil(total_items / items_per_page)
    
    if total_pages <= 1:
        return 1
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("First", disabled=(st.session_state.current_page == 1)):
            st.session_state.current_page = 1
            st.rerun()
    
    with col2:
        if st.button(" Prev", disabled=(st.session_state.current_page == 1)):
            st.session_state.current_page -= 1
            st.rerun()
    
    with col3:
        st.write(f"Page {st.session_state.current_page} of {total_pages} ({total_items} total items)")
    
    with col4:
        if st.button("Next ", disabled=(st.session_state.current_page == total_pages)):
            st.session_state.current_page += 1
            st.rerun()
    
    with col5:
        if st.button("Last", disabled=(st.session_state.current_page == total_pages)):
            st.session_state.current_page = total_pages
            st.rerun()
    
    return st.session_state.current_page


def get_paginated_items(items: List, page: int, items_per_page: int) -> Tuple[List, int]:
    """Get items for current page"""
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    return items[start_idx:end_idx], start_idx
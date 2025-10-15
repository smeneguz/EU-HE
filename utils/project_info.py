"""Project information extraction utilities"""

import pandas as pd
from typing import Dict, Any
from core.models import ProjectMatch


def extract_project_info(match: ProjectMatch) -> Dict[str, Any]:
    """Extract detailed project information from match data"""
    data = match.project_data
    
    info = {
        'title': None,
        'call_id': None,
        'deadline': None,
        'budget': None,
        'partners': None,
        'coordinator': None,
        'type_of_action': None,
        'topics': None,
        'description': None,
        'expected_outcomes': None,
        'scope': None,
        'opening_date': None,
        'url': None
    }
    
    # Title variations
    title_keys = ['Title', 'title', 'Project Title', 'PROJECT_TITLE', 'Call title', 'Topic title', 'Topic']
    info['title'] = _extract_first_valid(data, title_keys)
    
    # Call ID variations
    call_id_keys = ['Call ID', 'Call identifier', 'Topic ID', 'Identifier', 'ID', 'Topic identifier']
    info['call_id'] = _extract_first_valid(data, call_id_keys)
    
    # Deadline variations
    deadline_keys = ['Deadline', 'Submission deadline', 'Closing date', 'Deadline date', 'Deadline model']
    info['deadline'] = _extract_first_valid(data, deadline_keys)
    
    # Opening date
    opening_keys = ['Opening date', 'Opening', 'Start date']
    info['opening_date'] = _extract_first_valid(data, opening_keys)
    
    # Budget variations
    budget_keys = ['Budget', 'Total budget', 'Funding', 'Budget (EUR)', 'EU contribution', 'Indicative budget']
    info['budget'] = _extract_first_valid(data, budget_keys)
    
    # Partners variations
    partner_keys = ['Partners', 'Number of partners', 'Expected partners', 'Consortium size', 
                    'Min partners', 'Max partners', 'Planned number of grants']
    info['partners'] = _extract_first_valid(data, partner_keys)
    
    # Coordinator variations
    coordinator_keys = ['Coordinator', 'Coordinating entity', 'Lead partner']
    info['coordinator'] = _extract_first_valid(data, coordinator_keys)
    
    # Type of action variations
    action_keys = ['Type of Action', 'Action type', 'Type', 'Action', 'Type of action']
    info['type_of_action'] = _extract_first_valid(data, action_keys)
    
    # Topics variations (excluding 'Topic' to avoid duplicate with title)
    topic_keys = ['Topics', 'Research topics', 'Themes', 'Call', 'Destination']
    info['topics'] = _extract_first_valid(data, topic_keys)
    
    # Description variations
    desc_keys = ['Description', 'Call description', 'Topic description', 'Summary', 'Expected Outcome']
    info['description'] = _extract_first_valid(data, desc_keys)
    
    # Expected outcomes variations
    outcome_keys = ['Expected outcomes', 'Outcomes', 'Expected impacts', 'Specific challenge']
    info['expected_outcomes'] = _extract_first_valid(data, outcome_keys)
    
    # Scope variations
    scope_keys = ['Scope', 'Call scope', 'Topic scope']
    info['scope'] = _extract_first_valid(data, scope_keys)
    
    # URL variations
    url_keys = ['URL', 'Link', 'Web link', 'Call URL']
    info['url'] = _extract_first_valid(data, url_keys)
    
    return info


def _extract_first_valid(data: Dict, keys: list) -> str:
    """Extract first valid value from data using list of possible keys"""
    for key in keys:
        if key in data and pd.notna(data[key]):
            return str(data[key])
    return None
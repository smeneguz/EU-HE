"""Export utilities"""

import pandas as pd
import json
from typing import List
from core.models import ProjectMatch
from .project_info import extract_project_info


def export_to_csv(matches: List[ProjectMatch]) -> bytes:
    """Export matches to CSV with detailed information"""
    export_data = []
    
    for match in matches:
        info = extract_project_info(match)
        row = {
            'excel_row': match.row_index,
            'sheet_name': match.sheet_name,
            'score': match.score,
            'priority': match.priority_level,
            'title': info['title'] or match.get_project_title(),
            'call_id': info['call_id'],
            'opening_date': info['opening_date'],
            'deadline': info['deadline'],
            'budget': info['budget'],
            'partners': info['partners'],
            'coordinator': info['coordinator'],
            'type_of_action': info['type_of_action'],
            'technologies': ', '.join(match.technologies),
            'potential_roles': ', '.join(match.potential_roles),
            'matched_keywords': str(match.matched_keywords),
            'contributions': ', '.join(match.contributions),
            'url': info['url']
        }
        export_data.append(row)
    
    df = pd.DataFrame(export_data)
    return df.to_csv(index=False).encode('utf-8')


def export_to_json(matches: List[ProjectMatch]) -> str:
    """Export matches to JSON with detailed information"""
    export_data = []
    
    for match in matches:
        info = extract_project_info(match)
        data = match.to_dict()
        data['excel_row'] = match.row_index
        data['detailed_info'] = info
        export_data.append(data)
    
    return json.dumps(export_data, indent=2)
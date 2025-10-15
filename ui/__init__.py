"""UI components package"""

from .statistics import display_statistics
from .project_card import display_match_card
from .pagination import display_pagination, get_paginated_items
from .filters import display_filters

__all__ = [
    'display_statistics',
    'display_match_card',
    'display_pagination',
    'get_paginated_items',
    'display_filters'
]
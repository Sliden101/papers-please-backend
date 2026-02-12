"""
Scraper package for papers please
"""

from .subjects_scraper import (
    scrape_arxiv_subjects_hierarchy    

)

__all__ = [
    'scrape_arxiv_subjects_hierarchy'
]

__version__ = "1.0.0"

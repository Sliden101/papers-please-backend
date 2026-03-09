"""
Scraper package for papers please
"""

from .subjects_scraper import (
    scrape_arxiv_subjects_hierarchy    

)

from .paper_scraper import (
     ArxivScraper
)

__all__ = [
    'scrape_arxiv_subjects_hierarchy',
    'ArxivScraper'
]

__version__ = "1.0.0"

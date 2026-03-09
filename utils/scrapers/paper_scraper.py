from typing import Dict, List, Tuple, Optional

import requests
import re
from bs4 import BeautifulSoup

from db import PaperStatus

class ArxivScraper:
    """Ingests paper metadata from arXiv"""
    
    BASE_URL = "https://arxiv.org/abs/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_paper(self, arxiv_id: str) -> Optional[Dict[str, any]]:
        """
        Fetch paper metadata from arXiv by ID
        Example: 2602.15763
        """

        try:
            arxiv_id = self._clean_arxiv_id(arxiv_id)
            
            url = f"{self.BASE_URL}{arxiv_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            paper_data = {
                'arxiv_id': arxiv_id,
                'title': self._extract_title(soup),
                'authors': self._extract_authors(soup),
                'abstract': self._extract_abstract(soup),
                'subjects': self._extract_subjects(soup),
                'doi': self._extract_doi(soup),
                'published_date': self._extract_date(soup)
            }
            
            return paper_data

        except requests.RequestException as e:
            print(f"Network error fetching {arxiv_id}: {e}")
            return None
        except Exception as e:
            print(f"Error parsing {arxiv_id}: {e}")
            return None

    def _clean_arxiv_id(self, arxiv_id: str) -> str:
        """Remove version number and cleans ID"""
        return re.sub(r'v\d+$', '', arxiv_id.strip())
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract paper title"""
        title_tag = soup.find('h1', class_ = 'title mathjax')
        if title_tag:
            title = title_tag.text.replace('Title:', '').strip()
            return title
        return "Unknown Title"
    
    def _extract_authors(self, soup: BeautifulSoup) -> List[str]:
        """Extract list of authors"""
        authors_div = soup.find('div', class_='authors')
        if authors_div:
            author_links = authors_div.find_all('a')
            authors = []
            for a in author_links:
                # who is this et al guy lol /j
                if a.get('id') == 'toggle':
                    continue

                author_name = a.text.strip()
                if author_name and not author_name.startswith('et al.'): # holy retard hack 
                    authors.append(author_name)

            long_list = soup.find('div', id='long-author-list')
            if long_list:
                hidden_authors = long_list.find_all('a')
                for a in hidden_authors:
                    author_name = a.text.strip()
                    if author_name:
                        authors.append(author_name)

            return authors if authors else ["Unknown Author"]
        return ["Unknown Author"]

    def _extract_abstract(self, soup: BeautifulSoup) -> str:
        """Extract paper abstract"""
        abstract_block = soup.find('blockq')

        abstract_block = soup.find('blockquote', class_='abstract mathjax')
        if abstract_block:
            # Remove 'Abstract:' prefix and clean
            abstract = abstract_block.text.replace('Abstract:', '').strip()
            return abstract
        return ""
    def _extract_subjects(self, soup: BeautifulSoup) -> List[Tuple[str, str]]:
        """
        Extract subject categories
        Returns list of (subject_name, shorthand) tuples
        """
        subjects = []
        
        subjects_cell = soup.find('td', class_='tablecell subjects')
        
        if subjects_cell:
            #primary subjects
            primary_span = subjects_cell.find('span', class_='primary-subject')
            if primary_span:
                primary_text = primary_span.text.strip()
                match = re.match(r'(.+?)\s*\((.+?)\)', primary_text)
                if match:
                    full_name = match.group(1).strip()
                    shorthand = match.group(2).strip()
                    subjects.append((full_name, shorthand))
            
            remaining_text = subjects_cell.get_text()
            if primary_span:
                remaining_text = remaining_text.replace(primary_span.text, '', 1)
            
            if ';' in remaining_text:
                parts = remaining_text.split(';')
                for part in parts:
                    part = part.strip()
                    if part:
                        match = re.match(r'(.+?)\s*\((.+?)\)', part)
                        if match:
                            full_name = match.group(1).strip()
                            shorthand = match.group(2).strip()
                            subjects.append((full_name, shorthand))
        
        return subjects

    def _extract_doi(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract DOI"""
        doi_row = soup.find('td', class_='tablecell arxivdoi')
        if doi_row:
            doi_link = doi_row.find('a', id='arxiv-doi-link')
            if doi_link:
                return doi_link.text.strip()
        return None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract submission date"""
        dateline = soup.find('div', class_='dateline')
        if dateline:
            date_text = dateline.text
            match = re.search(r'\[Submitted on (\d{1,2} \w+ \d{4})', date_text)
            if match:
                return match.group(1)
        return None

class Paper():
    arxiv_id: str
    title: str
    abstract: str
    doi: str
    status: PaperStatus

    def __init__(self, arxiv_id: str, title: str, abstract: str, doi: str, status: PaperStatus):
        self.arxiv_id = arxiv_id
        self.title = title
        self.abstract = abstract
        self.doi = doi

    

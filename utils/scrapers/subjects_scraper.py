import requests
import json
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Tuple

## Subject Scraper

def scrape_arxiv_subjects_hierarchy() -> Dict[str, Dict[str, List[Tuple[str, str]]]]:
    """
    Creates a dictw where:
    - Keys are main subjects (eg: 'Physics', 'Math', 'Computer Science')
    - Values are dictionaries with:
      - 'subjects': list of main subject areas
      - 'categories': nested dictionary of categories under each subject``
    """

    url = "https://arxiv.org"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    result = {}
    
    for h2 in soup.find_all('h2'):
        main_category = h2.get_text().strip()
        
        if main_category in ["quick links", "About arXiv", "Secondary"]:
            continue
        result[main_category] = {}
        
        ul = None
        sibling = h2.find_next_sibling()
        
        while sibling and sibling.name != 'ul':
            sibling = sibling.find_next_sibling()
        
        if sibling and sibling.name == 'ul':
            ul = sibling
            
        if ul:
            for li in ul.find_all('li'):
                main_link = li.find('a', id=lambda x: x and x.startswith('main-'))
                
                if main_link:
                    subject_name = main_link.get_text().strip()
                    result[main_category][subject_name] = []
                    
                    strong_tag = li.find('strong')
                    main_shorthand = strong_tag.get_text().strip() if strong_tag else subject_name
                    
                    # find all category links
                    for link in li.find_all('a'):
                        link_text = link.get_text().strip()
                        link_href = link.get('href', '')
                        
                        # Skip:
                        # - It's the main link itself
                        # - It's empty
                        # - It's a control link
                        if (link is main_link or 
                            not link_text or 
                            link_text.lower() in ['new', 'recent', 'search']):
                            continue
                        
                        if 'detailed' in link_text.lower():
                            continue
                        
                        # Extract shorthand from href
                        shorthand = extract_shorthand(link_href)
                        
                        # Add to categories list if not already there
                        if link_text not in [cat[0] for cat in result[main_category][subject_name]]:
                            result[main_category][subject_name].append((link_text, shorthand)) 

    return result

def extract_shorthand(href: str) -> str:
    """
    Extract shorthand code from href, id or text
    """
    if '/list/' in href:
        # Pattern: /list/cs.NI/recent
        parts = href.split('/')
        if len(parts) > 2:
            return parts[2]    

def print_hierarchy(hierarchy: Dict[str, Dict[str, List[str]]]):
    """Print examples of the hierarchy"""
    print("arXiv Subjects Hierarchy (with shorthand codes)")
    print("=" * 70)
    
    for main_category, subjects_dict in hierarchy.items():
        print(f"\n{main_category}")
        print("-" * 40)
        
        for subject_name, categories in subjects_dict.items():
            print(f"  • {subject_name}")
            
            if categories:
                for category_name, shorthand in categories:
                    print(f"      - {category_name} ({shorthand})")
                print(f"    Total categories: {len(categories)}")
            else:
                print(f"    (No sub-categories)")
            print()





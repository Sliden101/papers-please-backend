import requests
from utils.scrapers import ArxivScraper
from db import Paper as DBPaper, Author, Subject, PaperStatus, engine, PaperAuthorLink, PaperSubjectLink
from sqlmodel import Session

class PaperManager():
    """Manages adding papers to the database"""

    def __init__(self):
        self.scraper = ArxivScraper()

    def add_paper(self, arxiv_id: str, status: PaperStatus = PaperStatus.UNREAD) -> bool:
        """
        Scrape and add a paper to the database
        """
        
        paper_data = self.scraper.fetch_paper(arxiv_id)
        
        if not paper_data:
            print(f"Failed to fetch paper {arxiv_id}")
            return False

        try:
            with Session(engine) as session:
                existing = session.get(DBPaper, arxiv_id)
                if existing:
                    print(f"Paper {arxiv_id} already exists in this database")
                    return False    
            
                db_paper = DBPaper(
                    id=paper_data['arxiv_id'],
                    title=paper_data['title'],
                    abstract=paper_data['abstract'],
                    doi=paper_data['doi'],
                    status=status
                )

                session.add(db_paper)
                session.commit()
    
                #imagine this paper has like 200 authors or something........
                # no way right........
                unique_author_names = set()
                for author_name in paper_data['authors']:
                    if author_name in unique_author_names:
                        continue
                    unique_author_names.add(author_name)

                    author = session.get(Author, author_name)
                    if not author:
                        author = Author(name=author_name)
                        session.add(author)
                        session.flush()

                    link = PaperAuthorLink(paper_id=db_paper.id, author_name=author.name)
                    session.add(link)
                    
                session.commit()

                for subject_name, shorthand in paper_data['subjects']:
                    subject = session.get(Subject, subject_name)
                    if subject:
                        link = PaperSubjectLink(paper_id=db_paper.id, subject_name=subject.name)
                        session.add(link)
                    else:
                        print(f"Note: Subject '{subject_name}' ({shorthand}) not found in database")
                
                session.commit()
                return True

        except requests.RequestException as e:
            print(f"Network error fetching {arxiv_id}: {e}")
            return False
            
        except Exception as e:
            print(f"Unexpected error adding {arxiv_id}: {e}")
            if session:
                session.rollback()
            return False
            
        finally:
            if session:
                session.close()
                print(f"Database connection closed for {arxiv_id}")
    
    def add_papers_batch(self, arxiv_ids: list, status: PaperStatus = PaperStatus.UNREAD) -> dict:
        results = {}
        successful = 0
        failed = 0
        
        for i, arxiv_id in enumerate(arxiv_ids, 1):
            print(f"\n[{i}/{len(arxiv_ids)}] {'='*40}") # retard maxxing progress bar
        
            success = self.add_paper(arxiv_id, status)
            results[arxiv_id] = success
        
            if success:
                successful += 1
            else:
                failed += 1

        return results

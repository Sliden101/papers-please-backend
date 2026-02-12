from db import create_db_and_tables, Paper, Author, Subject, DatabaseManager
from utils.scrapers import scrape_arxiv_subjects_hierarchy

res = scrape_arxiv_subjects_hierarchy()

db_manager = DatabaseManager()

db_manager.add_subjects_hierarchy(res)


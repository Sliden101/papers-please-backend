"""
Database package for papers please
"""

from .db import (
    create_db_and_tables,
    create_db_session,

    #Db schemas
    Paper,
    Author,
    Subject,
    MainSubject,

    #Link schemas
    PaperAuthorLink,
    PaperSubjectLink,
    SubjectMainSubjectLink,
    SubjectParentLink,

    
    # Database engine
    engine,
)

from .manager import (
    DatabaseManager,
)

__all__ = [
    'create_db_and_tables',
    'create_db_session',
    'DatabaseManager',
    'Paper',
    'Author',
    'Subject',
    'MainSubject',
    'PaperAuthorLink',
    'PaperSubjectLink',
    'SubjectMainSubjectLink',
    'SubjectParentLink',
    'engine',
]

__version__ = '1.0.0'

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
    # Sessio
    engine,

    #Enums
    PaperStatus,
)

from .subject_manager import (
    SubjectManager,
)

from .paper_manager import (
    PaperManager,
)
__all__ = [
    'create_db_and_tables',
    'create_db_session',
    'SubjectManager',
    'PaperManager'
    'Paper',
    'Author',
    'Subject',
    'MainSubject',
    'PaperAuthorLink',
    'PaperSubjectLink',
    'SubjectMainSubjectLink',
    'SubjectParentLink',
    'engine',
    'PaperStatus',
]

__version__ = '1.0.2'

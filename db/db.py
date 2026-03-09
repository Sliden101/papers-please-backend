import enum
from typing import Optional, List
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, Enum, Column
from sqlalchemy.types import String

#Link Tables

class PaperAuthorLink(SQLModel, table=True):
    paper_id: Optional[str]= Field(default=None, foreign_key="paper.id", primary_key=True)
    author_name: Optional[str] = Field(default=None, foreign_key="author.name", primary_key=True)

class PaperSubjectLink(SQLModel, table=True):
    paper_id: Optional[str] = Field(default=None, foreign_key="paper.id", primary_key=True)
    subject_name: Optional[str] = Field(default=None, foreign_key="subject.name", primary_key=True)

class SubjectMainSubjectLink(SQLModel, table=True):
    subject_name: Optional[str] = Field(default=None, foreign_key="subject.name", primary_key=True)
    main_subject_name: Optional[str] = Field(
        default=None, 
        foreign_key="mainsubject.name", 
        primary_key=True
    )

class SubjectParentLink(SQLModel, table=True):
    subject_name: Optional[str] = Field(default=None, foreign_key="subject.name", primary_key=True)
    parent_subject_name: Optional[str] = Field(
        default=None,
        foreign_key="subject.name",
        primary_key=True
    )

# Main Tables
class MainSubject(SQLModel, table=True):
    __tablename__ = "mainsubject"
    name: Optional[str] = Field(default=None, primary_key=True)
    subjects: List["Subject"] = Relationship(back_populates="main_subjects", link_model=SubjectMainSubjectLink)

class Subject(SQLModel, table=True):
    __tablename__ = "subject"
    name: Optional[str] = Field(default=None, primary_key=True)
    shorthand: str = Field(default="", index=True)
    level: int = Field(default=0)

    main_subjects: List["MainSubject"] = Relationship(back_populates="subjects", link_model=SubjectMainSubjectLink) 
    papers: List["Paper"] = Relationship(back_populates="subjects", link_model=PaperSubjectLink)
 
    #self referential Hierarchy
    parents: List["Subject"] = Relationship(
        back_populates="children",
        link_model=SubjectParentLink,
        sa_relationship_kwargs={
            "primaryjoin": "Subject.name == SubjectParentLink.subject_name",
            "secondaryjoin": "Subject.name == SubjectParentLink.parent_subject_name"
        }
    )
   
    children: List["Subject"] = Relationship(
        back_populates="parents",
        link_model=SubjectParentLink,
        sa_relationship_kwargs={
            "primaryjoin": "Subject.name == SubjectParentLink.parent_subject_name",
            "secondaryjoin": "Subject.name == SubjectParentLink.subject_name"
        }
    )

class Author(SQLModel, table=True):
    __tablename__ = "author"
    name: Optional[str] = Field(default=None, primary_key=True)
    papers: List["Paper"] = Relationship(back_populates="authors", link_model=PaperAuthorLink)

class PaperStatus(str, enum.Enum): #Python built in Enum "type"
    READING = "reading"
    UNREAD = "unread"
    COMPLETED = "completed"

class Paper(SQLModel, table=True):
    __tablename__ = "paper"
    id: Optional[str] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    abstract: str = Field(default=None)
    doi: str = Field(default=None)
    status: PaperStatus = Field(
        sa_column=Column(
                index=True,
                name="status",
                nullable=False,
                type_ = Enum(PaperStatus),
        )
    )
    note: Optional[str] = Field(default = None,sa_column=Column(String, nullable=True))
    authors: List["Author"] = Relationship(back_populates="papers", link_model=PaperAuthorLink)
    subjects: List["Subject"] = Relationship(back_populates="papers", link_model=PaperSubjectLink)
    
# Database connection

SQLITE_FILE_NAME = "db/database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

connect_args = {"check_same_thread": False}
engine = create_engine(
        SQLITE_URL, 
        echo=True, 
        connect_args=connect_args,
        pool_pre_ping=True
    )

def create_db_and_tables() -> bool:
    """Create all database tables"""
    try:
        SQLModel.metadata.drop_all(engine)
        SQLModel.metadata.create_all(engine)
        return True
    except Exception as e:
        print(f"Exception raised {e}")
        return False

def create_db_session():
    """Gets a database session"""
    try:
        return Session(engine) 
    except Exception as e:
        print(f"Exception raised {e}")

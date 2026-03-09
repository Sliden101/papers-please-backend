from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import logging

from db import create_db_and_tables, Paper as DBPaper, Author, Subject, PaperStatus, engine
from db import PaperAuthorLink, PaperSubjectLink, PaperManager
from sqlmodel import Session, select
from sqlalchemy import func

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

paper_manager = PaperManager()

#Pydantic Models
class PaperAddRequest(BaseModel):
    arxiv_id: str = Field(..., description="arXiv ID of the paper (e.g., 2106.09685)")
    status: PaperStatus = Field(default=PaperStatus.UNREAD, description="Reading status")

class PaperResponse(BaseModel):
    id: str
    title: str
    abstract: Optional[str] = None
    doi: Optional[str] = None
    status: PaperStatus
    note: Optional[str] = None
    authors: List[str] = []
    subjects: List[str] = []

class PaperDetailResponse(PaperResponse):
    author_count: int
    subject_count: int

class PaperUpdateRequest(BaseModel):
    status: Optional[PaperStatus] = None
    note: Optional[str] = None

class StatsResponse(BaseModel):
    total_papers: int
    papers_by_status: Dict[str, int]
    top_authors: List[Dict[str, Any]]
    top_subjects: List[Dict[str, Any]] 
    recent_papers: List[Dict[str, Any]]

#API Endpoints
@router.get("/")
def read_root():
    return {
        "message": "Papers Please API",
        "version": "1.0.0",
        "endpoints": [
            "/v1/add_paper - Add a single paper",
            "/v1/papers - List all papers",
            "/v1/papers/{paper_id} - Get paper details",
            "/v1/papers/{paper_id} - Update paper (PUT)",
            "/v1/papers/{paper_id} - Delete paper (DELETE)",
            "/v1/search - Search papers",
            "/v1/stats - Get library statistics",
            "/v1/authors - List all authors",
            "/v1/subjects - List all subjects"
        ]
    }

@router.post("/v1/add_paper")
async def add_paper(request: PaperAddRequest):
    """Add a single paper"""
    try:

        with Session(engine) as session:
            existing = session.get(DBPaper, request.arxiv_id)
            if existing:
                authors = [a.name for a in existing.authors]
                subjects = [s.name for s in existing.subjects]
                
                raise HTTPException(
                    status_code=409,
                    detail={
                        "message": f"Paper {request.arxiv_id} already exists",
                        "paper": PaperResponse(
                            id=existing.id,
                            title=existing.title,
                            abstract=existing.abstract,
                            doi=existing.doi,
                            status=existing.status,
                            note=existing.note,
                            authors=authors,
                            subjects=subjects
                        ).dict()
                    }
                )

        success = paper_manager.add_paper(request.arxiv_id, request.status)

        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to add paper {request.arxiv_id}"
            )

        with Session(engine) as session:
            paper = session.get(DBPaper, request.arxiv_id)
            if not paper:
                raise HTTPException(
                    status_code=404,
                    detail=f"Paper {request.arxiv_id} not found after adding"
                )
            authors = [a.name for a in paper.authors]
            subjects = [s.name for s in paper.subjects]
            
            return PaperResponse(
                id=paper.id,
                title=paper.title,
                abstract=paper.abstract,
                doi=paper.doi,
                status=paper.status,
                note=paper.note,
                authors=authors,
                subjects=subjects
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding paper {request.arxiv_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/v1/papers", response_model=List[PaperResponse])
async def list_papers(
    skip: int = Query(0, description="Number of papers to skip"),
    limit: int = Query(100, description="Number of papers to return"),
    status: Optional[PaperStatus] = Query(None, description="Filter by status")
):
    """
    List all papers with pagination
    """
    with Session(engine) as session:
        query = select(DBPaper)

        if status:
            query = query.where(DBPaper.status == status)

        query = query.offset(skip).limit(limit)
        papers = session.exec(query).all()

        result = []
        for paper in papers:
            result.append(PaperResponse(
                id=paper.id,
                title=paper.title,
                abstract=paper.abstract,
                doi=paper.doi,
                status=paper.status,
                note=paper.note,
                authors=[a.name for a in paper.authors],
                subjects=[s.name for s in paper.subjects]
            ))
        
        return result

@router.get("/v1/papers/{paper_id}", response_model=PaperDetailResponse)
async def get_paper(paper_id: str):
    """
    Get information about a specific paper.
    """
    with Session(engine) as session:
        paper = session.get(DBPaper, paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")

        authors = [a.name for a in paper.authors]
        subjects = [s.name for s in paper.subjects]
        
        return PaperDetailResponse(
            id=paper.id,
            title=paper.title,
            abstract=paper.abstract,
            doi=paper.doi,
            status=paper.status,
            note=paper.note,
            authors=authors,
            subjects=subjects,
            author_count=len(authors),
            subject_count=len(subjects)
        )

@router.put("/v1/papers/{paper_id}")
async def update_paper(paper_id: str, update: PaperUpdateRequest):
    """
    Update a paper's status or notes.
    """
    with Session(engine) as session:
        paper = session.get(DBPaper, paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        if update.status:
            paper.status = update.status
        if update.note is not None:
            paper.note = update.note
        
        session.add(paper)
        session.commit()
        
        return {"message": f"Paper {paper_id} updated successfully"}

@router.delete("/v1/papers/{paper_id}")
async def delete_paper(paper_id: str):
    """
    Delete a paper.
    """
    with Session(engine) as session:
        paper = session.get(DBPaper, paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        session.delete(paper)
        session.commit()
        
        return {"message": f"Paper {paper_id} deleted successfully"}

@router.get("/v1/search")
async def search_papers(
    q: str = Query(..., description="Search query"),
    author: Optional[str] = Query(None, description="Filter by author"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    status: Optional[PaperStatus] = Query(None, description="Filter by status")
):
    """Search papers by title, abstract, or author"""
    with Session(engine) as session:
        query = select(DBPaper)
        
        if q:
            query = query.where(
                (DBPaper.title.contains(q)) |
                (DBPaper.abstract.contains(q))
            )

        if author:
            query = query.join(PaperAuthorLink).join(Author).where(
                Author.name.contains(author)
            )

        if subject:
            query = query.join(PaperSubjectLink).join(Subject).where(
                Subject.name.contains(subject)
            )

        if status:
            query = query.where(DBPaper.status == status)
    
        papers = session.exec(query).all()
        
        results = []
        for paper in papers:
            results.append({
                "id": paper.id,
                "title": paper.title,
                "status": paper.status,
                "authors": [a.name for a in paper.authors],
                "subjects": [s.name for s in paper.subjects]
            })
        
        return {
            "query": q,
            "count": len(results),
            "results": results
        }


@router.get("/v1/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get library statistics.
    """
    with Session(engine) as session:
        total_papers = session.exec(select(func.count()).select_from(DBPaper)).one()
        
        status_counts = {}
        for status in PaperStatus:
            count = session.exec(
                select(func.count()).where(DBPaper.status == status)
            ).one()
            status_counts[status.value] = count
        
        top_authors_query = (
            select(Author.name, func.count(PaperAuthorLink.paper_id).label("paper_count"))
            .join(PaperAuthorLink)
            .group_by(Author.name)
            .order_by(func.count(PaperAuthorLink.paper_id).desc())
            .limit(10)
        )
        top_authors = [
            {"name": name, "paper_count": count}
            for name, count in session.exec(top_authors_query)
        ]
        
        top_subjects_query = (
            select(Subject.name, func.count(PaperSubjectLink.paper_id).label("paper_count"))
            .join(PaperSubjectLink)
            .group_by(Subject.name)
            .order_by(func.count(PaperSubjectLink.paper_id).desc())
            .limit(10)
        )
        top_subjects = [
            {"name": name, "paper_count": count}
            for name, count in session.exec(top_subjects_query)
        ]
        
        recent_query = (
            select(DBPaper)
            .order_by(DBPaper.id.desc())
            .limit(5)
        )
        recent_papers = [
            {"id": p.id, "title": p.title, "status": p.status}
            for p in session.exec(recent_query)
        ]
        
        return StatsResponse(
            total_papers=total_papers,
            papers_by_status=status_counts,
            top_authors=top_authors,
            top_subjects=top_subjects,
            recent_papers=recent_papers
        )


@router.get("/v1/authors")
async def list_authors(
    skip: int = Query(0, description="Number of authors to skip"),
    limit: int = Query(50, description="Maximum number of authors to return")
):
    """
    List all authors with their paper counts.
    """
    with Session(engine) as session:
        query = (
            select(Author.name, func.count(PaperAuthorLink.paper_id).label("paper_count"))
            .outerjoin(PaperAuthorLink)
            .group_by(Author.name)
            .order_by(Author.name)
            .offset(skip)
            .limit(limit)
        )
        
        authors = [
            {"name": name, "paper_count": count}
            for name, count in session.exec(query)
        ]
        
        return {
            "total": len(authors),
            "authors": authors
        }

@router.get("/v1/subjects")
async def list_subjects(
    skip: int = Query(0, description="Number of subjects to skip"),
    limit: int = Query(50, description="Maximum number of subjects to return")
):
    """
    List all subjects with their paper counts.
    """
    with Session(engine) as session:
        query = (
            select(Subject.name, Subject.shorthand, func.count(PaperSubjectLink.paper_id).label("paper_count"))
            .outerjoin(PaperSubjectLink)
            .group_by(Subject.name, Subject.shorthand)
            .order_by(Subject.name)
            .offset(skip)
            .limit(limit)
        )
        
        subjects = [
            {"name": name, "shorthand": shorthand, "paper_count": count}
            for name, shorthand, count in session.exec(query)
        ]
        
        return {
            "total": len(subjects),
            "subjects": subjects
        }


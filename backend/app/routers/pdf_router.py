from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.pdf_service import PDFService
from app.schemas.pdf import PDFResponse, PDFListResponse, PDFDetailResponse
from app.schemas.pdf_chunk import (
    PDFChunkResponse,
    PDFChunkListResponse,
    PDFChunkSearchResponse,
)
from app.routers.user_router import get_current_user

router = APIRouter(prefix="/api/pdfs", tags=["pdfs"])


@router.post("/upload", response_model=PDFResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    title: Optional[str] = Query(None, description="PDF title"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        pdf_service = PDFService(db)
        pdf = await pdf_service.upload_and_parse_pdf(file, title)
        return PDFResponse.model_validate(pdf)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


@router.get("/", response_model=PDFListResponse)
def get_pdfs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        pdf_service = PDFService(db)
        pdfs = pdf_service.get_pdf_list(skip=skip, limit=limit)

        # Get total count for pagination
        total = pdf_service.pdf_repo.count()

        return PDFListResponse(
            items=[PDFResponse.model_validate(pdf) for pdf in pdfs],
            total=total,
            page=skip // limit + 1,
            size=limit,
            pages=(total + limit - 1) // limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve PDFs: {str(e)}"
        )


@router.get("/{pdf_id}", response_model=PDFDetailResponse)
def get_pdf_detail(
    pdf_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    try:
        pdf_service = PDFService(db)
        pdf = pdf_service.get_pdf_detail(pdf_id)

        if not pdf:
            raise HTTPException(status_code=404, detail="PDF not found")

        # Convert chunks to response format
        chunks = [PDFChunkResponse.model_validate(chunk) for chunk in pdf.chunks]

        pdf_response = PDFDetailResponse.model_validate(pdf)
        pdf_response.chunks = chunks

        return pdf_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve PDF: {str(e)}")


@router.get("/{pdf_id}/chunks", response_model=PDFChunkListResponse)
def get_pdf_chunks(
    pdf_id: int,
    skip: int = Query(0, ge=0, description="Number of chunks to skip"),
    limit: int = Query(20, ge=1, le=50, description="Number of chunks to return"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        pdf_service = PDFService(db)

        if not pdf_service.pdf_repo.exists(pdf_id):
            raise HTTPException(status_code=404, detail="PDF not found")

        chunks = pdf_service.get_pdf_chunks(pdf_id, skip=skip, limit=limit)
        total = pdf_service.chunk_repo.count_by_pdf(pdf_id)

        return PDFChunkListResponse(
            items=[PDFChunkResponse.model_validate(chunk) for chunk in chunks],
            total=total,
            page=skip // limit + 1,
            size=limit,
            pages=(total + limit - 1) // limit,
            pdf_id=pdf_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve chunks: {str(e)}"
        )


@router.get("/search/content", response_model=PDFChunkSearchResponse)
def search_pdf_content(
    q: str = Query(..., min_length=1, description="Search query"),
    pdf_id: Optional[int] = Query(None, description="Search within specific PDF"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(20, ge=1, le=50, description="Number of results to return"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        pdf_service = PDFService(db)

        if pdf_id and not pdf_service.pdf_repo.exists(pdf_id):
            raise HTTPException(status_code=404, detail="PDF not found")

        # Get search results and count
        chunks = pdf_service.search_pdf_content(q, pdf_id, skip=skip, limit=limit)
        total = pdf_service.count_search_results(q, pdf_id)

        # Calculate pagination
        page = skip // limit + 1
        pages = (total + limit - 1) // limit if total > 0 else 0

        return PDFChunkSearchResponse(
            items=[PDFChunkResponse.model_validate(chunk) for chunk in chunks],
            total=total,
            page=page,
            size=limit,
            pages=pages,
            query=q,
            pdf_id=pdf_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.delete("/{pdf_id}")
def delete_pdf(
    pdf_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete a PDF and its chunks."""
    try:
        pdf_service = PDFService(db)

        if not pdf_service.delete_pdf(pdf_id):
            raise HTTPException(status_code=404, detail="PDF not found")

        return {"message": "PDF deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete PDF: {str(e)}")

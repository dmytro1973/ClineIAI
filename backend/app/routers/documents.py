from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID, uuid4

router = APIRouter(prefix="/api/documents", tags=["Documents"])

class Document(BaseModel):
    id: UUID
    name: str
    content: str
    created_at: str
    updated_at: str

class DocumentCreate(BaseModel):
    name: str
    content: str

# Mock database
documents_db = {
    UUID("123e4567-e89b-12d3-a456-426614174000"): Document(
        id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        name="Patient Report",
        content="Detailed patient medical report...",
        created_at="2023-12-15T10:00:00Z",
        updated_at="2023-12-15T10:00:00Z"
    )
}

@router.get("/", response_model=List[Document])
async def get_documents():
    return list(documents_db.values())

@router.post("/", response_model=Document)
async def create_document(doc: DocumentCreate):
    new_id = uuid4()
    new_doc = Document(
        id=new_id,
        name=doc.name,
        content=doc.content,
        created_at="2023-12-16T18:00:00Z",
        updated_at="2023-12-16T18:00:00Z"
    )
    documents_db[new_id] = new_doc
    return new_doc

@router.get("/{document_id}", response_model=Document)
async def get_document(document_id: UUID):
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    return documents_db[document_id]

@router.delete("/{document_id}", response_model=dict)
async def delete_document(document_id: UUID):
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    del documents_db[document_id]
    return {"message": "Document deleted successfully"}

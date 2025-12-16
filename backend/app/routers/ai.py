from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from ..services.ai_service import ai_service

router = APIRouter(prefix="/api/ai", tags=["AI"])

class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4"

class ChatResponse(BaseModel):
    response: str
    model: str

class DocumentAnalysisRequest(BaseModel):
    document_text: str
    analysis_type: str = "full"

class DocumentAnalysisResponse(BaseModel):
    analysis: Dict[str, Any]
    summary: str

class DiagnosisRequest(BaseModel):
    symptoms: str
    patient_history: str = ""

class DiagnosisResponse(BaseModel):
    possible_conditions: List[str]
    recommended_actions: List[str]
    confidence: str
    medical_concepts: List[Dict[str, Any]]

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat mit KI für medizinische Fragen"""
    try:
        response = await ai_service.chat_with_ai(request.message, request.model)
        return {
            "response": response,
            "model": request.model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(request: DocumentAnalysisRequest):
    """Dokumentenanalyse mit OCR und NLP"""
    try:
        analysis = ai_service.analyze_document_with_ocr(request.document_text)
        return {
            "analysis": analysis,
            "summary": analysis["summary"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis error: {str(e)}")

@router.post("/diagnose", response_model=DiagnosisResponse)
async def get_diagnosis(request: DiagnosisRequest):
    """KI-gestützte Diagnosevorschläge"""
    try:
        diagnosis = ai_service.get_diagnosis_suggestions(request.symptoms)
        medical_concepts = ai_service.get_medical_concepts(request.symptoms + " " + request.patient_history)

        return {
            "possible_conditions": diagnosis["possible_conditions"],
            "recommended_actions": diagnosis["recommended_actions"],
            "confidence": diagnosis["confidence"],
            "medical_concepts": [concept.dict() for concept in medical_concepts]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnosis service error: {str(e)}")

@router.get("/models", response_model=List[str])
async def get_models():
    """Verfügbare KI-Modelle"""
    return ["gpt-4", "claude-3", "llama-2", "mistral-7b", "medical-ai"]

@router.get("/medical-concepts", response_model=List[Dict[str, Any]])
async def get_medical_concepts(text: str):
    """Extrahiert medizinische Konzepte aus Text"""
    try:
        concepts = ai_service.get_medical_concepts(text)
        return [concept.dict() for concept in concepts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Medical concept extraction error: {str(e)}")

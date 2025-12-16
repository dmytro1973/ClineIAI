import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

# Medizinische Ontologien (vereinfacht)
SNOMED_CT = {
    "248152002": {"term": "Asthma", "definition": "Chronic respiratory disease"},
    "386661006": {"term": "Diabetes mellitus", "definition": "Metabolic disorder"},
    "195967001": {"term": "Hypertension", "definition": "High blood pressure"},
    "233604007": {"term": "Pneumonia", "definition": "Lung inflammation"},
    "274805003": {"term": "Myocardial infarction", "definition": "Heart attack"}
}

ICD_10 = {
    "J45": {"description": "Asthma", "category": "Respiratory"},
    "E11": {"description": "Type 2 diabetes mellitus", "category": "Endocrine"},
    "I10": {"description": "Essential (primary) hypertension", "category": "Circulatory"},
    "J18": {"description": "Pneumonia, unspecified", "category": "Respiratory"},
    "I21": {"description": "Acute myocardial infarction", "category": "Circulatory"}
}

class MedicalConcept(BaseModel):
    code: str
    system: str
    display: str
    definition: Optional[str] = None

class AIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "mock-api-key")
        self.base_url = "https://api.openai.com/v1"
        self.claude_url = "https://api.anthropic.com/v1"

    def get_medical_concepts(self, text: str) -> List[MedicalConcept]:
        """Extrahiert medizinische Konzepte aus Text mit SNOMED und ICD-10"""
        concepts = []

        # Einfache Textanalyse für Demo-Zwecke
        text_lower = text.lower()

        if "asthma" in text_lower:
            concepts.append(MedicalConcept(
                code="248152002",
                system="SNOMED-CT",
                display="Asthma",
                definition="Chronic respiratory disease"
            ))
            concepts.append(MedicalConcept(
                code="J45",
                system="ICD-10",
                display="Asthma",
                definition="Chronic respiratory disease"
            ))

        if "diabetes" in text_lower or "zucker" in text_lower:
            concepts.append(MedicalConcept(
                code="386661006",
                system="SNOMED-CT",
                display="Diabetes mellitus",
                definition="Metabolic disorder"
            ))
            concepts.append(MedicalConcept(
                code="E11",
                system="ICD-10",
                display="Type 2 diabetes mellitus",
                definition="Metabolic disorder"
            ))

        if "blutdruck" in text_lower or "hypertonie" in text_lower:
            concepts.append(MedicalConcept(
                code="195967001",
                system="SNOMED-CT",
                display="Hypertension",
                definition="High blood pressure"
            ))
            concepts.append(MedicalConcept(
                code="I10",
                system="ICD-10",
                display="Essential hypertension",
                definition="High blood pressure"
            ))

        return concepts

    def analyze_document_with_ocr(self, document_text: str) -> Dict[str, Any]:
        """Dokumentenanalyse mit OCR und NLP"""
        analysis = {
            "entities": [],
            "medical_concepts": [],
            "summary": "",
            "sentiment": "neutral",
            "language": "de"
        }

        # Einfache Textanalyse
        words = document_text.split()
        analysis["summary"] = f"Analyse von {len(words)} Wörtern. "

        # Medizinische Konzepte extrahieren
        medical_concepts = self.get_medical_concepts(document_text)
        analysis["medical_concepts"] = [concept.dict() for concept in medical_concepts]

        # Einfache Entitätserkennung
        if "patient" in document_text.lower():
            analysis["entities"].append("Patient")
        if "arzt" in document_text.lower() or "ärztin" in document_text.lower():
            analysis["entities"].append("Arzt")
        if "krankenhaus" in document_text.lower() or "klinik" in document_text.lower():
            analysis["entities"].append("Krankenhaus")

        # Einfache Stimmungsanalyse
        positive_words = ["gut", "besser", "erfolgreich", "gesund"]
        negative_words = ["schlecht", "schmerz", "problem", "krank"]

        pos_count = sum(1 for word in words if word.lower() in positive_words)
        neg_count = sum(1 for word in words if word.lower() in negative_words)

        if pos_count > neg_count:
            analysis["sentiment"] = "positive"
        elif neg_count > pos_count:
            analysis["sentiment"] = "negative"

        analysis["summary"] += f"Stimmung: {analysis['sentiment']}. "

        if medical_concepts:
            analysis["summary"] += f"Medizinische Konzepte gefunden: {len(medical_concepts)}."

        return analysis

    async def chat_with_ai(self, message: str, model: str = "gpt-4") -> str:
        """Chat mit KI (Echte API-Integration)"""
        # Versuchen Sie zuerst die echte API zu verwenden
        if self.api_key and self.api_key != "mock-api-key":
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                # Anpassen der API-URL basierend auf dem Modell
                api_url = self.base_url
                if model.startswith("claude"):
                    api_url = self.claude_url
                    # Für Claude API (Anthropic)
                    data = {
                        "model": model,
                        "max_tokens": 1024,
                        "messages": [{"role": "user", "content": message}]
                    }
                else:
                    # Für OpenAI API
                    data = {
                        "model": model,
                        "messages": [{"role": "user", "content": message}]
                    }

                response = requests.post(f"{api_url}/chat/completions", headers=headers, json=data)
                response.raise_for_status()
                result = response.json()

                # Unterschiedliche Antwortstrukturen handhaben
                if model.startswith("claude"):
                    return result["content"][0]["text"]
                else:
                    return result["choices"][0]["message"]["content"]

            except Exception as e:
                print(f"API-Aufruf fehlgeschlagen: {str(e)}")
                # Fallback zu Mock-Antwort bei API-Fehler
                return f"KI-Antwort (Modell: {model}): {self._generate_mock_response(message)}"
        else:
            # Mock-Antwort, wenn kein API-Schlüssel vorhanden ist
            return f"KI-Antwort (Modell: {model}): {self._generate_mock_response(message)}"

    def _generate_mock_response(self, message: str) -> str:
        """Generiert eine Mock-Antwort basierend auf der Eingabe"""
        message_lower = message.lower()

        if "diagnose" in message_lower:
            return "Basierend auf den Symptomen könnte es sich um eine Infektion handeln. Bitte konsultieren Sie einen Arzt für eine genaue Diagnose."
        elif "behandlung" in message_lower:
            return "Die Behandlung hängt von der Diagnose ab. Typische Optionen umfassen Medikamente, Physiotherapie oder chirurgische Eingriffe."
        elif "medikament" in message_lower:
            return "Ich kann keine spezifischen Medikamente empfehlen. Bitte sprechen Sie mit Ihrem Arzt über geeignete Behandlungsoptionen."
        elif "symptom" in message_lower:
            return "Bitte beschreiben Sie Ihre Symptome genauer, damit ich Ihnen besser helfen kann."
        else:
            return "Vielen Dank für Ihre Frage. Wie kann ich Ihnen bei Ihrer medizinischen Anfrage helfen?"

    def get_diagnosis_suggestions(self, symptoms: str) -> Dict[str, Any]:
        """Gibt Diagnosevorschläge basierend auf Symptomen"""
        suggestions = {
            "possible_conditions": [],
            "recommended_actions": [],
            "confidence": "low"
        }

        symptoms_lower = symptoms.lower()

        if "husten" in symptoms_lower and "fieber" in symptoms_lower:
            suggestions["possible_conditions"].append("Grippe")
            suggestions["possible_conditions"].append("Lungenentzündung")
            suggestions["recommended_actions"].append("Arzt konsultieren")
            suggestions["recommended_actions"].append("Ausreichend Flüssigkeit")
            suggestions["confidence"] = "medium"

        if "brustschmerz" in symptoms_lower:
            suggestions["possible_conditions"].append("Herzprobleme")
            suggestions["possible_conditions"].append("Sodbrennen")
            suggestions["recommended_actions"].append("Sofort Arzt aufsuchen")
            suggestions["confidence"] = "high"

        if "müdigkeit" in symptoms_lower and "durst" in symptoms_lower:
            suggestions["possible_conditions"].append("Diabetes")
            suggestions["recommended_actions"].append("Blutzucker testen")
            suggestions["confidence"] = "low"

        if not suggestions["possible_conditions"]:
            suggestions["possible_conditions"].append("Unspezifische Symptome")
            suggestions["recommended_actions"].append("Beobachtung")
            suggestions["confidence"] = "very low"

        return suggestions

# Singleton-Instanz
ai_service = AIService()

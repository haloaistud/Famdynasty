import os
import asyncio
import json
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import google.generativeai as genai
import openai
import httpx
from datetime import datetime
import pandas as pd
import numpy as np
from textblob import TextBlob
import re

# Initialize FastAPI app
app = FastAPI(title="MyFamilyDynasty AI Services", version="1.0.0")

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
APIGPT_BASE_URL = os.getenv("APIGPT_BASE_URL", "https://api.apigpt.dev/v1")
APIGPT_API_KEY = os.getenv("APIGPT_API_KEY", "")

# Configure Google Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-pro')

# Configure OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# Pydantic models
class FamilyMember(BaseModel):
    id: str
    name: str
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    birth_place: Optional[str] = None
    occupation: Optional[str] = None
    biography: Optional[str] = None
    relationships: List[Dict[str, str]] = []

class GenealogyAnalysisRequest(BaseModel):
    family_data: List[FamilyMember]
    analysis_type: str = "comprehensive"

class DocumentAnalysisRequest(BaseModel):
    document_text: str
    document_type: str = "unknown"

class NameAnalysisRequest(BaseModel):
    name: str
    origin_context: Optional[str] = None

# Google Gemini Integration
class GeminiAIService:
    @staticmethod
    async def analyze_family_history(family_data: List[FamilyMember]) -> Dict[str, Any]:
        """Analyze family history using Google Gemini"""
        if not GOOGLE_API_KEY:
            raise HTTPException(status_code=500, detail="Google API key not configured")
        
        try:
            # Prepare family data for analysis
            family_context = []
            for member in family_data:
                member_info = f"Name: {member.name}"
                if member.birth_date:
                    member_info += f", Born: {member.birth_date}"
                if member.death_date:
                    member_info += f", Died: {member.death_date}"
                if member.birth_place:
                    member_info += f", Born in: {member.birth_place}"
                if member.occupation:
                    member_info += f", Occupation: {member.occupation}"
                if member.biography:
                    member_info += f", Biography: {member.biography[:200]}..."
                family_context.append(member_info)
            
            prompt = f"""
            Analyze the following family history data and provide comprehensive insights:
            
            Family Members:
            {chr(10).join(family_context)}
            
            Please provide:
            1. Historical timeline and patterns
            2. Migration patterns and geographical analysis
            3. Occupational trends across generations
            4. Potential historical events that affected this family
            5. Cultural and social context
            6. Suggestions for further genealogical research
            7. Notable family characteristics or achievements
            
            Format the response as detailed JSON with clear sections.
            """
            
            response = await asyncio.to_thread(gemini_model.generate_content, prompt)
            
            return {
                "provider": "Google Gemini",
                "analysis": response.text,
                "timestamp": datetime.utcnow().isoformat(),
                "family_size": len(family_data)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini analysis failed: {str(e)}")

    @staticmethod
    async def analyze_document(document_text: str, doc_type: str) -> Dict[str, Any]:
        """Extract genealogical information from documents"""
        if not GOOGLE_API_KEY:
            raise HTTPException(status_code=500, detail="Google API key not configured")
            
        try:
            prompt = f"""
            Extract genealogical information from this {doc_type} document:
            
            {document_text[:2000]}
            
            Please identify and extract:
            1. Names of people mentioned
            2. Dates (birth, death, marriage, etc.)
            3. Places mentioned
            4. Relationships between people
            5. Occupations or professions
            6. Historical events referenced
            7. Family connections and lineage information
            
            Format as structured JSON with confidence scores for each extraction.
            """
            
            response = await asyncio.to_thread(gemini_model.generate_content, prompt)
            
            return {
                "provider": "Google Gemini",
                "extracted_data": response.text,
                "document_type": doc_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

# API-GPT Integration
class ApiGptService:
    @staticmethod
    async def generate_family_story(family_data: List[FamilyMember]) -> Dict[str, Any]:
        """Generate narrative family stories using API-GPT"""
        if not APIGPT_API_KEY:
            raise HTTPException(status_code=500, detail="API-GPT key not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                # Prepare family timeline
                timeline_data = []
                for member in family_data:
                    if member.birth_date:
                        timeline_data.append({
                            "name": member.name,
                            "event": "birth",
                            "date": member.birth_date,
                            "details": member.biography or ""
                        })
                
                payload = {
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional genealogist and storyteller. Create engaging family narratives based on genealogical data."
                        },
                        {
                            "role": "user",
                            "content": f"""
                            Create a compelling family story based on this genealogical data:
                            {json.dumps([member.dict() for member in family_data], indent=2)}
                            
                            Include:
                            - A narrative timeline of the family
                            - Character descriptions and relationships
                            - Historical context for the time periods
                            - Emotional connections and family dynamics
                            - Significant family achievements or challenges
                            
                            Write in an engaging, book-like format suitable for family members.
                            """
                        }
                    ],
                    "temperature": 0.8,
                    "max_tokens": 2000
                }
                
                response = await client.post(
                    f"{APIGPT_BASE_URL}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {APIGPT_API_KEY}"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "provider": "API-GPT",
                        "family_story": result["choices"][0]["message"]["content"],
                        "timestamp": datetime.utcnow().isoformat(),
                        "word_count": len(result["choices"][0]["message"]["content"].split())
                    }
                else:
                    raise HTTPException(status_code=500, detail="API-GPT request failed")
                    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")

    @staticmethod
    async def analyze_name_origins(name: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Analyze name origins and meanings"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert in etymology, genealogy, and cultural name analysis."
                        },
                        {
                            "role": "user",
                            "content": f"""
                            Analyze the name "{name}" {f"in the context of {context}" if context else ""}
                            
                            Provide:
                            1. Origin and etymology
                            2. Cultural significance
                            3. Historical usage patterns
                            4. Geographic distribution
                            5. Famous historical bearers
                            6. Variations and related names
                            7. Genealogical research tips for this name
                            
                            Format as detailed JSON.
                            """
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
                
                response = await client.post(
                    f"{APIGPT_BASE_URL}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {APIGPT_API_KEY}"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "provider": "API-GPT",
                        "name_analysis": result["choices"][0]["message"]["content"],
                        "analyzed_name": name,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Name analysis failed: {str(e)}")

# Enhanced genealogy analysis with QPython-compatible functions
class GenealogyAnalyzer:
    @staticmethod
    def analyze_family_patterns(family_data: List[FamilyMember]) -> Dict[str, Any]:
        """Analyze patterns in family data using data science techniques"""
        try:
            # Convert to DataFrame for analysis
            df_data = []
            for member in family_data:
                row = {
                    'name': member.name,
                    'birth_year': int(member.birth_date.split('-')[0]) if member.birth_date else None,
                    'death_year': int(member.death_date.split('-')[0]) if member.death_date else None,
                    'birth_place': member.birth_place,
                    'occupation': member.occupation,
                    'bio_length': len(member.biography) if member.biography else 0
                }
                if row['birth_year'] and row['death_year']:
                    row['lifespan'] = row['death_year'] - row['birth_year']
                df_data.append(row)
            
            df = pd.DataFrame(df_data)
            
            analysis_results = {
                'total_members': len(family_data),
                'time_span': {
                    'earliest_birth': df['birth_year'].min() if not df['birth_year'].isna().all() else None,
                    'latest_birth': df['birth_year'].max() if not df['birth_year'].isna().all() else None
                },
                'geographic_distribution': df['birth_place'].value_counts().to_dict() if 'birth_place' in df.columns else {},
                'occupation_trends': df['occupation'].value_counts().to_dict() if 'occupation' in df.columns else {},
                'average_lifespan': df['lifespan'].mean() if 'lifespan' in df.columns else None,
                'generation_gaps': []
            }
            
            # Calculate generation gaps
            birth_years = df['birth_year'].dropna().sort_values()
            if len(birth_years) > 1:
                gaps = birth_years.diff().dropna()
                analysis_results['generation_gaps'] = {
                    'average_gap': gaps.mean(),
                    'median_gap': gaps.median(),
                    'min_gap': gaps.min(),
                    'max_gap': gaps.max()
                }
            
            return analysis_results
            
        except Exception as e:
            return {'error': f'Pattern analysis failed: {str(e)}'}

    @staticmethod
    def extract_text_insights(text: str) -> Dict[str, Any]:
        """Extract insights from biographical text using NLP"""
        try:
            blob = TextBlob(text)
            
            # Extract potential dates
            date_pattern = r'\b\d{4}\b|\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b'
            dates = re.findall(date_pattern, text)
            
            # Extract potential places (capitalized words)
            place_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
            potential_places = re.findall(place_pattern, text)
            
            # Sentiment analysis
            sentiment = blob.sentiment
            
            return {
                'sentiment': {
                    'polarity': sentiment.polarity,
                    'subjectivity': sentiment.subjectivity
                },
                'extracted_dates': dates,
                'potential_places': list(set(potential_places)),
                'word_count': len(blob.words),
                'sentence_count': len(blob.sentences),
                'key_phrases': [str(phrase) for phrase in blob.noun_phrases][:10]
            }
            
        except Exception as e:
            return {'error': f'Text analysis failed: {str(e)}'}

# API Endpoints
@app.post("/api/ai/analyze-family")
async def analyze_family_comprehensive(request: GenealogyAnalysisRequest):
    """Comprehensive family analysis using multiple AI providers"""
    try:
        results = {}
        
        # Google Gemini analysis
        try:
            gemini_result = await GeminiAIService.analyze_family_history(request.family_data)
            results['gemini_analysis'] = gemini_result
        except Exception as e:
            results['gemini_analysis'] = {'error': str(e)}
        
        # API-GPT story generation
        try:
            apigpt_result = await ApiGptService.generate_family_story(request.family_data)
            results['family_story'] = apigpt_result
        except Exception as e:
            results['family_story'] = {'error': str(e)}
        
        # Pattern analysis
        pattern_analysis = GenealogyAnalyzer.analyze_family_patterns(request.family_data)
        results['pattern_analysis'] = pattern_analysis
        
        return {
            'status': 'success',
            'analysis_type': request.analysis_type,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/ai/analyze-document")
async def analyze_document_endpoint(request: DocumentAnalysisRequest):
    """Analyze genealogical documents"""
    try:
        # Gemini document analysis
        gemini_result = await GeminiAIService.analyze_document(
            request.document_text, 
            request.document_type
        )
        
        # Text insights
        text_insights = GenealogyAnalyzer.extract_text_insights(request.document_text)
        
        return {
            'status': 'success',
            'document_analysis': gemini_result,
            'text_insights': text_insights,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

@app.post("/api/ai/analyze-name")
async def analyze_name_endpoint(request: NameAnalysisRequest):
    """Analyze name origins and meanings"""
    try:
        name_analysis = await ApiGptService.analyze_name_origins(
            request.name, 
            request.origin_context
        )
        
        return {
            'status': 'success',
            'name_analysis': name_analysis,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Name analysis failed: {str(e)}")

@app.post("/api/ai/upload-document")
async def upload_document_analysis(file: UploadFile = File(...)):
    """Upload and analyze document files"""
    try:
        # Read file content
        content = await file.read()
        
        # For now, assume text files. In production, add OCR for images/PDFs
        if file.content_type.startswith('text/'):
            text_content = content.decode('utf-8')
        else:
            # Placeholder for OCR functionality
            text_content = "OCR processing not implemented in this demo"
        
        # Analyze extracted text
        analysis = await GeminiAIService.analyze_document(text_content, file.content_type)
        text_insights = GenealogyAnalyzer.extract_text_insights(text_content)
        
        return {
            'status': 'success',
            'filename': file.filename,
            'content_type': file.content_type,
            'analysis': analysis,
            'insights': text_insights
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")

@app.get("/api/ai/health")
async def health_check():
    """Health check for AI services"""
    return {
        'status': 'healthy',
        'services': {
            'google_gemini': bool(GOOGLE_API_KEY),
            'openai': bool(OPENAI_API_KEY),
            'apigpt': bool(APIGPT_API_KEY)
        },
        'timestamp': datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models import ChatRequest, ChatResponse
from middleware.translation import TranslationMiddleware
from agents.mock_orchestrator import mock_orchestrate
from agents.graph import run_agent

# Load environment variables
load_dotenv()

app = FastAPI(title='ORCA Marine Intelligence API', version='1.0.0')

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

translator = TranslationMiddleware()

@app.on_event("startup")
async def startup_event():
    mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if mock_mode or not api_key:
        print("ORCA Backend started in MOCK mode.")
    else:
        print("ORCA Backend started in LLM mode.")

@app.get("/api/health")
async def health_check():
    mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
    api_key = os.getenv("GOOGLE_API_KEY", "")
    mode = 'mock' if mock_mode or not api_key else 'llm'
    return {"status": "healthy", "mode": mode, "version": "1.0.0"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Step 1: Detect and translate input
        lang = translator.detect_language(request.message)
        if lang != 'en':
            request.message = await translator.translate_to_english(request.message, lang)

        mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        api_key = os.getenv("GOOGLE_API_KEY", "")
        
        # Step 2 & 3: Route to mock or LLM agent
        if mock_mode or not api_key:
            response = await mock_orchestrate(request)
        else:
            response = await run_agent(request)
            
        # Step 4: Translate back if necessary
        if lang != 'en':
            response.text_response = await translator.translate_from_english(response.text_response, lang)
            
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

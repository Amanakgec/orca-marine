import os
import sys
import re

# Configure UTF-8 for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import edge_tts

from models import ChatRequest, ChatResponse
from middleware.translation import TranslationMiddleware
from agents.mock_orchestrator import mock_orchestrate
from agents.graph import run_agent

# Load environment variables
load_dotenv()

app = FastAPI(title='ORCA Marine Intelligence API', version='1.2.0')

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

translator = TranslationMiddleware()

# High-fidelity Microsoft Neural Indian Regional Voices (100% human sounding)
VOICE_MAP = {
    'en': 'en-IN-NeerjaExpressiveNeural',
    'hi': 'hi-IN-SwaraNeural',
    'ta': 'ta-IN-PallaviNeural',
    'te': 'te-IN-ShrutiNeural',
    'mr': 'mr-IN-AarohiNeural',
    'gu': 'gu-IN-DhwaniNeural',
    'kn': 'kn-IN-SapnaNeural',
    'ml': 'ml-IN-SobhanaNeural',
    'bn': 'bn-IN-TanishaaNeural',
    'gom': 'mr-IN-AarohiNeural',
    'or': 'hi-IN-SwaraNeural'
}

@app.on_event("startup")
async def startup_event():
    mock_mode = os.getenv("MOCK_MODE", "true").lower() == "true"
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if mock_mode or not api_key:
        print("[ORCA] Backend started in MOCK & COASTAL INTEL mode with Neural TTS.")
    else:
        print("[ORCA] Backend started in LLM mode with Gemini & Neural TTS.")

@app.get("/api/health")
async def health_check():
    mock_mode = os.getenv("MOCK_MODE", "true").lower() == "true"
    api_key = os.getenv("GOOGLE_API_KEY", "")
    mode = 'mock' if mock_mode or not api_key else 'llm'
    return {
        "status": "healthy",
        "mode": mode,
        "supported_languages": list(translator.SUPPORTED_LANGUAGES.keys()),
        "neural_tts_enabled": True,
        "version": "1.2.0"
    }

@app.get("/api/tts")
async def get_neural_tts(text: str, language: str = 'en'):
    """Generate realistic, human-like neural speech for regional Indian coastal languages."""
    try:
        # Strip markdown syntax and clean spacing
        clean_text = re.sub(r'[*_#`•]', ' ', text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        if not clean_text:
            raise HTTPException(status_code=400, detail="Empty text provided")

        # Select natural regional neural voice
        voice = VOICE_MAP.get(language, 'en-IN-NeerjaExpressiveNeural')

        # Limit to first 600 characters for snappy speech responses
        truncated_text = clean_text[:600]

        communicate = edge_tts.Communicate(truncated_text, voice)
        audio_stream = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.extend(chunk["data"])

        return Response(
            content=bytes(audio_stream),
            media_type="audio/mpeg",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    except Exception as e:
        print(f"[TTS Error]: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Step 1: Detect language of input message
        detected_lang = translator.detect_language(request.message)

        # Target language priority: user selected dropdown -> detected from message -> English default
        target_lang = request.language if (request.language and request.language != 'en') else detected_lang

        # Translate input message to English for agent reasoning if typed in an Indic script
        processed_message = request.message
        if detected_lang != 'en':
            processed_message = await translator.translate_to_english(request.message, detected_lang)

        internal_request = ChatRequest(
            message=processed_message,
            location=request.location,
            language=target_lang
        )

        mock_mode = os.getenv("MOCK_MODE", "true").lower() == "true"
        api_key = os.getenv("GOOGLE_API_KEY", "")

        # Step 2: Route to LangGraph LLM agent or Mock Orchestrator
        if mock_mode or not api_key:
            response = await mock_orchestrate(internal_request)
        else:
            response = await run_agent(internal_request)

        # Step 3: Translate response text to the user's requested regional language
        if target_lang and target_lang != 'en':
            translated_text = await translator.translate_from_english(response.text_response, target_lang)
            if translated_text:
                response.text_response = translated_text

        return response
    except Exception as e:
        print(f"[Error in /api/chat]: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# Frontend Static Asset Serving (Production)
# ==========================================
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if not os.path.exists(FRONTEND_DIST):
    # Fallback to local dist if packaged in backend folder
    alt_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist"))
    if os.path.exists(alt_dist):
        FRONTEND_DIST = alt_dist

if os.path.exists(FRONTEND_DIST):
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="static-assets")

    @app.get("/")
    async def serve_root():
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"status": "ORCA Marine Intelligence API running"}

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Page not found")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"[ORCA] Starting server on port {port}...")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)


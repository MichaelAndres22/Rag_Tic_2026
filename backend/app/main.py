from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.documents import router as documents_router
from app.api.routes.chat import router as chat_router
from app.api.routes.outputs import router as outputs_router

app = FastAPI(title="RAG NotebookLM-like (MVP)")

# CORS configuration must be added before routes
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "https://interfaz-ia-beta.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(outputs_router)

@app.get("/health")
def health():
    return {"status": "ok"}
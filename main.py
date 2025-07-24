
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from utils import process_presentation
import openai
import os

app = FastAPI()

# Allow all origins (so Wix can call it)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/review")
async def review(file: UploadFile = File(...)):
    content = await file.read()
    results = await process_presentation(content, file.filename)
    return results

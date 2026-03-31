from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import pdfplumber
import os
import json
from dotenv import load_dotenv
from .auth import router as auth_router

# -------------------- ENV SETUP --------------------
load_dotenv("../.env")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
print("Loaded key:", GROQ_API_KEY) 

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found.")

# -------------------- FASTAPI INIT --------------------
app = FastAPI()

# Include auth routes
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- LLM SETUP --------------------
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0.5
)

# -------------------- PDF READER --------------------
def extract_text_from_pdf(uploaded_file):
    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text.strip()

# -------------------- QUESTION GENERATOR --------------------
def generate_questions(
    q_type,
    subject,
    full_syllabus,
    unit_number,
    co_name,
    number,
    difficulty
):
    if number == 0:
        return ""

    prompt_template = """
You are an expert university question paper setter.

Generate {number} {q_type} questions.

Subject: {subject}
Course Outcome: {co_name}
Difficulty Level: {difficulty}

FULL SYLLABUS:
{full_syllabus}

IMPORTANT:
- Generate questions ONLY from Unit {unit_number}
- Ignore all other units completely
- University exam standard
- NO answers
- NO explanations

Output format:
Q1. ...
Q2. ...
"""

    chain = (
        ChatPromptTemplate.from_template(prompt_template)
        | llm
        | StrOutputParser()
    )

    return chain.invoke({
        "number": number,
        "q_type": q_type,
        "subject": subject,
        "co_name": co_name,
        "full_syllabus": full_syllabus,
        "unit_number": unit_number,
        "difficulty": difficulty
    })

# -------------------- API ENDPOINT --------------------
@app.post("/generate")
async def generate(
    subject: str = Form(...),
    unitConfig: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # Convert JSON string from frontend → Python list
        unit_config = json.loads(unitConfig)

        # Extract syllabus text
        syllabus_text = extract_text_from_pdf(file.file)

        results = []

        for unit in unit_config:

            mcq = ""
            short_q = ""
            long_q = ""

            if unit.get("mcq", 0) > 0:
                mcq = generate_questions(
                    "multiple choice",
                    subject,
                    syllabus_text,
                    unit["unit"],
                    unit["co"],
                    unit["mcq"],
                    unit["difficulty"]
                )

            if unit.get("short", 0) > 0:
                short_q = generate_questions(
                    "short answer",
                    subject,
                    syllabus_text,
                    unit["unit"],
                    unit["co"],
                    unit["short"],
                    unit["difficulty"]
                )

            if unit.get("long", 0) > 0:
                long_q = generate_questions(
                    "long answer",
                    subject,
                    syllabus_text,
                    unit["unit"],
                    unit["co"],
                    unit["long"],
                    unit["difficulty"]
                )

            if mcq or short_q or long_q:
                results.append({
                    "unit": unit["unit"],
                    "co": unit["co"],
                    "difficulty": unit["difficulty"],
                    "mcq": mcq,
                    "short": short_q,
                    "long": long_q
                })

        return {
            "success": True,
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# -------------------- HEALTH CHECK --------------------
@app.get("/")
def home():
    return {"status": "Backend is running successfully"}

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine
from pydantic import BaseModel

# --- AI Imports ---
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware

# 1. --- Load Environment Variables (CORRECTED PATH) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🌟 NAYA: Kyunki aapki .env file 'textile_project' folder ke andar hai
env_path = os.path.join(BASE_DIR, 'textile_project', '.env')
load_dotenv(dotenv_path=env_path)

# Check karein ki key load hui ya nahi (Fail-safe)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(f"❌ ERROR: OPENAI_API_KEY nahi mili! Kripya check karein ki is file mein key hai: {env_path}")

# 2. --- Database Engine Setup ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://skpuser:mypassword@localhost:5432/textileerp"

engine = create_engine(DATABASE_URL)

# 3. --- FastAPI Setup ---
app = FastAPI(title="Royal Logic AI Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://192.168.29.38:3000" # Aapka network IP
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8000/api/token/")


# 4. --- LangChain SQL Agent Setup ---
langchain_db = SQLDatabase(engine)

# Initialize the LLM (The "Brain")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 🌟 NAYA: AI ke liye Custom Instructions (Smart Prompt)
CUSTOM_PREFIX = """You are an intelligent ERP Assistant named Royal Logic AI.
Whenever a user asks for a 'report', 'list', 'table', 'details', or uses simple phrases like 'show me all products', 'till date', 'pending orders', etc., YOU MUST ASSUME they want a data table.
In these cases, ALWAYS generate the final data STRICTLY as a raw JSON array of objects. 
DO NOT ask the user to specify the format. Make sure the JSON keys are clear, user-friendly, and readable (use spaces instead of underscores).
If they ask a simple question that requires just a number or a short text answer, answer normally without JSON.
"""

# Create the Agent that translates English to SQL (Prefix pass kiya gaya hai)
sql_agent = create_sql_agent(
    llm=llm, 
    db=langchain_db, 
    agent_type="openai-tools", 
    verbose=True,
    prefix=CUSTOM_PREFIX # 🌟 NAYA: Prompt yahan add kiya hai
)

# 5. --- Define the Input Format ---
class AIQuery(BaseModel):
    question: str

# 6. --- API Routes ---
@app.post("/api/ai/ask")
async def ask_inventory_ai(query: AIQuery, token: str = Depends(oauth2_scheme)):
    """
    Send an English question, get an AI-generated answer based on your database.
    """
    try:
        # The agent dynamically writes SQL, runs it, and explains the result
        response = sql_agent.invoke({"input": query.question})
        
        return {
            "status": "Success",
            "question": query.question,
            "answer": response["output"],
            "bot_name": "Royal_Logic_AI"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {str(e)}")
    
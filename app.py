import bcrypt
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from agents import deps, async_groq_client
from auth import create_access_token, verify_password
from database import DatabaseHandler
from fastapi.middleware.cors import CORSMiddleware
from main import main, chat
import shutil
from uuid import uuid4, UUID
import os
from datetime import datetime
from transcription import TranscriptionService
import boto3
from botocore.client import Config
db = DatabaseHandler(deps)

transcription_service = TranscriptionService(groq_client=async_groq_client)

app = FastAPI()

origins = [
    "http://localhost:3000",  
    "http://127.0.0.1:3000",
    "https://voiceiqindominuslabs.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ColumnRequest(BaseModel):
    columns: List[str] | str
    limit: int

class ReportRequest(BaseModel):
    uuid: UUID
    
class ChatRequest(BaseModel):
    user_prompt: str
    uuid: UUID

class Dates(BaseModel):
    from_date: datetime
    to_date: datetime

class VoiceChatRequest(BaseModel):
    file: UploadFile = File(...)
    uuid: UUID

@app.post("/logs/date")
async def get_all_by_dates(req: Dates):
    try:
        call_logs = await db.get_all_by_dates(req.from_date, req.to_date)
        return {"data": call_logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs/all")
async def get_all_logs():
    try:
        result = await db.get_all_logs()
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs/{id}")
async def get_all_by_id(id: str):  # or `id: str` depending on your data type
    try:
        result = await db.get_log(id=id)
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/logs/columns")
async def get_columns(req: ColumnRequest):
    try:
        result = await db.get_columns(req.columns, req.limit)
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/logs/report")
async def get_report(req: ReportRequest):
    try:
        result = await db.get_report(req.uuid)
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create_log")
async def create_log(file: UploadFile = File(...)):
    allowed_exts = (".wav", ".mp3")
    ext = os.path.splitext(file.filename)[-1].lower()
    filename = file.filename

    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Only .wav or .mp3 files are supported")

    # Check if filename already exists
    if await db.file_exists(filename):
        raise HTTPException(status_code=409, detail="File with this name already uploaded")

    try:
        temp_filename = filename

        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print("✅ TempFile Created.")

        id = await main(file_path=temp_filename)

        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        return JSONResponse(content={
            "status": "success",
            "message" : "Log uploaded successfully",
            "uuid": id
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    

@app.post("/chat")
async def report_chat(req: ChatRequest):
    try:
        response = await chat(user_prompt=req.user_prompt, uuid=req.uuid)
        
        return JSONResponse(content={
            "status": "success",
            "content": response
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/voice_chat")
async def report_voice_chat(file: UploadFile = File(...), uuid: UUID = Form(...)):
    try:
        temp_filename = file.filename

        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        transcript = await transcription_service.transcribe_groq(file_path=temp_filename)

        response = await chat(user_prompt=transcript, uuid=uuid)
        
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        return JSONResponse(content={
            "status": "success",
            "content": response
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/health")
async def health():
    return JSONResponse(content={
            "status": "success",
            "content": "healthy asf!"
        })

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    user_data = await db.get_user_by_email(user.email)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, user_data["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": str(user_data["email"])})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/signup")
async def signup(user: UserLogin):
    existing_user = await db.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    created = await db.create_user(user.email, hashed)
    if not created:
        raise HTTPException(status_code=500, detail="User creation failed")

    return {"msg": "User created successfully"}






# MinIO settings
MINIO_ENDPOINT = "http://localhost:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
REGION = "us-east-1"
EXPIRATION = 3600  # in seconds

# Initialize S3 client
s3 = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name=REGION
)

class PresignRequest(BaseModel):
    bucket: str
    key: str 

@app.post("/generate-presigned-url")
def generate_presigned_url(req: PresignRequest):
    try:
        s3.head_bucket(Bucket=req.bucket)
    except:
        s3.create_bucket(Bucket=req.bucket)


    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": req.bucket, "Key": req.key},
        ExpiresIn=EXPIRATION
    )
    return {"url": url}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
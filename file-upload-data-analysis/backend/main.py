import os
import pandas as pd
import PyPDF2
import ezdxf
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, JSON, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Optional
import uvicorn
import logging
import aiofiles
from cryptography.fernet import Fernet
import requests
import asyncio
from datetime import datetime, timedelta  # Import for JWT claims

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db/mydatabase"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ExtractedData(Base):
    __tablename__ = "extracted_data"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    file_type = Column(String)
    content = Column(JSON)
    raw_file = Column(LargeBinary)

Base.metadata.create_all(bind=engine)

# Security setup
SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")  # Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Encryption setup
ENCRYPTION_KEY = Fernet.generate_key()
fernet = Fernet(ENCRYPTION_KEY)

# File processing functions
async def process_pdf(file_path: str) -> Dict:
    async with aiofiles.open(file_path, 'rb') as file:
        content = await file.read()
        reader = PyPDF2.PdfReader(content)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return {"text": text}

async def process_xlsx(file_path: str) -> Dict:
    df = pd.read_excel(file_path)
    return df.to_dict()

async def process_cad(file_path: str) -> Dict:
    doc = ezdxf.readfile(file_path)
    modelspace = doc.modelspace()
    
    # Extract more specific measurements and metadata
    entities = []
    for entity in modelspace:
        if entity.dxftype() == 'LINE':
            start = entity.dxf.start
            end = entity.dxf.end
            length = entity.length()
            entities.append({
                'type': 'LINE',
                'start': (start.x, start.y, start.z),
                'end': (end.x, end.y, end.z),
                'length': length
            })
        elif entity.dxftype() == 'CIRCLE':
            center = entity.dxf.center
            radius = entity.dxf.radius
            entities.append({
                'type': 'CIRCLE',
                'center': (center.x, center.y, center.z),
                'radius': radius
            })
        # Add more entity types as needed
    
    metadata = {
        'version': doc.header['$ACADVER'],
        'units': doc.header['$INSUNITS'],
        'create_date': doc.header['$TDCREATE'],
        'last_saved': doc.header['$TDUPDATE'],
    }
    
    return {"metadata": metadata, "entities": entities}

# Database functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def store_data(db: SessionLocal, file_name: str, file_type: str, data: Dict, raw_file: bytes):
    encrypted_file = fernet.encrypt(raw_file)
    db_item = ExtractedData(file_name=file_name, file_type=file_type, content=data, raw_file=encrypted_file)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# Form generation functions
def generate_form(data: Dict) -> Dict:
    form = {"title": "Generated Form", "fields": []}
    
    if "metadata" in data:
        for key, value in data["metadata"].items():
            form["fields"].append({"name": f"Metadata: {key}", "value": str(value), "type": "text"})
    
    if "entities" in data:
        for i, entity in enumerate(data["entities"]):
            form["fields"].append({"name": f"Entity {i+1}", "value": str(entity), "type": "text"})
    
    if "text" in data:
        form["fields"].append({"name": "Extracted Text", "value": data["text"], "type": "textarea"})
    
    return form

# Microsoft Dynamics integration
async def send_to_dynamics(form_data: Dict):
    # This is a placeholder. You'll need to implement the actual API call to Microsoft Dynamics
    dynamics_api_url = "https://your-dynamics-instance.api.crm.dynamics.com/api/data/v9.2/"
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(dynamics_api_url, json=form_data, headers=headers)
        response.raise_for_status()
        return {"status": "success", "message": "Data sent to Microsoft Dynamics"}
    except requests.RequestException as e:
        logger.error(f"Error sending data to Microsoft Dynamics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send data to Microsoft Dynamics")

# FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication
def create_access_token(data: dict):
    to_encode = data.copy()
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expires, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Implement user authentication logic here
    
    # Retrieve user from the database (pseudo code)
    # user = db.query(User).filter(User.username == form_data.username).first()
    # if not user or not pwd_context.verify(form_data.password, user.hashed_password):
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")

    
    # For simplicity, we're using a hardcoded user
    if form_data.username != "admin" or form_data.password != "password":
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

# File upload and processing endpoint
@app.post("/upload/")
async def upload_files(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = [],
    db: SessionLocal = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    results = []
    for file in files:
        file_path = f"temp_{file.filename}"
        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            
            if file.filename.endswith('.pdf'):
                data = await process_pdf(file_path)
                file_type = 'pdf'
            elif file.filename.endswith('.xlsx'):
                data = await process_xlsx(file_path)
                file_type = 'xlsx'
            elif file.filename.endswith('.dwg'):
                data = await process_cad(file_path)
                file_type = 'cad'
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
            
            db_item = await store_data(db, file.filename, file_type, data, content)
            form = generate_form(data)
            results.append({"filename": file.filename, "form": form, "id": db_item.id})
            
            # Send to Microsoft Dynamics in the background
            background_tasks.add_task(send_to_dynamics, form)
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}: {str(e)}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    return results

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from a .env file
    uvicorn.run(app, host="0.0.0.0", port=8000)
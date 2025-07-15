import os, time, secrets, hashlib
from fastapi import FastAPI, Depends, HTTPException, Header, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from io import BytesIO
from models import User
from database import SessionLocal, create_tables
from auth import hash_password, verify_password
from pydantic import BaseModel
from cryptography.fernet import Fernet
from jwt_auth import create_access_token, verify_access_token
from datetime import timedelta
from encryption import get_fernet
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import Request
from slowapi.errors import RateLimitExceeded
from fastapi import Query
from datetime import datetime
import logging
from fastapi import Query, HTTPException
from models import User, FileShare
import sys

# Allowed file extensions and size
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".png", ".jpg", ".doc", ".rar", ".7z", ".zip", ".py"}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# FastAPI app and CORS setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate-limiter setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("trustshare.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


@app.get("/")
def read_root():
    return {"msg": "TrustShare backend running!"}

class UserCreate(BaseModel):
    username: str
    password: str

create_tables()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_obj(db: Session = Depends(get_db), authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ")[1] if " " in authorization else authorization
    username = verify_access_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return db_user

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        logging.warning(f"Registration failed: Username already exists ({user.username})")
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = hash_password(user.password)
    encryption_key = Fernet.generate_key().decode()
    new_user = User(username=user.username, hashed_password=hashed, encryption_key=encryption_key)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logging.info(f"New user registered: {user.username}")
    return {"msg": "User created successfully"}

@app.post("/login")
@limiter.limit("5/minute")
def login(user: UserCreate, db: Session = Depends(get_db), request: Request = None):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        logging.warning(f"Failed login attempt for username: {user.username}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=60)
    )
    logging.info(f"User logged in: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_obj)
):
    logging.info(f"Upload endpoint called by user: {current_user.username}")
    print(f"Upload called by {current_user.username}")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        logging.warning(f"{current_user.username} attempted upload with disallowed extension: {file.filename}")
        raise HTTPException(status_code=400, detail="File type not allowed.")
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        logging.warning(f"{current_user.username} attempted to upload oversized file: {file.filename}")
        raise HTTPException(status_code=400, detail="File too large.")

    user_prefix = hashlib.sha256(current_user.username.encode()).hexdigest()[:8]
    unique_part = secrets.token_hex(8)
    safe_filename = f"{user_prefix}_{int(time.time())}_{unique_part}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, safe_filename)

    fernet = Fernet(current_user.encryption_key.encode())
    encrypted_content = fernet.encrypt(content)

    with open(filepath, "wb") as f:
        f.write(encrypted_content)

    logging.info(f"{current_user.username} uploaded file: {file.filename}")
    return {"msg": "File uploaded & encrypted!", "filename": safe_filename}

@app.get("/files")
def list_files(current_user: User = Depends(get_current_user_obj)):
    user_prefix = hashlib.sha256(current_user.username.encode()).hexdigest()[:8]
    files = [
        f for f in os.listdir(UPLOAD_DIR)
        if f.startswith(f"{user_prefix}_")
    ]
    result = [
        {
            "stored_name": f,
            "display_name": "_".join(f.split("_")[3:])  # original filename portion
        }
        for f in files
    ]
    logging.info(f"{current_user.username} listed files.")
    return {"files": result}

@app.get("/files/{filename}")
def get_file(filename: str, current_user: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    import hashlib

    user_prefix = hashlib.sha256(current_user.username.encode()).hexdigest()[:8]
    logging.info(f"User '{current_user.username}' requested file download: '{filename}'")

    owned_matches = [
        f for f in os.listdir(UPLOAD_DIR)
        if f.startswith(f"{user_prefix}_") and f.split("_", 3)[-1] == filename
    ]

    if owned_matches:
        logging.info(f"File '{filename}' is owned by user '{current_user.username}'")
        path = os.path.join(UPLOAD_DIR, owned_matches[0])
        encryption_key = current_user.encryption_key
    else:
        share = db.query(FileShare).filter(
            FileShare.file_name == filename,
            FileShare.shared_with_id == current_user.id
        ).first()

        if not share:
            logging.warning(f"Unauthorized file access attempt by '{current_user.username}' for file '{filename}'")
            raise HTTPException(status_code=404, detail="File not found or access denied.")

        logging.info(f"File '{filename}' is shared with user '{current_user.username}' by owner ID {share.owner_id}")
        path = os.path.join(UPLOAD_DIR, share.file_name)

        owner = db.query(User).filter(User.id == share.owner_id).first()
        if not owner:
            logging.error(f"Owner not found for shared file '{filename}' (owner ID: {share.owner_id})")
            raise HTTPException(status_code=404, detail="File owner not found.")

        encryption_key = owner.encryption_key

    try:
        fernet = Fernet(encryption_key.encode())
        with open(path, "rb") as f:
            encrypted_content = f.read()
        decrypted_content = fernet.decrypt(encrypted_content)
    except Exception as e:
        logging.error(f"Error decrypting or reading file '{filename}' for user '{current_user.username}': {e}")
        raise HTTPException(status_code=500, detail="Error decrypting file.")

    logging.info(f"User '{current_user.username}' successfully downloaded file: '{filename}'")
    return StreamingResponse(
        BytesIO(decrypted_content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


    
@app.post("/share-file")
def share_file(
    file_name: str = Query(..., description="Stored encrypted filename"),
    shared_with_username: str = Query(..., description="Username to share file with"),
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    try:
        user_prefix = hashlib.sha256(current_user.username.encode()).hexdigest()[:8]
        if not file_name.startswith(user_prefix):
            raise HTTPException(status_code=403, detail="You do not own this file.")

        file_path = os.path.join(UPLOAD_DIR, file_name)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found.")

        shared_user = db.query(User).filter(User.username == shared_with_username).first()
        if not shared_user:
            raise HTTPException(status_code=404, detail="User to share with not found.")

        if shared_user.id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot share file with yourself.")

        existing_share = db.query(FileShare).filter(
            FileShare.file_name == file_name,
            FileShare.owner_id == current_user.id,
            FileShare.shared_with_id == shared_user.id
        ).first()
        if existing_share:
            return {"msg": f"File already shared with {shared_with_username}."}

        share = FileShare(
            file_name=file_name,
            owner_id=current_user.id,
            shared_with_id=shared_user.id
        )
        db.add(share)
        db.commit()

        logging.info(f"{current_user.username} shared file '{file_name}' with {shared_with_username}")
        return {"msg": f"File shared with {shared_with_username} successfully."}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error sharing file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")


@app.get("/shared-files")
def get_shared_files(
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    shares = db.query(FileShare).filter(FileShare.shared_with_id == current_user.id).all()

    files = []
    for share in shares:
        shared_at_iso = (
            share.shared_at.isoformat() if share.shared_at and isinstance(share.shared_at, datetime) else None
        )
        files.append({
            "file_name": share.file_name,
            "owner": share.owner.username,
            "shared_at": shared_at_iso
        })

    return {"shared_files": files}


import os
import logging
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import httpx
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("baptism_feedback")

# Load environment variables
load_dotenv()

# Setup SQLite Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./feedback.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Model for Feedback
class FeedbackModel(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    relationship = Column(String(50), nullable=False)
    invitation_rating = Column(Integer, nullable=False)
    overall_rating = Column(Integer, nullable=False)
    food_rating = Column(String(30), nullable=False)
    improvements = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create database tables
Base.metadata.create_all(bind=engine)

# Pydantic Schemas for Validation
class FeedbackCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the guest")
    relationship: str = Field(..., description="Relationship to family")
    invitation_rating: int = Field(..., ge=1, le=5, description="Invitation rating (1-5)")
    overall_rating: int = Field(..., ge=1, le=5, description="Overall function rating (1-5)")
    food_rating: str = Field(..., description="Food rating")
    improvements: Optional[str] = Field(None, max_length=1000, description="Suggestions or feedback")

    # Validate relationship options
    @field_validator('relationship')
    @classmethod
    def validate_relationship(cls, value: str) -> str:
        valid_options = {"Friend", "Relative", "Church member", "Neighbor"}
        if value not in valid_options:
            raise ValueError(f"Relationship must be one of: {', '.join(valid_options)}")
        return value

    # Validate food rating options
    @field_validator('food_rating')
    @classmethod
    def validate_food_rating(cls, value: str) -> str:
        valid_options = {"Excellent", "Good", "Average", "Poor"}
        if value not in valid_options:
            raise ValueError(f"Food rating must be one of: {', '.join(valid_options)}")
        return value

# Initialize FastAPI
app = FastAPI(
    title="Baptism Feedback System",
    description="A simple, elegant feedback system with SQLite and Telegram integration.",
    version="1.0.0"
)

# Enable CORS for local development when running frontend/backend separately
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telegram integration function
async def send_telegram_notification(feedback: FeedbackCreate):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    # If variables are missing, log a warning and return.
    # This ensures the API still works even if the user hasn't set up Telegram yet.
    if not token or not chat_id or token.startswith("your_") or chat_id.startswith("your_"):
        logger.warning("Telegram Bot Token or Chat ID not configured. Skipping notification.")
        return

    message = (
        f"💒 *New message received:*\n"
        f"👤 *Name:* {feedback.name}\n"
        f"🤝 *Relationship:* {feedback.relationship}\n"
        f"✉️ *Invitation experience:* {feedback.invitation_rating}/5\n"
        f"✨ *Overall function rating:* {feedback.overall_rating}/5\n"
        f"🍲 *Food rating:* {feedback.food_rating}\n"
        f"📝 *Any improve:* {feedback.improvements or 'None'}"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            if response.status_code == 200:
                logger.info("Telegram notification sent successfully.")
            else:
                logger.error(f"Failed to send Telegram message. Response: {response.text}")
    except Exception as e:
        logger.error(f"Error connecting to Telegram API: {str(e)}")

# API Endpoint to receive feedback
@app.post("/api/feedback", status_code=status.HTTP_201_CREATED)
async def create_feedback(feedback: FeedbackCreate):
    # Save to database
    db: Session = SessionLocal()
    try:
        db_feedback = FeedbackModel(
            name=feedback.name,
            relationship=feedback.relationship,
            invitation_rating=feedback.invitation_rating,
            overall_rating=feedback.overall_rating,
            food_rating=feedback.food_rating,
            improvements=feedback.improvements
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save feedback to the database."
        )
    finally:
        db.close()

    # Trigger Telegram notification asynchronously (don't block the HTTP response)
    await send_telegram_notification(feedback)

    return {"status": "success", "message": "Feedback submitted successfully", "id": db_feedback.id}

# Route to serve the main frontend page
@app.get("/")
async def serve_index():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend files not found. Please place static files in '/static' folder."}

# Mount the static directory to serve styling, scripts and assets
# Ensure the directory exists to prevent startup errors
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    # Read port from environment variable, defaulting to 8000
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)

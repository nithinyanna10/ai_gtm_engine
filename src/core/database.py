"""
Database models and connection management for the AI GTM Engine.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from pydantic import BaseModel

from .config import settings

# Create database engine
engine = create_engine(
    settings.database.database_url,
    echo=settings.database.echo,
    pool_pre_ping=True
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
class Base(DeclarativeBase):
    pass

# Pydantic models for API responses
class LeadBase(BaseModel):
    company_name: str
    domain: str
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    revenue_range: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    intent_score: float
    last_updated: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class SignalBase(BaseModel):
    lead_id: int
    signal_type: str
    source: str
    content: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None

class SignalCreate(SignalBase):
    pass

class Signal(SignalBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class OutreachBase(BaseModel):
    lead_id: int
    channel: str
    content: str
    status: str
    metadata: Optional[Dict[str, Any]] = None

class OutreachCreate(OutreachBase):
    pass

class Outreach(OutreachBase):
    id: int
    created_at: datetime
    sent_at: Optional[datetime] = None
    response_received_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# SQLAlchemy Models
class Lead(Base):
    """Lead/company information and scoring."""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), nullable=False, unique=True, index=True)
    industry = Column(String(100), index=True)
    employee_count = Column(Integer)
    revenue_range = Column(String(50))
    location = Column(String(255))
    description = Column(Text)
    
    # Scoring fields
    intent_score = Column(Float, default=0.0, index=True)
    github_score = Column(Float, default=0.0)
    community_score = Column(Float, default=0.0)
    job_posting_score = Column(Float, default=0.0)
    news_score = Column(Float, default=0.0)
    technographic_score = Column(Float, default=0.0)
    firmographic_score = Column(Float, default=0.0)
    
    # Technographic data
    tech_stack = Column(JSON)
    primary_tech = Column(String(100))
    
    # Firmographic data
    funding_stage = Column(String(50))
    total_funding = Column(Float)
    founded_year = Column(Integer)
    
    # Metadata
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    signals = relationship("Signal", back_populates="lead", cascade="all, delete-orphan")
    outreaches = relationship("Outreach", back_populates="lead", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_leads_intent_score', 'intent_score'),
        Index('idx_leads_industry', 'industry'),
        Index('idx_leads_employee_count', 'employee_count'),
        Index('idx_leads_last_updated', 'last_updated'),
    )

class Signal(Base):
    """Intent signals from various sources."""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    signal_type = Column(String(50), nullable=False, index=True)  # github, reddit, linkedin, news, etc.
    source = Column(String(100), nullable=False)  # specific source (e.g., "github.com/company/repo")
    content = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    
    # Signal metadata
    signal_metadata = Column(JSON)  # Additional data like URLs, timestamps, etc.
    keywords_found = Column(JSON)  # List of relevant keywords found
    
    # Timestamps
    signal_date = Column(DateTime)  # When the signal occurred
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    lead = relationship("Lead", back_populates="signals")
    
    # Indexes
    __table_args__ = (
        Index('idx_signals_lead_id', 'lead_id'),
        Index('idx_signals_type', 'signal_type'),
        Index('idx_signals_date', 'signal_date'),
        Index('idx_signals_confidence', 'confidence'),
    )

class Outreach(Base):
    """Outreach attempts and responses."""
    __tablename__ = "outreaches"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    channel = Column(String(50), nullable=False, index=True)  # email, linkedin, video, call
    content = Column(Text, nullable=False)
    status = Column(String(50), default="pending", index=True)  # pending, sent, delivered, opened, replied, bounced
    
    # Delivery metadata
    delivery_metadata = Column(JSON)  # Delivery info, response data, etc.
    subject_line = Column(String(255))
    recipient_email = Column(String(255))
    recipient_name = Column(String(255))
    
    # Response tracking
    response_content = Column(Text)
    response_sentiment = Column(String(50))  # positive, negative, neutral
    response_score = Column(Float)  # 0-1 score of response quality
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    replied_at = Column(DateTime)
    
    # Relationships
    lead = relationship("Lead", back_populates="outreaches")
    
    # Indexes
    __table_args__ = (
        Index('idx_outreaches_lead_id', 'lead_id'),
        Index('idx_outreaches_channel', 'channel'),
        Index('idx_outreaches_status', 'status'),
        Index('idx_outreaches_created_at', 'created_at'),
    )

class AITemplate(Base):
    """AI-generated content templates and prompts."""
    __tablename__ = "ai_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_type = Column(String(50), nullable=False, index=True)  # email, linkedin, video, call
    trigger_type = Column(String(50), nullable=False, index=True)  # github, hiring, news, etc.
    prompt_template = Column(Text, nullable=False)
    example_output = Column(Text)
    performance_score = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_templates_type', 'template_type'),
        Index('idx_templates_trigger', 'trigger_type'),
        Index('idx_templates_performance', 'performance_score'),
    )

# Database utility functions
def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)

def get_high_intent_leads(db: Session, limit: int = 100, min_score: float = None) -> List[Lead]:
    """Get leads with high intent scores."""
    query = db.query(Lead).filter(Lead.is_active == True)
    
    if min_score is None:
        min_score = settings.scoring.high_intent_threshold
    
    query = query.filter(Lead.intent_score >= min_score)
    query = query.order_by(Lead.intent_score.desc())
    query = query.limit(limit)
    
    return query.all()

def get_recent_signals(db: Session, days: int = 7) -> List[Signal]:
    """Get recent signals within specified days."""
    cutoff_date = datetime.now() - timedelta(days=days)
    return db.query(Signal).filter(Signal.created_at >= cutoff_date).all()

def get_lead_signals(db: Session, lead_id: int) -> List[Signal]:
    """Get all signals for a specific lead."""
    return db.query(Signal).filter(Signal.lead_id == lead_id).order_by(Signal.created_at.desc()).all()

def update_lead_score(db: Session, lead_id: int, scores: Dict[str, float]):
    """Update lead scoring based on new signals."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return
    
    # Update individual scores
    if 'github' in scores:
        lead.github_score = scores['github']
    if 'community' in scores:
        lead.community_score = scores['community']
    if 'job_posting' in scores:
        lead.job_posting_score = scores['job_posting']
    if 'news' in scores:
        lead.news_score = scores['news']
    if 'technographic' in scores:
        lead.technographic_score = scores['technographic']
    if 'firmographic' in scores:
        lead.firmographic_score = scores['firmographic']
    
    # Calculate overall intent score
    lead.intent_score = (
        lead.github_score * settings.scoring.github_weight +
        lead.community_score * settings.scoring.community_weight +
        lead.job_posting_score * settings.scoring.job_posting_weight +
        lead.news_score * settings.scoring.news_weight +
        lead.technographic_score * settings.scoring.technographic_weight +
        lead.firmographic_score * settings.scoring.firmographic_weight
    )
    
    lead.last_updated = datetime.now()
    db.commit()

# Initialize database on import
init_db()

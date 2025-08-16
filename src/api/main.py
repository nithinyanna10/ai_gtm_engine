"""
Main FastAPI application for the AI GTM Engine.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import uvicorn
from loguru import logger
from datetime import datetime, timedelta

from ..core.config import settings
from ..core.database import get_db, Lead, Signal, Outreach, get_high_intent_leads, update_lead_score
from ..data_collection.github_collector import github_collector
from ..data_collection.reddit_collector import reddit_collector
from ..data_collection.news_collector import create_news_collector
from ..data_collection.company_intelligence_collector import create_company_intelligence_collector
from ..data_collection.tech_stack_analyzer import create_tech_stack_analyzer
from ..data_collection.lead_discovery import create_lead_discovery
from ..ai_processing.content_generator import content_generator

# Create FastAPI app
app = FastAPI(
    title="AI GTM Engine",
    description="Advanced AI-powered Go-To-Market engine for intelligent lead generation and outreach",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI GTM Engine API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# Lead Management Endpoints
@app.get("/leads", response_model=List[Dict[str, Any]])
async def get_leads(
    limit: int = 100,
    min_score: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get leads with optional filtering."""
    try:
        leads = get_high_intent_leads(db, limit=limit, min_score=min_score)
        return [
            {
                "id": lead.id,
                "company_name": lead.company_name,
                "domain": lead.domain,
                "industry": lead.industry,
                "employee_count": lead.employee_count,
                "intent_score": lead.intent_score,
                "github_score": lead.github_score,
                "community_score": lead.community_score,
                "job_posting_score": lead.job_posting_score,
                "news_score": lead.news_score,
                "technographic_score": lead.technographic_score,
                "firmographic_score": lead.firmographic_score,
                "tech_stack": lead.tech_stack,
                "last_updated": lead.last_updated.isoformat(),
                "created_at": lead.created_at.isoformat()
            }
            for lead in leads
        ]
    except Exception as e:
        logger.error(f"Error getting leads: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/leads/{lead_id}", response_model=Dict[str, Any])
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get a specific lead by ID."""
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return {
            "id": lead.id,
            "company_name": lead.company_name,
            "domain": lead.domain,
            "industry": lead.industry,
            "employee_count": lead.employee_count,
            "revenue_range": lead.revenue_range,
            "location": lead.location,
            "description": lead.description,
            "intent_score": lead.intent_score,
            "github_score": lead.github_score,
            "community_score": lead.community_score,
            "job_posting_score": lead.job_posting_score,
            "news_score": lead.news_score,
            "technographic_score": lead.technographic_score,
            "firmographic_score": lead.firmographic_score,
            "tech_stack": lead.tech_stack,
            "primary_tech": lead.primary_tech,
            "funding_stage": lead.funding_stage,
            "total_funding": lead.total_funding,
            "founded_year": lead.founded_year,
            "last_updated": lead.last_updated.isoformat(),
            "created_at": lead.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/leads")
async def create_lead(
    lead_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Create a new lead."""
    try:
        # Check if lead already exists
        existing = db.query(Lead).filter(Lead.domain == lead_data["domain"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Lead with this domain already exists")
        
        # Create new lead
        lead = Lead(
            company_name=lead_data["company_name"],
            domain=lead_data["domain"],
            industry=lead_data.get("industry"),
            employee_count=lead_data.get("employee_count"),
            revenue_range=lead_data.get("revenue_range"),
            location=lead_data.get("location"),
            description=lead_data.get("description"),
            tech_stack=lead_data.get("tech_stack", []),
            primary_tech=lead_data.get("primary_tech"),
            funding_stage=lead_data.get("funding_stage"),
            total_funding=lead_data.get("total_funding"),
            founded_year=lead_data.get("founded_year")
        )
        
        db.add(lead)
        db.commit()
        db.refresh(lead)
        
        return {"id": lead.id, "message": "Lead created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

# Signal Collection Endpoints
@app.post("/leads/{lead_id}/collect-signals")
async def collect_signals(
    lead_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Collect signals for a specific lead."""
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Add background task to collect signals
        background_tasks.add_task(
            collect_signals_background,
            lead_id,
            lead.company_name,
            lead.domain
        )
        
        return {"message": "Signal collection started in background"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting signal collection for lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def collect_signals_background(lead_id: int, company_name: str, domain: str):
    """Background task to collect signals."""
    try:
        # Get lead object for collectors that need it
        db = next(get_db())
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        db.close()
        
        if not lead:
            logger.error(f"Lead {lead_id} not found for signal collection")
            return
        
        # Collect GitHub signals
        github_signals = github_collector.collect_company_activity(company_name, domain)
        github_collector.save_signals_to_db(lead_id, github_signals)
        
        # Collect Reddit signals
        reddit_signals = reddit_collector.collect_security_discussions(company_name, domain)
        reddit_collector.save_signals_to_db(lead_id, reddit_signals)
        
        # Collect News signals (new)
        news_collector = create_news_collector()
        news_signals = news_collector.collect_signals_for_lead(lead)
        news_collector.save_signals_to_db(lead_id, news_signals)
        
        # Collect Company Intelligence signals (new)
        company_collector = create_company_intelligence_collector()
        company_signals = company_collector.collect_signals_for_lead(lead)
        company_collector.save_signals_to_db(lead_id, company_signals)
        
        # Collect Tech Stack signals (new)
        tech_collector = create_tech_stack_analyzer()
        tech_signals = tech_collector.collect_signals_for_lead(lead)
        tech_collector.save_signals_to_db(lead_id, tech_signals)
        
        # Update lead scores
        db = next(get_db())
        try:
            # Calculate new scores based on collected signals
            scores = calculate_signal_scores(github_signals, reddit_signals, news_signals, company_signals, tech_signals)
            update_lead_score(db, lead_id, scores)
        finally:
            db.close()
        
        logger.info(f"Completed signal collection for lead {lead_id}")
    except Exception as e:
        logger.error(f"Error in background signal collection for lead {lead_id}: {e}")

@app.post("/discover-leads")
async def discover_leads(background_tasks: BackgroundTasks):
    """Discover new leads using API data sources."""
    try:
        # Add background task to discover leads
        background_tasks.add_task(discover_leads_background)
        
        return {"message": "Lead discovery started in background"}
    except Exception as e:
        logger.error(f"Error starting lead discovery: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def discover_leads_background():
    """Background task to discover leads from APIs."""
    try:
        lead_discovery = create_lead_discovery()
        
        # Discover leads from different sources
        github_leads = lead_discovery.discover_leads_from_github()
        news_leads = lead_discovery.discover_leads_from_news()
        reddit_leads = lead_discovery.discover_leads_from_reddit()
        
        # Combine all leads
        all_leads = github_leads + news_leads + reddit_leads
        
        # Save to database
        lead_discovery.save_leads_to_db(all_leads)
        
        logger.info(f"Discovered {len(all_leads)} new leads from APIs")
        
    except Exception as e:
        logger.error(f"Error in background lead discovery: {e}")

def calculate_signal_scores(github_signals: List[Dict], reddit_signals: List[Dict], news_signals: List[Dict], company_signals: List[Dict], tech_signals: List[Dict]) -> Dict[str, float]:
    """Calculate scores based on collected signals."""
    scores = {
        'github': 0.0,
        'community': 0.0,
        'job_posting': 0.0,
        'news': 0.0,
        'technographic': 0.0,
        'firmographic': 0.0
    }
    
    # Calculate GitHub score
    if github_signals:
        avg_confidence = sum(s['confidence'] for s in github_signals) / len(github_signals)
        scores['github'] = min(avg_confidence, 1.0)
    
    # Calculate community score (Reddit)
    if reddit_signals:
        avg_confidence = sum(s['confidence'] for s in reddit_signals) / len(reddit_signals)
        scores['community'] = min(avg_confidence, 1.0)
    
    # Calculate news score
    if news_signals:
        avg_confidence = sum(s['confidence'] for s in news_signals) / len(news_signals)
        scores['news'] = min(avg_confidence, 1.0)
    
    # Calculate company intelligence score
    if company_signals:
        avg_confidence = sum(s['confidence'] for s in company_signals) / len(company_signals)
        scores['firmographic'] = min(avg_confidence, 1.0)
    
    # Calculate technographic score
    if tech_signals:
        avg_confidence = sum(s['confidence'] for s in tech_signals) / len(tech_signals)
        scores['technographic'] = min(avg_confidence, 1.0)
    
    return scores

@app.get("/leads/{lead_id}/signals", response_model=List[Dict[str, Any]])
async def get_lead_signals(lead_id: int, db: Session = Depends(get_db)):
    """Get signals for a specific lead."""
    try:
        signals = db.query(Signal).filter(Signal.lead_id == lead_id).order_by(Signal.created_at.desc()).all()
        
        return [
            {
                "id": signal.id,
                "signal_type": signal.signal_type,
                "source": signal.source,
                "content": signal.content,
                "confidence": signal.confidence,
                "relevance_score": signal.relevance_score,
                "metadata": signal.metadata,
                "keywords_found": signal.keywords_found,
                "signal_date": signal.signal_date.isoformat() if signal.signal_date else None,
                "created_at": signal.created_at.isoformat()
            }
            for signal in signals
        ]
    except Exception as e:
        logger.error(f"Error getting signals for lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Content Generation Endpoints
@app.post("/leads/{lead_id}/generate-content")
async def generate_outreach_content(
    lead_id: int,
    contact_info: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Generate outreach content for a lead."""
    try:
        # Verify lead exists
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Generate content
        content = content_generator.generate_outreach_content(lead_id, contact_info)
        
        return {
            "lead_id": lead_id,
            "contact_info": contact_info,
            "content": content
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating content for lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Outreach Management Endpoints
@app.post("/leads/{lead_id}/outreach")
async def create_outreach(
    lead_id: int,
    outreach_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Create a new outreach attempt."""
    try:
        # Verify lead exists
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Create outreach record
        outreach = Outreach(
            lead_id=lead_id,
            channel=outreach_data["channel"],
            content=outreach_data["content"],
            status=outreach_data.get("status", "pending"),
            delivery_metadata=outreach_data.get("metadata", {}),
            subject_line=outreach_data.get("subject_line"),
            recipient_email=outreach_data.get("recipient_email"),
            recipient_name=outreach_data.get("recipient_name")
        )
        
        db.add(outreach)
        db.commit()
        db.refresh(outreach)
        
        return {"id": outreach.id, "message": "Outreach created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating outreach for lead {lead_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/leads/{lead_id}/outreach", response_model=List[Dict[str, Any]])
async def get_lead_outreach(lead_id: int, db: Session = Depends(get_db)):
    """Get outreach attempts for a lead."""
    try:
        outreaches = db.query(Outreach).filter(Outreach.lead_id == lead_id).order_by(Outreach.created_at.desc()).all()
        
        return [
            {
                "id": outreach.id,
                "channel": outreach.channel,
                "content": outreach.content,
                "status": outreach.status,
                "metadata": outreach.metadata,
                "subject_line": outreach.subject_line,
                "recipient_email": outreach.recipient_email,
                "recipient_name": outreach.recipient_name,
                "response_content": outreach.response_content,
                "response_sentiment": outreach.response_sentiment,
                "response_score": outreach.response_score,
                "created_at": outreach.created_at.isoformat(),
                "sent_at": outreach.sent_at.isoformat() if outreach.sent_at else None,
                "delivered_at": outreach.delivered_at.isoformat() if outreach.delivered_at else None,
                "opened_at": outreach.opened_at.isoformat() if outreach.opened_at else None,
                "replied_at": outreach.replied_at.isoformat() if outreach.replied_at else None
            }
            for outreach in outreaches
        ]
    except Exception as e:
        logger.error(f"Error getting outreach for lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Analytics Endpoints
@app.get("/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get analytics overview."""
    try:
        # Get basic counts
        total_leads = db.query(Lead).count()
        high_intent_leads = db.query(Lead).filter(Lead.intent_score >= settings.scoring.high_intent_threshold).count()
        total_signals = db.query(Signal).count()
        total_outreach = db.query(Outreach).count()
        
        # Get recent activity
        recent_signals = db.query(Signal).filter(
            Signal.created_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        recent_outreach = db.query(Outreach).filter(
            Outreach.created_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        return {
            "total_leads": total_leads,
            "high_intent_leads": high_intent_leads,
            "total_signals": total_signals,
            "total_outreach": total_outreach,
            "recent_signals_7d": recent_signals,
            "recent_outreach_7d": recent_outreach,
            "high_intent_threshold": settings.scoring.high_intent_threshold
        }
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/analytics/signals-by-type")
async def get_signals_by_type(db: Session = Depends(get_db)):
    """Get signal counts by type."""
    try:
        from sqlalchemy import func
        
        signal_counts = db.query(
            Signal.signal_type,
            func.count(Signal.id).label('count')
        ).group_by(Signal.signal_type).all()
        
        return [
            {"signal_type": signal_type, "count": count}
            for signal_type, count in signal_counts
        ]
    except Exception as e:
        logger.error(f"Error getting signals by type: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

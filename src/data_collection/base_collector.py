#!/usr/bin/env python3
"""
Base collector class for all data collection modules.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from src.core.database import get_db, Signal


class BaseCollector(ABC):
    """Base class for all data collectors."""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    def collect_signals_for_lead(self, lead) -> List[Dict[str, Any]]:
        """Collect signals for a specific lead. Must be implemented by subclasses."""
        pass
    
    def save_signals_to_db(self, lead_id: int, signals: List[Dict[str, Any]]) -> None:
        """Save collected signals to the database."""
        if not signals:
            return
            
        try:
            db = next(get_db())
            try:
                for signal_data in signals:
                    signal = Signal(
                        lead_id=lead_id,
                        signal_type=signal_data['signal_type'],
                        source=self.name,
                        content=signal_data['content'],
                        confidence=signal_data['confidence'],
                        signal_metadata=signal_data.get('metadata', {}),
                        keywords_found=signal_data.get('keywords_found', []),
                        signal_date=signal_data.get('metadata', {}).get('date', datetime.now())
                    )
                    db.add(signal)
                
                db.commit()
                logger.info(f"Saved {len(signals)} signals from {self.name} for lead {lead_id}")
                
            except Exception as e:
                logger.error(f"Error saving signals to database: {e}")
                db.rollback()
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting database session: {e}")
    
    def validate_signal_data(self, signal_data: Dict[str, Any]) -> bool:
        """Validate signal data structure."""
        required_fields = ['signal_type', 'content', 'confidence']
        return all(field in signal_data for field in required_fields)
    
    def clean_content(self, content: str, max_length: int = 1000) -> str:
        """Clean and truncate content."""
        if not content:
            return ""
        
        # Remove extra whitespace
        content = ' '.join(content.split())
        
        # Truncate if too long
        if len(content) > max_length:
            content = content[:max_length] + "..."
            
        return content
    
    def calculate_confidence(self, factors: Dict[str, float]) -> float:
        """Calculate confidence score based on multiple factors."""
        if not factors:
            return 0.0
            
        # Simple weighted average
        total_weight = sum(factors.values())
        if total_weight == 0:
            return 0.0
            
        weighted_sum = sum(score * weight for score, weight in factors.items())
        confidence = weighted_sum / total_weight
        
        return min(max(confidence, 0.0), 1.0)

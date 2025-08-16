#!/usr/bin/env python3
"""
Company Intelligence collector using Logo.dev API.
Uses Logo.dev (free tier) for company data and logos
"""

import requests
import time
from typing import List, Dict, Any
from loguru import logger
from ..core.config import get_settings
from ..core.database import get_db, Signal, Lead
from .base_collector import BaseCollector


class CompanyIntelligenceCollector(BaseCollector):
    """Collects company intelligence data using Logo.dev API."""
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.api_key = self.settings.logo_dev_api_key
        self.base_url = "https://api.logo.dev"
        self.session = requests.Session()
        
    def collect_signals_for_lead(self, lead: Lead) -> List[Dict[str, Any]]:
        """Collect company intelligence signals for a specific lead."""
        signals = []
        
        if not self.api_key or self.api_key == "your_logo_dev_api_key_here":
            logger.warning("Logo.dev API key not configured, skipping company intelligence collection")
            return signals
            
        try:
            # Get company data and logo
            company_signals = self._analyze_company_data(lead)
            signals.extend(company_signals)
            
            # Analyze company description and keywords
            description_signals = self._analyze_company_description(lead)
            signals.extend(description_signals)
            
            logger.info(f"Collected {len(signals)} company intelligence signals for {lead.company_name}")
            
        except Exception as e:
            logger.error(f"Error collecting company intelligence for {lead.company_name}: {e}")
            
        return signals
    
    def _analyze_company_data(self, lead: Lead) -> List[Dict[str, Any]]:
        """Analyze company data from Logo.dev."""
        signals = []
        
        try:
            # Get company logo and basic data
            params = {
                'token': self.api_key,
                'domain': lead.domain
            }
            
            response = self.session.get(f"{self.base_url}/logo", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                # Create signal for company data
                signal = self._create_company_data_signal(data, lead)
                if signal:
                    signals.append(signal)
                    
                # Check if company has security-related keywords in description
                if data.get('description'):
                    security_signal = self._create_security_keyword_signal(data['description'], lead)
                    if security_signal:
                        signals.append(security_signal)
                        
        except Exception as e:
            logger.error(f"Error analyzing company data for {lead.domain}: {e}")
            
        return signals
    
    def _analyze_company_description(self, lead: Lead) -> List[Dict[str, Any]]:
        """Analyze company description for relevant keywords."""
        signals = []
        
        try:
            # Get additional company information
            params = {
                'token': self.api_key,
                'domain': lead.domain
            }
            
            response = self.session.get(f"{self.base_url}/company", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success') and data.get('description'):
                # Analyze description for security/tech keywords
                signal = self._create_description_analysis_signal(data['description'], lead)
                if signal:
                    signals.append(signal)
                    
        except Exception as e:
            logger.error(f"Error analyzing company description for {lead.domain}: {e}")
            
        return signals
    
    def _create_company_data_signal(self, data: Dict, lead: Lead) -> Dict[str, Any]:
        """Create a signal from company data analysis."""
        try:
            # Calculate relevance based on company data
            relevance_score = self._calculate_company_relevance(data, lead)
            
            # Extract relevant keywords
            keywords = self._extract_company_keywords(data)
            
            return {
                'signal_type': 'company_intelligence',
                'content': f"Company intelligence for {lead.company_name}: {data.get('description', 'No description available')}",
                'confidence': relevance_score,
                'keywords_found': keywords,
                'metadata': {
                    'logo_url': data.get('logo'),
                    'description': data.get('description'),
                    'industry': data.get('industry'),
                    'date': time.time()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating company data signal: {e}")
            return None
    
    def _create_security_keyword_signal(self, description: str, lead: Lead) -> Dict[str, Any]:
        """Create a signal if security keywords are found in description."""
        try:
            security_keywords = [
                'security', 'authentication', 'identity', 'auth', 'sso', 'oauth',
                'cybersecurity', 'data protection', 'privacy', 'compliance',
                'encryption', 'access control', 'user management'
            ]
            
            found_keywords = []
            description_lower = description.lower()
            
            for keyword in security_keywords:
                if keyword in description_lower:
                    found_keywords.append(keyword)
            
            if found_keywords:
                return {
                    'signal_type': 'security_keywords',
                    'content': f"Security-related keywords found in {lead.company_name} description: {', '.join(found_keywords)}",
                    'confidence': 0.8,
                    'keywords_found': found_keywords,
                    'metadata': {
                        'description': description,
                        'keywords_found': found_keywords,
                        'date': time.time()
                    }
                }
                
        except Exception as e:
            logger.error(f"Error creating security keyword signal: {e}")
            
        return None
    
    def _create_description_analysis_signal(self, description: str, lead: Lead) -> Dict[str, Any]:
        """Create a signal from description analysis."""
        try:
            # Analyze description for tech stack and industry relevance
            tech_keywords = [
                'software', 'platform', 'solution', 'technology', 'digital',
                'cloud', 'saas', 'api', 'integration', 'automation'
            ]
            
            found_tech = []
            description_lower = description.lower()
            
            for keyword in tech_keywords:
                if keyword in description_lower:
                    found_tech.append(keyword)
            
            relevance_score = min(len(found_tech) * 0.2, 1.0)
            
            return {
                'signal_type': 'description_analysis',
                'content': f"Tech-focused description analysis for {lead.company_name}: {', '.join(found_tech)}",
                'confidence': relevance_score,
                'keywords_found': found_tech,
                'metadata': {
                    'description': description,
                    'tech_keywords': found_tech,
                    'date': time.time()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating description analysis signal: {e}")
            return None
    
    def _calculate_company_relevance(self, data: Dict, lead: Lead) -> float:
        """Calculate relevance score based on company data."""
        score = 0.0
        
        # Check if company has a description
        if data.get('description'):
            score += 0.3
            
        # Check if company has a logo (indicates established company)
        if data.get('logo'):
            score += 0.2
            
        # Check for security-related keywords in description
        if data.get('description'):
            description_lower = data['description'].lower()
            security_terms = ['security', 'authentication', 'identity', 'auth']
            for term in security_terms:
                if term in description_lower:
                    score += 0.3
                    break
                    
        # Check for tech-related keywords
        if data.get('description'):
            description_lower = data['description'].lower()
            tech_terms = ['software', 'platform', 'technology', 'digital']
            for term in tech_terms:
                if term in description_lower:
                    score += 0.2
                    break
                    
        return min(score, 1.0)
    
    def _extract_company_keywords(self, data: Dict) -> List[str]:
        """Extract relevant keywords from company data."""
        keywords = []
        
        if data.get('description'):
            description_lower = data['description'].lower()
            
            # Security-related keywords
            security_keywords = ['security', 'authentication', 'identity', 'auth', 'sso', 'oauth']
            for keyword in security_keywords:
                if keyword in description_lower:
                    keywords.append(keyword)
                    
            # Tech-related keywords
            tech_keywords = ['software', 'platform', 'technology', 'digital', 'cloud', 'saas']
            for keyword in tech_keywords:
                if keyword in description_lower:
                    keywords.append(keyword)
                    
        return list(set(keywords))[:5]  # Remove duplicates and limit


# Factory function
def create_company_intelligence_collector() -> CompanyIntelligenceCollector:
    """Create and return a company intelligence collector instance."""
    return CompanyIntelligenceCollector()

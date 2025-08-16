#!/usr/bin/env python3
"""
News API collector for gathering company mentions and security-related news.
Uses NewsAPI (free tier: 1,000 requests/day)
"""

import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from loguru import logger
from ..core.config import get_settings
from ..core.database import get_db, Signal, Lead
from .base_collector import BaseCollector


class NewsCollector(BaseCollector):
    """Collects news mentions and security-related articles."""
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.api_key = self.settings.news_api_key
        self.base_url = "https://newsapi.org/v2"
        self.session = requests.Session()
        
    def collect_signals_for_lead(self, lead: Lead) -> List[Dict[str, Any]]:
        """Collect news signals for a specific lead."""
        signals = []
        
        if not self.api_key or self.api_key == "your_news_api_key_here":
            logger.warning("News API key not configured, skipping news collection")
            return signals
            
        try:
            # Search for company mentions
            company_signals = self._search_company_mentions(lead)
            signals.extend(company_signals)
            
            # Search for security-related news in the industry
            security_signals = self._search_security_news(lead)
            signals.extend(security_signals)
            
            # Search for authentication/identity news
            auth_signals = self._search_auth_news(lead)
            signals.extend(auth_signals)
            
            logger.info(f"Collected {len(signals)} news signals for {lead.company_name}")
            
        except Exception as e:
            logger.error(f"Error collecting news signals for {lead.company_name}: {e}")
            
        return signals
    
    def _search_company_mentions(self, lead: Lead) -> List[Dict[str, Any]]:
        """Search for direct company mentions."""
        signals = []
        
        # Search for company name and domain
        search_terms = [lead.company_name, lead.domain]
        
        for term in search_terms:
            try:
                params = {
                    'q': term,
                    'apiKey': self.api_key,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 10,
                    'from': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                }
                
                response = self.session.get(f"{self.base_url}/everything", params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') == 'ok' and data.get('articles'):
                    for article in data['articles']:
                        signal = self._create_signal_from_article(article, lead, 'company_mention')
                        if signal:
                            signals.append(signal)
                            
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error searching for company mentions '{term}': {e}")
                
        return signals
    
    def _search_security_news(self, lead: Lead) -> List[Dict[str, Any]]:
        """Search for security-related news in the lead's industry."""
        signals = []
        
        # Security keywords relevant to the industry
        security_keywords = [
            "authentication", "authorization", "identity management",
            "single sign-on", "SSO", "OAuth", "SAML", "JWT",
            "password security", "multi-factor authentication", "MFA",
            "zero trust", "API security", "data breach", "cybersecurity"
        ]
        
        # Industry-specific keywords
        industry_keywords = {
            "Technology": ["SaaS security", "cloud security", "devops security"],
            "Finance": ["fintech security", "payment security", "compliance"],
            "Healthcare": ["HIPAA", "healthcare security", "patient data"],
            "default": ["enterprise security", "business security"]
        }
        
        keywords = security_keywords + industry_keywords.get(lead.industry, industry_keywords["default"])
        
        for keyword in keywords[:5]:  # Limit to avoid rate limits
            try:
                params = {
                    'q': f'"{keyword}" AND "{lead.industry}"',
                    'apiKey': self.api_key,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 5,
                    'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                }
                
                response = self.session.get(f"{self.base_url}/everything", params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') == 'ok' and data.get('articles'):
                    for article in data['articles']:
                        signal = self._create_signal_from_article(article, lead, 'security_news')
                        if signal:
                            signals.append(signal)
                            
                # Rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                logger.error(f"Error searching for security news '{keyword}': {e}")
                
        return signals
    
    def _search_auth_news(self, lead: Lead) -> List[Dict[str, Any]]:
        """Search for authentication and identity management news."""
        signals = []
        
        auth_keywords = [
            "authentication platform", "identity provider", "IdP",
            "user management", "access control", "identity verification"
        ]
        
        for keyword in auth_keywords[:3]:  # Limit to avoid rate limits
            try:
                params = {
                    'q': keyword,
                    'apiKey': self.api_key,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 3,
                    'from': (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
                }
                
                response = self.session.get(f"{self.base_url}/everything", params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') == 'ok' and data.get('articles'):
                    for article in data['articles']:
                        signal = self._create_signal_from_article(article, lead, 'auth_news')
                        if signal:
                            signals.append(signal)
                            
                # Rate limiting
                time.sleep(0.3)
                
            except Exception as e:
                logger.error(f"Error searching for auth news '{keyword}': {e}")
                
        return signals
    
    def _create_signal_from_article(self, article: Dict, lead: Lead, signal_type: str) -> Dict[str, Any]:
        """Create a signal from a news article."""
        try:
            # Calculate relevance score based on content
            content = f"{article.get('title', '')} {article.get('description', '')}"
            relevance_score = self._calculate_relevance(content, lead)
            
            if relevance_score < 0.3:  # Only include relevant articles
                return None
                
            # Extract keywords
            keywords = self._extract_keywords(content)
            
            return {
                'signal_type': signal_type,
                'content': content[:500],  # Truncate for database
                'confidence': relevance_score,
                'keywords_found': keywords,
                'metadata': {
                    'title': article.get('title'),
                    'url': article.get('url'),
                    'source': article.get('source', {}).get('name'),
                    'published_at': article.get('publishedAt'),
                    'date': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating signal from article: {e}")
            return None
    
    def _calculate_relevance(self, content: str, lead: Lead) -> float:
        """Calculate relevance score for content."""
        content_lower = content.lower()
        score = 0.0
        
        # Company relevance
        if lead.company_name.lower() in content_lower:
            score += 0.4
        if lead.domain.lower() in content_lower:
            score += 0.3
            
        # Industry relevance
        if lead.industry.lower() in content_lower:
            score += 0.2
            
        # Security relevance
        security_terms = ['security', 'authentication', 'identity', 'auth', 'sso', 'oauth']
        for term in security_terms:
            if term in content_lower:
                score += 0.1
                break
                
        return min(score, 1.0)
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords from content."""
        keywords = []
        content_lower = content.lower()
        
        # Security-related keywords
        security_keywords = [
            'authentication', 'authorization', 'identity', 'security',
            'sso', 'oauth', 'saml', 'jwt', 'mfa', 'password', 'login'
        ]
        
        for keyword in security_keywords:
            if keyword in content_lower:
                keywords.append(keyword)
                
        return keywords[:5]  # Limit to top 5 keywords


# Factory function
def create_news_collector() -> NewsCollector:
    """Create and return a news collector instance."""
    return NewsCollector()

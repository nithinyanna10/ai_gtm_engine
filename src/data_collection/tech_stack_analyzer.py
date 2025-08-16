#!/usr/bin/env python3
"""
Simple Tech Stack Analyzer using web scraping and pattern matching.
Free alternative to BuiltWith/Wappalyzer APIs
"""

import requests
import re
from typing import List, Dict, Any
from loguru import logger
from ..core.config import get_settings
from ..core.database import get_db, Signal, Lead
from .base_collector import BaseCollector
import time


class TechStackAnalyzer(BaseCollector):
    """Analyzes tech stack using web scraping and pattern matching."""
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Common technology patterns
        self.tech_patterns = {
            'frameworks': {
                'React': [r'react', r'__REACT_DEVTOOLS_GLOBAL_HOOK__'],
                'Vue.js': [r'vue', r'__VUE__'],
                'Angular': [r'angular', r'ng-'],
                'Django': [r'django', r'csrfmiddlewaretoken'],
                'Flask': [r'flask', r'werkzeug'],
                'Express': [r'express', r'__express'],
                'Laravel': [r'laravel', r'XSRF-TOKEN'],
                'Ruby on Rails': [r'rails', r'_rails'],
                'Spring': [r'spring', r'org.springframework'],
                'ASP.NET': [r'asp\.net', r'__VIEWSTATE']
            },
            'databases': {
                'PostgreSQL': [r'postgresql', r'postgres'],
                'MySQL': [r'mysql', r'mysqli'],
                'MongoDB': [r'mongodb', r'mongo'],
                'Redis': [r'redis', r'redis-cli'],
                'SQLite': [r'sqlite', r'sqlite3'],
                'Oracle': [r'oracle', r'oracle\.com'],
                'SQL Server': [r'sql server', r'microsoft\.sql']
            },
            'cloud_platforms': {
                'AWS': [r'aws', r'amazonaws\.com', r'cloudfront'],
                'Azure': [r'azure', r'microsoft\.com/azure'],
                'Google Cloud': [r'gcp', r'googleapis\.com', r'google\.com/cloud'],
                'Heroku': [r'heroku', r'herokuapp\.com'],
                'Vercel': [r'vercel', r'vercel\.app'],
                'Netlify': [r'netlify', r'netlify\.app']
            },
            'security': {
                'Auth0': [r'auth0', r'auth0\.com'],
                'Okta': [r'okta', r'okta\.com'],
                'OneLogin': [r'onelogin', r'onelogin\.com'],
                'Ping Identity': [r'ping', r'pingidentity\.com'],
                'Azure AD': [r'azure ad', r'microsoft\.com/identity'],
                'AWS Cognito': [r'cognito', r'cognito-idp'],
                'Firebase Auth': [r'firebase', r'firebase\.google\.com']
            },
            'analytics': {
                'Google Analytics': [r'ga\(', r'google-analytics', r'gtag'],
                'Mixpanel': [r'mixpanel', r'mixpanel\.com'],
                'Segment': [r'segment', r'segment\.com'],
                'Hotjar': [r'hotjar', r'hotjar\.com'],
                'FullStory': [r'fullstory', r'fullstory\.com']
            }
        }
        
    def collect_signals_for_lead(self, lead: Lead) -> List[Dict[str, Any]]:
        """Collect tech stack signals for a specific lead."""
        signals = []
        
        try:
            # Analyze website for tech stack
            tech_signals = self._analyze_website_tech(lead)
            signals.extend(tech_signals)
            
            # Analyze for security technologies
            security_signals = self._analyze_security_tech(lead)
            signals.extend(security_signals)
            
            logger.info(f"Collected {len(signals)} tech stack signals for {lead.company_name}")
            
        except Exception as e:
            logger.error(f"Error collecting tech stack for {lead.company_name}: {e}")
            
        return signals
    
    def _analyze_website_tech(self, lead: Lead) -> List[Dict[str, Any]]:
        """Analyze website for technology stack."""
        signals = []
        
        try:
            # Try to fetch the website
            url = f"https://{lead.domain}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                html_content = response.text.lower()
                headers = dict(response.headers)
                
                # Analyze HTML content
                html_signals = self._analyze_html_content(html_content, lead)
                signals.extend(html_signals)
                
                # Analyze HTTP headers
                header_signals = self._analyze_http_headers(headers, lead)
                signals.extend(header_signals)
                
        except Exception as e:
            logger.error(f"Error analyzing website for {lead.domain}: {e}")
            
        return signals
    
    def _analyze_html_content(self, html_content: str, lead: Lead) -> List[Dict[str, Any]]:
        """Analyze HTML content for technology patterns."""
        signals = []
        found_tech = {}
        
        # Check each technology category
        for category, technologies in self.tech_patterns.items():
            category_tech = []
            
            for tech_name, patterns in technologies.items():
                for pattern in patterns:
                    if re.search(pattern, html_content, re.IGNORECASE):
                        category_tech.append(tech_name)
                        break
            
            if category_tech:
                found_tech[category] = category_tech
        
        # Create signals for found technologies
        if found_tech:
            signal = self._create_tech_stack_signal(found_tech, lead)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _analyze_http_headers(self, headers: Dict[str, str], lead: Lead) -> List[Dict[str, Any]]:
        """Analyze HTTP headers for technology indicators."""
        signals = []
        found_tech = {}
        
        # Check for common header-based technology indicators
        header_indicators = {
            'frameworks': {
                'Django': ['csrftoken', 'sessionid'],
                'Laravel': ['laravel_session', 'XSRF-TOKEN'],
                'Express': ['express', 'connect.sid'],
                'ASP.NET': ['ASP.NET_SessionId', '__VIEWSTATE']
            },
            'security': {
                'Cloudflare': ['cf-ray', 'cf-cache-status'],
                'AWS': ['x-amz-cf-id', 'x-amz-id-2'],
                'Azure': ['x-azure-ref', 'x-ms-version']
            }
        }
        
        for category, technologies in header_indicators.items():
            category_tech = []
            
            for tech_name, indicators in technologies.items():
                for indicator in indicators:
                    if any(indicator.lower() in key.lower() for key in headers.keys()):
                        category_tech.append(tech_name)
                        break
            
            if category_tech:
                found_tech[category] = category_tech
        
        # Create signals for header-based technologies
        if found_tech:
            signal = self._create_header_tech_signal(found_tech, lead)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _analyze_security_tech(self, lead: Lead) -> List[Dict[str, Any]]:
        """Analyze for security-related technologies."""
        signals = []
        
        try:
            # Check for common security endpoints
            security_endpoints = [
                '/auth', '/login', '/oauth', '/saml', '/sso',
                '/admin', '/api/auth', '/identity', '/user'
            ]
            
            found_endpoints = []
            base_url = f"https://{lead.domain}"
            
            for endpoint in security_endpoints:
                try:
                    response = self.session.head(f"{base_url}{endpoint}", timeout=5)
                    if response.status_code in [200, 301, 302, 401, 403]:
                        found_endpoints.append(endpoint)
                except:
                    continue
            
            if found_endpoints:
                signal = self._create_security_endpoint_signal(found_endpoints, lead)
                if signal:
                    signals.append(signal)
                    
        except Exception as e:
            logger.error(f"Error analyzing security tech for {lead.domain}: {e}")
            
        return signals
    
    def _create_tech_stack_signal(self, found_tech: Dict[str, List[str]], lead: Lead) -> Dict[str, Any]:
        """Create a signal from tech stack analysis."""
        try:
            # Calculate relevance score
            total_tech = sum(len(techs) for techs in found_tech.values())
            relevance_score = min(total_tech * 0.2, 1.0)
            
            # Format content
            tech_summary = []
            for category, techs in found_tech.items():
                tech_summary.append(f"{category}: {', '.join(techs)}")
            
            content = f"Tech stack analysis for {lead.company_name}: {'; '.join(tech_summary)}"
            
            # Extract keywords
            keywords = []
            for techs in found_tech.values():
                keywords.extend(techs)
            
            return {
                'signal_type': 'tech_stack_analysis',
                'content': content,
                'confidence': relevance_score,
                'keywords_found': keywords[:10],  # Limit keywords
                'metadata': {
                    'technologies': found_tech,
                    'total_technologies': total_tech,
                    'date': time.time()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating tech stack signal: {e}")
            return None
    
    def _create_header_tech_signal(self, found_tech: Dict[str, List[str]], lead: Lead) -> Dict[str, Any]:
        """Create a signal from header-based technology analysis."""
        try:
            tech_summary = []
            for category, techs in found_tech.items():
                tech_summary.append(f"{category}: {', '.join(techs)}")
            
            content = f"Header-based tech detection for {lead.company_name}: {'; '.join(tech_summary)}"
            
            keywords = []
            for techs in found_tech.values():
                keywords.extend(techs)
            
            return {
                'signal_type': 'header_technology',
                'content': content,
                'confidence': 0.7,
                'keywords_found': keywords,
                'metadata': {
                    'header_technologies': found_tech,
                    'date': time.time()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating header tech signal: {e}")
            return None
    
    def _create_security_endpoint_signal(self, endpoints: List[str], lead: Lead) -> Dict[str, Any]:
        """Create a signal from security endpoint analysis."""
        try:
            content = f"Security endpoints detected for {lead.company_name}: {', '.join(endpoints)}"
            
            return {
                'signal_type': 'security_endpoints',
                'content': content,
                'confidence': 0.6,
                'keywords_found': endpoints,
                'metadata': {
                    'security_endpoints': endpoints,
                    'date': time.time()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating security endpoint signal: {e}")
            return None


# Factory function
def create_tech_stack_analyzer() -> TechStackAnalyzer:
    """Create and return a tech stack analyzer instance."""
    return TechStackAnalyzer()

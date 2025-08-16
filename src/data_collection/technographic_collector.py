#!/usr/bin/env python3
"""
Technographic collector using BuiltWith API to analyze company tech stacks.
Uses BuiltWith (free tier: 100 requests/month)
"""

import requests
import time
from typing import List, Dict, Any
from loguru import logger
from src.core.config import get_settings
from src.core.database import get_db, Signal, Lead
from src.data_collection.base_collector import BaseCollector


class TechnographicCollector(BaseCollector):
    """Collects technographic data using BuiltWith API."""
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.api_key = self.settings.builtwith_api_key
        self.base_url = "https://api.builtwith.com/v20"
        self.session = requests.Session()
        
    def collect_signals_for_lead(self, lead: Lead) -> List[Dict[str, Any]]:
        """Collect technographic signals for a specific lead."""
        signals = []
        
        if not self.api_key or self.api_key == "your_builtwith_api_key_here":
            logger.warning("BuiltWith API key not configured, skipping technographic collection")
            return signals
            
        try:
            # Get tech stack for the company domain
            tech_signals = self._analyze_tech_stack(lead)
            signals.extend(tech_signals)
            
            # Analyze security technologies
            security_signals = self._analyze_security_tech(lead)
            signals.extend(security_signals)
            
            # Check for authentication/identity technologies
            auth_signals = self._analyze_auth_tech(lead)
            signals.extend(auth_signals)
            
            logger.info(f"Collected {len(signals)} technographic signals for {lead.company_name}")
            
        except Exception as e:
            logger.error(f"Error collecting technographic signals for {lead.company_name}: {e}")
            
        return signals
    
    def _analyze_tech_stack(self, lead: Lead) -> List[Dict[str, Any]]:
        """Analyze the overall tech stack of the company."""
        signals = []
        
        try:
            params = {
                'KEY': self.api_key,
                'LOOKUP': lead.domain
            }
            
            response = self.session.get(f"{self.base_url}/api.json", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('Results'):
                result = data['Results'][0]
                paths = result.get('Paths', [])
                
                # Extract all technologies
                all_tech = []
                for path in paths:
                    technologies = path.get('Technologies', [])
                    for tech in technologies:
                        all_tech.append({
                            'name': tech.get('Name'),
                            'category': tech.get('Categories', [{}])[0].get('Name'),
                            'description': tech.get('Description')
                        })
                
                # Create signal for tech stack analysis
                if all_tech:
                    signal = self._create_tech_stack_signal(all_tech, lead)
                    if signal:
                        signals.append(signal)
                        
        except Exception as e:
            logger.error(f"Error analyzing tech stack for {lead.domain}: {e}")
            
        return signals
    
    def _analyze_security_tech(self, lead: Lead) -> List[Dict[str, Any]]:
        """Analyze security-related technologies."""
        signals = []
        
        try:
            params = {
                'KEY': self.api_key,
                'LOOKUP': lead.domain,
                'CATEGORY': 'Security'
            }
            
            response = self.session.get(f"{self.base_url}/api.json", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('Results'):
                result = data['Results'][0]
                paths = result.get('Paths', [])
                
                security_tech = []
                for path in paths:
                    technologies = path.get('Technologies', [])
                    for tech in technologies:
                        security_tech.append({
                            'name': tech.get('Name'),
                            'description': tech.get('Description')
                        })
                
                if security_tech:
                    signal = self._create_security_tech_signal(security_tech, lead)
                    if signal:
                        signals.append(signal)
                        
        except Exception as e:
            logger.error(f"Error analyzing security tech for {lead.domain}: {e}")
            
        return signals
    
    def _analyze_auth_tech(self, lead: Lead) -> List[Dict[str, Any]]:
        """Analyze authentication and identity technologies."""
        signals = []
        
        # Auth-related categories to check
        auth_categories = ['Authentication', 'Identity', 'SSO', 'OAuth']
        
        for category in auth_categories:
            try:
                params = {
                    'KEY': self.api_key,
                    'LOOKUP': lead.domain,
                    'CATEGORY': category
                }
                
                response = self.session.get(f"{self.base_url}/api.json", params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('Results'):
                    result = data['Results'][0]
                    paths = result.get('Paths', [])
                    
                    auth_tech = []
                    for path in paths:
                        technologies = path.get('Technologies', [])
                        for tech in technologies:
                            auth_tech.append({
                                'name': tech.get('Name'),
                                'description': tech.get('Description')
                            })
                    
                    if auth_tech:
                        signal = self._create_auth_tech_signal(auth_tech, lead, category)
                        if signal:
                            signals.append(signal)
                            
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error analyzing auth tech for {lead.domain} category {category}: {e}")
                
        return signals
    
    def _create_tech_stack_signal(self, technologies: List[Dict], lead: Lead) -> Dict[str, Any]:
        """Create a signal from tech stack analysis."""
        try:
            # Calculate tech stack relevance
            tech_names = [tech['name'] for tech in technologies if tech['name']]
            relevance_score = self._calculate_tech_relevance(tech_names, lead)
            
            # Extract relevant keywords
            keywords = self._extract_tech_keywords(technologies)
            
            return {
                'signal_type': 'tech_stack_analysis',
                'content': f"Tech stack analysis for {lead.company_name}: {', '.join(tech_names[:10])}",
                'confidence': relevance_score,
                'keywords_found': keywords,
                'metadata': {
                    'technologies': technologies[:20],  # Limit for database
                    'total_technologies': len(technologies),
                    'date': time.time()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating tech stack signal: {e}")
            return None
    
    def _create_security_tech_signal(self, security_tech: List[Dict], lead: Lead) -> Dict[str, Any]:
        """Create a signal from security technology analysis."""
        try:
            tech_names = [tech['name'] for tech in security_tech if tech['name']]
            relevance_score = 0.8 if tech_names else 0.3  # High relevance if security tech found
            
            return {
                'signal_type': 'security_technology',
                'content': f"Security technologies detected for {lead.company_name}: {', '.join(tech_names)}",
                'confidence': relevance_score,
                'keywords_found': tech_names,
                'metadata': {
                    'security_technologies': security_tech,
                    'date': time.time()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating security tech signal: {e}")
            return None
    
    def _create_auth_tech_signal(self, auth_tech: List[Dict], lead: Lead, category: str) -> Dict[str, Any]:
        """Create a signal from authentication technology analysis."""
        try:
            tech_names = [tech['name'] for tech in auth_tech if tech['name']]
            relevance_score = 0.9 if tech_names else 0.2  # Very high relevance for auth tech
            
            return {
                'signal_type': 'auth_technology',
                'content': f"{category} technologies detected for {lead.company_name}: {', '.join(tech_names)}",
                'confidence': relevance_score,
                'keywords_found': tech_names,
                'metadata': {
                    'auth_technologies': auth_tech,
                    'category': category,
                    'date': time.time()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating auth tech signal: {e}")
            return None
    
    def _calculate_tech_relevance(self, tech_names: List[str], lead: Lead) -> float:
        """Calculate relevance score based on tech stack."""
        score = 0.0
        tech_lower = [tech.lower() for tech in tech_names]
        
        # Check for security/identity technologies
        security_tech = ['auth0', 'okta', 'onelogin', 'ping', 'azure ad', 'aws cognito', 'firebase auth']
        for tech in security_tech:
            if any(tech in t for t in tech_lower):
                score += 0.4
                break
                
        # Check for modern web technologies
        modern_tech = ['react', 'vue', 'angular', 'node.js', 'python', 'django', 'flask']
        for tech in modern_tech:
            if any(tech in t for t in tech_lower):
                score += 0.2
                break
                
        # Check for cloud platforms
        cloud_tech = ['aws', 'azure', 'gcp', 'heroku', 'vercel']
        for tech in cloud_tech:
            if any(tech in t for t in tech_lower):
                score += 0.2
                break
                
        return min(score, 1.0)
    
    def _extract_tech_keywords(self, technologies: List[Dict]) -> List[str]:
        """Extract relevant keywords from technologies."""
        keywords = []
        
        for tech in technologies:
            name = tech.get('name', '').lower()
            description = tech.get('description', '').lower()
            
            # Security-related keywords
            security_keywords = ['auth', 'security', 'identity', 'sso', 'oauth', 'saml', 'jwt']
            for keyword in security_keywords:
                if keyword in name or keyword in description:
                    keywords.append(keyword)
                    
        return list(set(keywords))[:5]  # Remove duplicates and limit


# Factory function
def create_technographic_collector() -> TechnographicCollector:
    """Create and return a technographic collector instance."""
    return TechnographicCollector()

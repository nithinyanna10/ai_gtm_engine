"""
Reddit data collector for detecting security and authentication-related discussions.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import praw
from loguru import logger

from ..core.config import get_settings
from ..core.database import Signal, get_db, Lead
from .base_collector import BaseCollector

class RedditCollector(BaseCollector):
    """Collects Reddit data to detect security/auth intent signals."""
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        # Disable Reddit API for now to avoid async issues
        self.reddit = None
        # if self.settings.api.reddit_client_id and self.settings.api.reddit_client_secret:
        #     self.reddit = praw.Reddit(
        #         client_id=self.settings.api.reddit_client_id,
        #         client_secret=self.settings.api.reddit_client_secret,
        #         user_agent=self.settings.api.reddit_user_agent
        #     )
        
        # Subreddits to monitor for security/auth discussions
        self.security_subreddits = [
            'netsec', 'security', 'cybersecurity', 'hacking', 'malware',
            'sysadmin', 'devops', 'programming', 'webdev', 'reactjs',
            'node', 'python', 'javascript', 'aws', 'azure', 'gcp',
            'startups', 'entrepreneur', 'SaaS', 'productivity'
        ]
        
        # Keywords that indicate security/auth challenges
        self.security_keywords = [
            'authentication', 'authorization', 'auth', 'login', 'signin', 'signup',
            'password', 'oauth', 'jwt', 'token', 'session', 'security', 'encryption',
            '2fa', 'mfa', 'two-factor', 'multi-factor', 'sso', 'single-sign-on',
            'identity', 'user management', 'permissions', 'roles', 'rbac',
            'vulnerability', 'breach', 'hack', 'security fix', 'security patch',
            'cve', 'xss', 'csrf', 'sql injection', 'authentication bypass',
            'password reset', 'forgot password', 'user registration',
            'login system', 'auth system', 'identity provider', 'idp'
        ]
        
        # Pain point indicators
        self.pain_point_indicators = [
            'problem', 'issue', 'bug', 'error', 'failing', 'broken',
            'help', 'advice', 'recommendation', 'solution', 'alternative',
            'struggling', 'difficult', 'complex', 'complicated', 'frustrated',
            'annoying', 'pain', 'headache', 'nightmare', 'terrible'
        ]
    
    def collect_signals_for_lead(self, lead: Lead) -> List[Dict[str, Any]]:
        """Collect Reddit signals for a specific lead."""
        signals = []
        
        try:
            # For now, return mock signals to avoid PRAW async issues
            # In production, you'd implement proper async Reddit API calls
            
            mock_signals = [
                {
                    'signal_type': 'reddit_discussion',
                    'source': 'reddit',
                    'content': f"Help with {lead.primary_tech} authentication system",
                    'confidence': 0.7,
                    'signal_date': datetime.now(),
                    'signal_metadata': {
                        'subreddit': 'programming',
                        'post_id': 'mock_123',
                        'url': 'https://reddit.com/r/programming/mock',
                        'score': 15,
                        'comments': 8
                    },
                    'keywords_found': ['authentication', 'login', 'security']
                },
                {
                    'signal_type': 'reddit_discussion',
                    'source': 'reddit',
                    'content': f"{lead.industry} security challenges discussion",
                    'confidence': 0.6,
                    'signal_date': datetime.now(),
                    'signal_metadata': {
                        'subreddit': 'sysadmin',
                        'post_id': 'mock_456',
                        'url': 'https://reddit.com/r/sysadmin/mock',
                        'score': 12,
                        'comments': 5
                    },
                    'keywords_found': ['security', 'challenges', 'industry']
                }
            ]
            
            signals.extend(mock_signals)
            logger.info(f"Generated {len(mock_signals)} mock Reddit signals for {lead.company_name}")
                    
        except Exception as e:
            logger.error(f"Error in Reddit signal collection: {e}")
            
        return signals
    
    def collect_security_discussions(self, company_name: str = None, domain: str = None) -> List[Dict[str, Any]]:
        """Collect security-related discussions from Reddit."""
        signals = []
        
        if not self.reddit:
            logger.warning("Reddit credentials not configured")
            return signals
        
        try:
            # Collect from security-focused subreddits
            for subreddit_name in self.security_subreddits:
                subreddit_signals = self._collect_from_subreddit(
                    subreddit_name, company_name, domain
                )
                signals.extend(subreddit_signals)
            
            # Search for company-specific discussions
            if company_name or domain:
                company_signals = self._search_company_discussions(company_name, domain)
                signals.extend(company_signals)
            
        except Exception as e:
            logger.error(f"Error collecting Reddit data: {e}")
        
        return signals
    
    def _collect_from_subreddit(self, subreddit_name: str, company_name: str = None, domain: str = None) -> List[Dict[str, Any]]:
        """Collect posts from a specific subreddit."""
        signals = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get hot posts
            for post in subreddit.hot(limit=25):
                post_signals = self._analyze_post(post, company_name, domain)
                signals.extend(post_signals)
            
            # Get new posts
            for post in subreddit.new(limit=25):
                post_signals = self._analyze_post(post, company_name, domain)
                signals.extend(post_signals)
            
            # Get top posts from last week
            for post in subreddit.top(time_filter='week', limit=25):
                post_signals = self._analyze_post(post, company_name, domain)
                signals.extend(post_signals)
                
        except Exception as e:
            logger.error(f"Error collecting from subreddit {subreddit_name}: {e}")
        
        return signals
    
    def _analyze_post(self, post, company_name: str = None, domain: str = None) -> List[Dict[str, Any]]:
        """Analyze a Reddit post for security/auth signals."""
        signals = []
        
        try:
            # Combine title and content
            full_text = f"{post.title} {post.selftext}".lower()
            
            # Check for security keywords
            security_keywords_found = [
                keyword for keyword in self.security_keywords 
                if keyword in full_text
            ]
            
            # Check for pain point indicators
            pain_indicators_found = [
                indicator for indicator in self.pain_point_indicators 
                if indicator in full_text
            ]
            
            # Check for company mentions
            company_mentioned = False
            if company_name and company_name.lower() in full_text:
                company_mentioned = True
            if domain and domain.lower() in full_text:
                company_mentioned = True
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(
                security_keywords_found, pain_indicators_found, company_mentioned
            )
            
            if relevance_score > 0.3:  # Only include relevant posts
                signal = {
                    'signal_type': 'reddit_post',
                    'source': f"reddit.com/r/{post.subreddit.display_name}",
                    'content': f"Security discussion: {post.title}",
                    'confidence': relevance_score,
                    'metadata': {
                        'subreddit': post.subreddit.display_name,
                        'post_id': post.id,
                        'post_url': f"https://reddit.com{post.permalink}",
                        'author': str(post.author) if post.author else 'Unknown',
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': datetime.fromtimestamp(post.created_utc),
                        'keywords_found': security_keywords_found,
                        'pain_indicators': pain_indicators_found,
                        'company_mentioned': company_mentioned,
                        'full_text': full_text[:500]  # Truncate for storage
                    }
                }
                signals.append(signal)
            
            # Analyze comments for additional signals
            comment_signals = self._analyze_comments(post, company_name, domain)
            signals.extend(comment_signals)
            
        except Exception as e:
            logger.error(f"Error analyzing Reddit post {post.id}: {e}")
        
        return signals
    
    def _analyze_comments(self, post, company_name: str = None, domain: str = None) -> List[Dict[str, Any]]:
        """Analyze comments for security/auth signals."""
        signals = []
        
        try:
            # Get top comments
            post.comments.replace_more(limit=0)  # Don't expand MoreComments
            
            for comment in post.comments.list()[:10]:  # Limit to top 10 comments
                comment_text = comment.body.lower()
                
                # Check for security keywords
                security_keywords_found = [
                    keyword for keyword in self.security_keywords 
                    if keyword in comment_text
                ]
                
                # Check for pain point indicators
                pain_indicators_found = [
                    indicator for indicator in self.pain_point_indicators 
                    if indicator in comment_text
                ]
                
                # Check for company mentions
                company_mentioned = False
                if company_name and company_name.lower() in comment_text:
                    company_mentioned = True
                if domain and domain.lower() in comment_text:
                    company_mentioned = True
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(
                    security_keywords_found, pain_indicators_found, company_mentioned
                )
                
                if relevance_score > 0.4:  # Higher threshold for comments
                    signal = {
                        'signal_type': 'reddit_comment',
                        'source': f"reddit.com/r/{post.subreddit.display_name}",
                        'content': f"Security comment: {comment.body[:100]}...",
                        'confidence': relevance_score,
                        'metadata': {
                            'subreddit': post.subreddit.display_name,
                            'post_id': post.id,
                            'comment_id': comment.id,
                            'comment_url': f"https://reddit.com{comment.permalink}",
                            'author': str(comment.author) if comment.author else 'Unknown',
                            'score': comment.score,
                            'created_utc': datetime.fromtimestamp(comment.created_utc),
                            'keywords_found': security_keywords_found,
                            'pain_indicators': pain_indicators_found,
                            'company_mentioned': company_mentioned,
                            'comment_text': comment_text[:500]  # Truncate for storage
                        }
                    }
                    signals.append(signal)
        
        except Exception as e:
            logger.error(f"Error analyzing comments for post {post.id}: {e}")
        
        return signals
    
    def _search_company_discussions(self, company_name: str = None, domain: str = None) -> List[Dict[str, Any]]:
        """Search for company-specific discussions."""
        signals = []
        
        if not company_name and not domain:
            return signals
        
        try:
            # Create search queries
            search_queries = []
            if company_name:
                search_queries.extend([
                    f'"{company_name}" authentication',
                    f'"{company_name}" security',
                    f'"{company_name}" auth',
                    f'"{company_name}" login'
                ])
            if domain:
                search_queries.extend([
                    f'"{domain}" authentication',
                    f'"{domain}" security',
                    f'"{domain}" auth'
                ])
            
            # Search across all subreddits
            for query in search_queries:
                try:
                    search_results = self.reddit.subreddit('all').search(
                        query, sort='relevance', time_filter='month', limit=10
                    )
                    
                    for post in search_results:
                        post_signals = self._analyze_post(post, company_name, domain)
                        signals.extend(post_signals)
                
                except Exception as e:
                    logger.warning(f"Reddit search failed for query '{query}': {e}")
        
        except Exception as e:
            logger.error(f"Error searching company discussions: {e}")
        
        return signals
    
    def _calculate_relevance_score(self, security_keywords: List[str], pain_indicators: List[str], company_mentioned: bool) -> float:
        """Calculate relevance score for a post/comment."""
        base_score = 0.1
        
        # Add score for security keywords
        keyword_score = min(len(security_keywords) * 0.15, 0.5)
        
        # Add score for pain indicators
        pain_score = min(len(pain_indicators) * 0.1, 0.3)
        
        # Add score for company mention
        company_score = 0.2 if company_mentioned else 0.0
        
        total_score = base_score + keyword_score + pain_score + company_score
        return min(total_score, 1.0)
    
    def save_signals_to_db(self, lead_id: int, signals: List[Dict[str, Any]]) -> None:
        """Save collected signals to the database."""
        db = next(get_db())
        
        try:
            for signal_data in signals:
                # Check if signal already exists
                existing = db.query(Signal).filter(
                    Signal.lead_id == lead_id,
                    Signal.signal_type == signal_data['signal_type'],
                    Signal.source == signal_data['source'],
                    Signal.content == signal_data['content']
                ).first()
                
                if not existing:
                    signal = Signal(
                        lead_id=lead_id,
                        signal_type=signal_data['signal_type'],
                        source=signal_data['source'],
                        content=signal_data['content'],
                        confidence=signal_data['confidence'],
                        signal_metadata=signal_data.get('metadata', {}),
                        signal_date=signal_data.get('metadata', {}).get('created_utc', datetime.now())
                    )
                    db.add(signal)
            
            db.commit()
            logger.info(f"Saved {len(signals)} Reddit signals for lead {lead_id}")
            
        except Exception as e:
            logger.error(f"Error saving Reddit signals to database: {e}")
            db.rollback()
        finally:
            db.close()

# Global instance
reddit_collector = RedditCollector()

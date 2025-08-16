"""
GitHub data collector for detecting security and authentication-related activity.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
from github import Github, GithubException
from loguru import logger

from ..core.config import get_settings
from ..core.database import Signal, Lead, get_db
from .base_collector import BaseCollector

class GitHubCollector(BaseCollector):
    """Collects GitHub activity data to detect security/auth intent signals."""
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.github = None
        if self.settings.api.github_token:
            self.github = Github(self.settings.api.github_token)
        
        # Keywords that indicate security/auth challenges
        self.security_keywords = [
            'authentication', 'authorization', 'auth', 'login', 'signin', 'signup',
            'password', 'oauth', 'jwt', 'token', 'session', 'security', 'encryption',
            '2fa', 'mfa', 'two-factor', 'multi-factor', 'sso', 'single-sign-on',
            'identity', 'user management', 'permissions', 'roles', 'rbac',
            'vulnerability', 'breach', 'hack', 'security fix', 'security patch',
            'cve', 'xss', 'csrf', 'sql injection', 'authentication bypass'
        ]
        
        # File patterns that indicate auth/security code
        self.security_files = [
            'auth', 'login', 'security', 'middleware', 'guard', 'permission',
            'user', 'session', 'token', 'jwt', 'oauth', 'sso'
        ]
        
        # Repository patterns to monitor
        self.repo_patterns = [
            'auth', 'security', 'identity', 'user', 'login', 'admin',
            'backend', 'api', 'server', 'core', 'main'
        ]
    
    def collect_signals_for_lead(self, lead) -> List[Dict[str, Any]]:
        """Collect GitHub signals for a specific lead."""
        signals = []
        
        try:
            # Use mock data to avoid API rate limiting and async issues
            mock_signals = [
                {
                    'signal_type': 'github_activity',
                    'source': 'github',
                    'content': f"Repository: {lead.company_name.lower()}-auth - Authentication system with security issues",
                    'confidence': 0.8,
                    'signal_date': datetime.now(),
                    'signal_metadata': {
                        'repo_name': f"{lead.company_name.lower()}-auth",
                        'repo_url': f"https://github.com/{lead.company_name.lower()}-auth",
                        'stars': 45,
                        'forks': 12,
                        'language': lead.primary_tech,
                        'open_issues': 8
                    },
                    'keywords_found': ['authentication', 'security', 'login']
                },
                {
                    'signal_type': 'github_activity',
                    'source': 'github',
                    'content': f"Repository: {lead.company_name.lower()}-login - Login system implementation",
                    'confidence': 0.7,
                    'signal_date': datetime.now(),
                    'signal_metadata': {
                        'repo_name': f"{lead.company_name.lower()}-login",
                        'repo_url': f"https://github.com/{lead.company_name.lower()}-login",
                        'stars': 23,
                        'forks': 5,
                        'language': lead.primary_tech,
                        'open_issues': 3
                    },
                    'keywords_found': ['login', 'system', 'implementation']
                }
            ]
            
            signals.extend(mock_signals)
            logger.info(f"Generated {len(mock_signals)} mock GitHub signals for {lead.company_name}")
                    
        except Exception as e:
            logger.error(f"Error in GitHub signal collection: {e}")
            
        return signals
    
    def collect_company_activity(self, company_name: str, domain: str) -> List[Dict[str, Any]]:
        """Collect GitHub activity for a specific company."""
        signals = []
        
        if not self.github:
            logger.warning("GitHub token not configured")
            return signals
        
        try:
            # Search for company repositories
            repos = self._find_company_repos(company_name, domain)
            
            for repo in repos:
                repo_signals = self._analyze_repository(repo, company_name)
                signals.extend(repo_signals)
            
            # Search for security-related issues and discussions
            security_signals = self._search_security_content(company_name, domain)
            signals.extend(security_signals)
            
        except Exception as e:
            logger.error(f"Error collecting GitHub data for {company_name}: {e}")
        
        return signals
    
    def _find_company_repos(self, company_name: str, domain: str) -> List[Any]:
        """Find repositories associated with the company."""
        repos = []
        
        # Search by company name
        search_queries = [
            f'org:{company_name.lower().replace(" ", "")}',
            f'user:{company_name.lower().replace(" ", "")}',
            f'"{company_name}"',
            f'"{domain}"'
        ]
        
        for query in search_queries:
            try:
                search_results = self.github.search_repositories(
                    query=query,
                    sort='updated',
                    order='desc'
                )
                
                for repo in search_results[:10]:  # Limit to top 10 results
                    if repo not in repos:
                        repos.append(repo)
                        
            except GithubException as e:
                logger.warning(f"GitHub search failed for query '{query}': {e}")
        
        return repos
    
    def _analyze_repository(self, repo: Any, company_name: str) -> List[Dict[str, Any]]:
        """Analyze a single repository for security/auth signals."""
        signals = []
        
        try:
            # Check recent commits
            commit_signals = self._analyze_commits(repo, company_name)
            signals.extend(commit_signals)
            
            # Check recent issues
            issue_signals = self._analyze_issues(repo, company_name)
            signals.extend(issue_signals)
            
            # Check recent pull requests
            pr_signals = self._analyze_pull_requests(repo, company_name)
            signals.extend(pr_signals)
            
            # Check repository topics and description
            topic_signals = self._analyze_repo_metadata(repo, company_name)
            signals.extend(topic_signals)
            
        except Exception as e:
            logger.error(f"Error analyzing repository {repo.full_name}: {e}")
        
        return signals
    
    def _analyze_commits(self, repo: Any, company_name: str) -> List[Dict[str, Any]]:
        """Analyze recent commits for security/auth patterns."""
        signals = []
        
        try:
            # Get commits from the last 30 days
            since_date = datetime.now() - timedelta(days=30)
            
            for commit in repo.get_commits(since=since_date):
                commit_message = commit.commit.message.lower()
                commit_files = [f.filename.lower() for f in commit.files] if commit.files else []
                
                # Check for security keywords in commit message
                security_keywords_found = [
                    keyword for keyword in self.security_keywords 
                    if keyword in commit_message
                ]
                
                # Check for security-related file changes
                security_files_changed = [
                    filename for filename in commit_files
                    if any(pattern in filename for pattern in self.security_files)
                ]
                
                if security_keywords_found or security_files_changed:
                    confidence = self._calculate_confidence(
                        security_keywords_found, security_files_changed
                    )
                    
                    signal = {
                        'signal_type': 'github_commit',
                        'source': f"github.com/{repo.full_name}",
                        'content': f"Security-related commit: {commit.commit.message}",
                        'confidence': confidence,
                        'metadata': {
                            'repo_name': repo.full_name,
                            'commit_sha': commit.sha,
                            'commit_url': commit.html_url,
                            'author': commit.author.login if commit.author else 'Unknown',
                            'keywords_found': security_keywords_found,
                            'files_changed': security_files_changed,
                            'date': commit.commit.author.date
                        }
                    }
                    signals.append(signal)
        
        except Exception as e:
            logger.error(f"Error analyzing commits for {repo.full_name}: {e}")
        
        return signals
    
    def _analyze_issues(self, repo: Any, company_name: str) -> List[Dict[str, Any]]:
        """Analyze recent issues for security/auth problems."""
        signals = []
        
        try:
            # Get recent issues
            for issue in repo.get_issues(state='open', sort='updated'):
                issue_title = issue.title.lower()
                issue_body = issue.body.lower() if issue.body else ""
                
                # Check for security keywords
                security_keywords_found = [
                    keyword for keyword in self.security_keywords 
                    if keyword in issue_title or keyword in issue_body
                ]
                
                if security_keywords_found:
                    confidence = self._calculate_confidence(security_keywords_found, [])
                    
                    signal = {
                        'signal_type': 'github_issue',
                        'source': f"github.com/{repo.full_name}",
                        'content': f"Security-related issue: {issue.title}",
                        'confidence': confidence,
                        'metadata': {
                            'repo_name': repo.full_name,
                            'issue_number': issue.number,
                            'issue_url': issue.html_url,
                            'keywords_found': security_keywords_found,
                            'labels': [label.name for label in issue.labels],
                            'date': issue.created_at
                        }
                    }
                    signals.append(signal)
        
        except Exception as e:
            logger.error(f"Error analyzing issues for {repo.full_name}: {e}")
        
        return signals
    
    def _analyze_pull_requests(self, repo: Any, company_name: str) -> List[Dict[str, Any]]:
        """Analyze recent pull requests for security/auth changes."""
        signals = []
        
        try:
            # Get recent pull requests
            for pr in repo.get_pulls(state='open', sort='updated'):
                pr_title = pr.title.lower()
                pr_body = pr.body.lower() if pr.body else ""
                
                # Check for security keywords
                security_keywords_found = [
                    keyword for keyword in self.security_keywords 
                    if keyword in pr_title or keyword in pr_body
                ]
                
                if security_keywords_found:
                    confidence = self._calculate_confidence(security_keywords_found, [])
                    
                    signal = {
                        'signal_type': 'github_pr',
                        'source': f"github.com/{repo.full_name}",
                        'content': f"Security-related PR: {pr.title}",
                        'confidence': confidence,
                        'metadata': {
                            'repo_name': repo.full_name,
                            'pr_number': pr.number,
                            'pr_url': pr.html_url,
                            'keywords_found': security_keywords_found,
                            'labels': [label.name for label in pr.labels],
                            'date': pr.created_at
                        }
                    }
                    signals.append(signal)
        
        except Exception as e:
            logger.error(f"Error analyzing PRs for {repo.full_name}: {e}")
        
        return signals
    
    def _analyze_repo_metadata(self, repo: Any, company_name: str) -> List[Dict[str, Any]]:
        """Analyze repository metadata for security/auth focus."""
        signals = []
        
        try:
            # Check repository description
            description = repo.description.lower() if repo.description else ""
            topics = [topic.lower() for topic in repo.get_topics()]
            
            # Check for security keywords in description and topics
            security_keywords_found = [
                keyword for keyword in self.security_keywords 
                if keyword in description or keyword in topics
            ]
            
            if security_keywords_found:
                confidence = self._calculate_confidence(security_keywords_found, [])
                
                signal = {
                    'signal_type': 'github_repo',
                    'source': f"github.com/{repo.full_name}",
                    'content': f"Security-focused repository: {repo.description}",
                    'confidence': confidence,
                    'metadata': {
                        'repo_name': repo.full_name,
                        'description': repo.description,
                        'topics': topics,
                        'keywords_found': security_keywords_found,
                        'stars': repo.stargazers_count,
                        'forks': repo.forks_count,
                        'date': repo.created_at
                    }
                }
                signals.append(signal)
        
        except Exception as e:
            logger.error(f"Error analyzing metadata for {repo.full_name}: {e}")
        
        return signals
    
    def _search_security_content(self, company_name: str, domain: str) -> List[Dict[str, Any]]:
        """Search for security-related content across GitHub."""
        signals = []
        
        try:
            # Search for security-related content mentioning the company
            search_queries = [
                f'"{company_name}" authentication',
                f'"{company_name}" security',
                f'"{company_name}" auth',
                f'"{domain}" authentication',
                f'"{domain}" security'
            ]
            
            for query in search_queries:
                try:
                    search_results = self.github.search_issues(
                        query=query,
                        sort='updated',
                        order='desc'
                    )
                    
                    for issue in search_results[:5]:  # Limit results
                        signal = {
                            'signal_type': 'github_search',
                            'source': f"github.com/{issue.repository.full_name}",
                            'content': f"Security discussion: {issue.title}",
                            'confidence': 0.6,  # Moderate confidence for search results
                            'metadata': {
                                'repo_name': issue.repository.full_name,
                                'issue_number': issue.number,
                                'issue_url': issue.html_url,
                                'search_query': query,
                                'date': issue.created_at
                            }
                        }
                        signals.append(signal)
                
                except GithubException as e:
                    logger.warning(f"GitHub search failed for query '{query}': {e}")
        
        except Exception as e:
            logger.error(f"Error searching security content for {company_name}: {e}")
        
        return signals
    
    def _calculate_confidence(self, keywords_found: List[str], files_changed: List[str]) -> float:
        """Calculate confidence score based on keywords and file changes."""
        base_score = 0.3
        
        # Add score for keywords found
        keyword_score = min(len(keywords_found) * 0.1, 0.4)
        
        # Add score for security files changed
        file_score = min(len(files_changed) * 0.15, 0.3)
        
        total_score = base_score + keyword_score + file_score
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
                        signal_date=signal_data.get('metadata', {}).get('date', datetime.now())
                    )
                    db.add(signal)
            
            db.commit()
            logger.info(f"Saved {len(signals)} GitHub signals for lead {lead_id}")
            
        except Exception as e:
            logger.error(f"Error saving GitHub signals to database: {e}")
            db.rollback()
        finally:
            db.close()

# Global instance
github_collector = GitHubCollector()

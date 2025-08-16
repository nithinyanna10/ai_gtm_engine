#!/usr/bin/env python3
"""
Flexible email service supporting multiple free email providers.
Supports Mailgun, Resend, and Brevo as free alternatives to SendGrid.
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from loguru import logger
from src.core.config import get_settings


class EmailService:
    """Email service supporting multiple free providers."""
    
    def __init__(self):
        self.settings = get_settings()
        self.session = requests.Session()
        
        # Initialize provider configurations
        self.providers = {
            'mailgun': {
                'api_key': self.settings.mailgun_api_key,
                'domain': self.settings.mailgun_domain,
                'url': None
            },
            'resend': {
                'api_key': self.settings.resend_api_key,
                'url': 'https://api.resend.com/emails'
            },
            'brevo': {
                'api_key': self.settings.brevo_api_key,
                'url': 'https://api.brevo.com/v3/smtp/email'
            }
        }
        
        # Determine which provider to use
        self.active_provider = self._get_active_provider()
        
    def _get_active_provider(self) -> Optional[str]:
        """Determine which email provider is available."""
        for provider, config in self.providers.items():
            if provider == 'mailgun' and config['api_key'] and config['domain']:
                if config['api_key'] != "your_mailgun_api_key_here":
                    return 'mailgun'
            elif provider in ['resend', 'brevo'] and config['api_key']:
                if config['api_key'] != f"your_{provider}_api_key_here":
                    return provider
        return None
    
    def send_email(self, to_email: str, subject: str, content: str, from_email: str = None) -> bool:
        """Send email using the active provider."""
        if not self.active_provider:
            logger.warning("No email provider configured")
            return False
            
        try:
            if self.active_provider == 'mailgun':
                return self._send_via_mailgun(to_email, subject, content, from_email)
            elif self.active_provider == 'resend':
                return self._send_via_resend(to_email, subject, content, from_email)
            elif self.active_provider == 'brevo':
                return self._send_via_brevo(to_email, subject, content, from_email)
            else:
                logger.error(f"Unknown email provider: {self.active_provider}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email via {self.active_provider}: {e}")
            return False
    
    def _send_via_mailgun(self, to_email: str, subject: str, content: str, from_email: str = None) -> bool:
        """Send email via Mailgun."""
        try:
            config = self.providers['mailgun']
            domain = config['domain']
            
            if not from_email:
                from_email = f"noreply@{domain}"
            
            url = f"https://api.mailgun.net/v3/{domain}/messages"
            
            data = {
                'from': from_email,
                'to': to_email,
                'subject': subject,
                'html': content
            }
            
            response = self.session.post(
                url,
                auth=('api', config['api_key']),
                data=data
            )
            
            if response.status_code == 200:
                logger.info(f"Email sent via Mailgun to {to_email}")
                return True
            else:
                logger.error(f"Mailgun error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Mailgun send error: {e}")
            return False
    
    def _send_via_resend(self, to_email: str, subject: str, content: str, from_email: str = None) -> bool:
        """Send email via Resend."""
        try:
            config = self.providers['resend']
            
            if not from_email:
                from_email = "noreply@yourdomain.com"  # Update with your domain
            
            payload = {
                'from': from_email,
                'to': [to_email],
                'subject': subject,
                'html': content
            }
            
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(
                config['url'],
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"Email sent via Resend to {to_email}")
                return True
            else:
                logger.error(f"Resend error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Resend send error: {e}")
            return False
    
    def _send_via_brevo(self, to_email: str, subject: str, content: str, from_email: str = None) -> bool:
        """Send email via Brevo (formerly Sendinblue)."""
        try:
            config = self.providers['brevo']
            
            if not from_email:
                from_email = "noreply@yourdomain.com"  # Update with your domain
            
            payload = {
                'sender': {
                    'name': 'AI GTM Engine',
                    'email': from_email
                },
                'to': [
                    {
                        'email': to_email
                    }
                ],
                'subject': subject,
                'htmlContent': content
            }
            
            headers = {
                'api-key': config['api_key'],
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(
                config['url'],
                json=payload,
                headers=headers
            )
            
            if response.status_code == 201:
                logger.info(f"Email sent via Brevo to {to_email}")
                return True
            else:
                logger.error(f"Brevo error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Brevo send error: {e}")
            return False
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all email providers."""
        status = {}
        
        for provider, config in self.providers.items():
            if provider == 'mailgun':
                status[provider] = {
                    'configured': bool(config['api_key'] and config['domain'] and 
                                     config['api_key'] != "your_mailgun_api_key_here"),
                    'api_key': bool(config['api_key'] and config['api_key'] != "your_mailgun_api_key_here"),
                    'domain': bool(config['domain'] and config['domain'] != "your_mailgun_domain_here")
                }
            else:
                status[provider] = {
                    'configured': bool(config['api_key'] and config['api_key'] != f"your_{provider}_api_key_here"),
                    'api_key': bool(config['api_key'] and config['api_key'] != f"your_{provider}_api_key_here")
                }
        
        status['active_provider'] = self.active_provider
        return status


# Global email service instance
email_service = EmailService()

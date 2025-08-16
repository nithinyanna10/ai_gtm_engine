"""
Advanced content generator using multiple LLMs for hyper-personalized outreach.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import OpenAI
from loguru import logger

from ..core.config import settings
from ..core.database import Lead, Signal, AITemplate, get_db

class ContentGenerator:
    """Generates hyper-personalized outreach content using multiple LLMs."""
    
    def __init__(self):
        self.openai_client = None
        
        if settings.api.openai_api_key:
            self.openai_client = OpenAI(api_key=settings.api.openai_api_key)
        
        # Load prompt templates
        self.prompts = self._load_prompt_templates()
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates from configuration."""
        return {
            'email': """You are an expert sales professional specializing in authentication and security solutions. 

Company Context:
- Company: {company_name}
- Industry: {industry}
- Size: {employee_count} employees
- Tech Stack: {tech_stack}
- Recent Activity: {recent_signals}

Recent Signals Detected:
{signal_summary}

Your goal is to write a compelling, personalized email that:
1. References specific recent activity or challenges they're facing
2. Shows you've done your research about their company
3. Offers a relevant solution to their specific pain points
4. Is concise (under 150 words) and professional
5. Includes a clear call-to-action

Write a personalized email that would resonate with {contact_title} at {company_name}:""",

            'linkedin': """You are a sales professional reaching out on LinkedIn. 

Company Context:
- Company: {company_name}
- Industry: {industry}
- Size: {employee_count} employees
- Tech Stack: {tech_stack}
- Recent Activity: {recent_signals}

Recent Signals Detected:
{signal_summary}

Write a LinkedIn connection request message that:
1. Is personal and shows you've researched their company
2. References specific recent activity or challenges
3. Is under 100 words
4. Includes a clear value proposition
5. Ends with a professional call-to-action

Write a LinkedIn message for {contact_name} at {company_name}:""",

            'video_script': """You are creating a personalized video script for a sales outreach.

Company Context:
- Company: {company_name}
- Industry: {industry}
- Size: {employee_count} employees
- Tech Stack: {tech_stack}
- Recent Activity: {recent_signals}

Recent Signals Detected:
{signal_summary}

Create a 30-second video script that:
1. Opens with a personalized hook about their recent activity
2. Identifies their specific pain point
3. Offers a relevant solution
4. Includes a clear call-to-action
5. Is conversational and engaging

Write a video script for {contact_name} at {company_name}:""",

            'call_script': """You are creating a cold call script for sales outreach.

Company Context:
- Company: {company_name}
- Industry: {industry}
- Size: {employee_count} employees
- Tech Stack: {tech_stack}
- Recent Activity: {recent_signals}

Recent Signals Detected:
{signal_summary}

Create a cold call script that:
1. Opens with a personalized hook about their recent activity
2. Identifies their specific pain point
3. Offers a relevant solution
4. Handles common objections
5. Includes a clear next step

Write a call script for {contact_name} at {company_name}:"""
        }
    
    def generate_outreach_content(self, lead_id: int, contact_info: Dict[str, Any]) -> Dict[str, str]:
        """Generate multi-channel outreach content for a lead."""
        db = next(get_db())
        
        try:
            # Get lead and signals
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                raise ValueError(f"Lead {lead_id} not found")
            
            signals = db.query(Signal).filter(Signal.lead_id == lead_id).order_by(Signal.created_at.desc()).all()
            
            # Prepare context
            context = self._prepare_context(lead, signals, contact_info)
            
            # Generate content for each channel
            content = {}
            
            # Email content
            email_content = self._generate_email_content(context)
            content['email'] = email_content
            
            # LinkedIn content
            linkedin_content = self._generate_linkedin_content(context)
            content['linkedin'] = linkedin_content
            
            # Video script
            video_script = self._generate_video_script(context)
            content['video_script'] = video_script
            
            # Call script
            call_script = self._generate_call_script(context)
            content['call_script'] = call_script
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating content for lead {lead_id}: {e}")
            return {}
        finally:
            db.close()
    
    def _prepare_context(self, lead: Lead, signals: List[Signal], contact_info: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for content generation."""
        # Group signals by type
        signal_groups = {}
        for signal in signals:
            if signal.signal_type not in signal_groups:
                signal_groups[signal.signal_type] = []
            signal_groups[signal.signal_type].append(signal)
        
        # Create signal summary
        signal_summary = self._create_signal_summary(signal_groups)
        
        # Get recent activity description
        recent_signals = self._get_recent_activity_description(signals)
        
        # Prepare tech stack description
        tech_stack_desc = self._format_tech_stack(lead.tech_stack)
        
        return {
            'company_name': lead.company_name,
            'industry': lead.industry or 'Technology',
            'employee_count': lead.employee_count or 'Unknown',
            'tech_stack': tech_stack_desc,
            'recent_signals': recent_signals,
            'signal_summary': signal_summary,
            'contact_name': contact_info.get('name', 'the team'),
            'contact_title': contact_info.get('title', 'the team'),
            'contact_email': contact_info.get('email', ''),
            'signals': signals
        }
    
    def _create_signal_summary(self, signal_groups: Dict[str, List[Signal]]) -> str:
        """Create a summary of detected signals."""
        summary_parts = []
        
        for signal_type, signals in signal_groups.items():
            if signals:
                # Get the most recent signal
                latest_signal = max(signals, key=lambda s: s.created_at)
                summary_parts.append(f"- {signal_type.replace('_', ' ').title()}: {latest_signal.content}")
        
        return "\n".join(summary_parts) if summary_parts else "No recent activity detected."
    
    def _get_recent_activity_description(self, signals: List[Signal]) -> str:
        """Get a description of recent activity."""
        if not signals:
            return "No recent activity detected."
        
        # Get the most recent signal
        latest_signal = max(signals, key=lambda s: s.created_at)
        
        # Create activity description based on signal type
        if 'github' in latest_signal.signal_type:
            return f"Recent GitHub activity related to authentication and security"
        elif 'reddit' in latest_signal.signal_type:
            return f"Recent community discussions about security challenges"
        elif 'linkedin' in latest_signal.signal_type:
            return f"Recent hiring activity for security roles"
        elif 'news' in latest_signal.signal_type:
            return f"Recent news about security initiatives"
        else:
            return f"Recent activity indicating security focus"
    
    def _format_tech_stack(self, tech_stack: List[str]) -> str:
        """Format tech stack for display."""
        if not tech_stack:
            return "Unknown"
        
        # Group by category
        categories = {
            'Backend': ['node', 'python', 'java', 'go', 'php', 'ruby', 'c#', '.net'],
            'Frontend': ['react', 'vue', 'angular', 'javascript', 'typescript'],
            'Database': ['postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch'],
            'Cloud': ['aws', 'azure', 'gcp', 'heroku', 'digitalocean'],
            'Auth': ['auth0', 'firebase', 'cognito', 'okta', 'onelogin']
        }
        
        categorized = {}
        for tech in tech_stack:
            tech_lower = tech.lower()
            for category, techs in categories.items():
                if any(t in tech_lower for t in techs):
                    if category not in categorized:
                        categorized[category] = []
                    categorized[category].append(tech)
                    break
            else:
                if 'Other' not in categorized:
                    categorized['Other'] = []
                categorized['Other'].append(tech)
        
        # Format output
        parts = []
        for category, techs in categorized.items():
            parts.append(f"{category}: {', '.join(techs[:3])}")  # Limit to 3 per category
        
        return "; ".join(parts)
    
    def _generate_email_content(self, context: Dict[str, Any]) -> str:
        """Generate personalized email content."""
        try:
            if self.openai_client:
                return self._generate_with_openai('email', context)
            else:
                return self._generate_fallback_email(context)
        except Exception as e:
            logger.error(f"Error generating email content: {e}")
            return self._generate_fallback_email(context)
    
    def _generate_linkedin_content(self, context: Dict[str, Any]) -> str:
        """Generate LinkedIn connection message."""
        try:
            if self.openai_client:
                return self._generate_with_openai('linkedin', context)
            else:
                return self._generate_fallback_linkedin(context)
        except Exception as e:
            logger.error(f"Error generating LinkedIn content: {e}")
            return self._generate_fallback_linkedin(context)
    
    def _generate_video_script(self, context: Dict[str, Any]) -> str:
        """Generate video script."""
        try:
            if self.openai_client:
                return self._generate_with_openai('video_script', context)
            else:
                return self._generate_fallback_video_script(context)
        except Exception as e:
            logger.error(f"Error generating video script: {e}")
            return self._generate_fallback_video_script(context)
    
    def _generate_call_script(self, context: Dict[str, Any]) -> str:
        """Generate cold call script."""
        try:
            if self.openai_client:
                return self._generate_with_openai('call_script', context)
            else:
                return self._generate_fallback_call_script(context)
        except Exception as e:
            logger.error(f"Error generating call script: {e}")
            return self._generate_fallback_call_script(context)
    
    def _generate_with_openai(self, content_type: str, context: Dict[str, Any]) -> str:
        """Generate content using OpenAI."""
        prompt = self.prompts[content_type].format(**context)
        
        response = self.openai_client.chat.completions.create(
            model=settings.api.openai_model,
            messages=[
                {"role": "system", "content": "You are an expert sales professional who creates compelling, personalized outreach content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    

    
    def _generate_fallback_email(self, context: Dict[str, Any]) -> str:
        """Generate fallback email content."""
        return f"""Hi {context['contact_name']},

I noticed {context['company_name']} has been active with {context['recent_signals'].lower()}. 

Given your focus on {context['industry']} and your tech stack ({context['tech_stack']}), I thought you might be interested in how we're helping companies like yours solve authentication and security challenges.

Would you be open to a 15-minute call to discuss how we could help {context['company_name']} improve its security posture?

Best regards,
[Your Name]"""
    
    def _generate_fallback_linkedin(self, context: Dict[str, Any]) -> str:
        """Generate fallback LinkedIn message."""
        return f"""Hi {context['contact_name']},

I noticed {context['company_name']} has been working on {context['recent_signals'].lower()}. 

Given your role and the company's focus on {context['industry']}, I'd love to connect and share how we're helping similar companies improve their authentication and security infrastructure.

Would you be interested in a brief conversation?

Best regards,
[Your Name]"""
    
    def _generate_fallback_video_script(self, context: Dict[str, Any]) -> str:
        """Generate fallback video script."""
        return f"""Hi {context['contact_name']},

I wanted to reach out because I noticed {context['company_name']} has been working on {context['recent_signals'].lower()}.

As a {context['industry']} company using {context['tech_stack']}, you're likely facing some common authentication and security challenges.

We've helped companies like yours implement robust, scalable authentication solutions that improve security while enhancing user experience.

I'd love to show you how we could help {context['company_name']} achieve similar results.

Would you be open to a 15-minute demo?

Thanks for your time!"""
    
    def _generate_fallback_call_script(self, context: Dict[str, Any]) -> str:
        """Generate fallback call script."""
        return f"""Hi {context['contact_name']}, this is [Your Name] from [Company].

I'm calling because I noticed {context['company_name']} has been working on {context['recent_signals'].lower()}.

Given your role and the company's focus on {context['industry']}, I thought you might be interested in how we're helping similar companies solve their authentication and security challenges.

Do you have a few minutes to discuss how we could help {context['company_name']} improve its security posture?

[If yes] Great! What specific authentication or security challenges are you currently facing?

[If no] No problem. Would you prefer if I sent you some information via email instead?

[Handle objections and set next steps]"""

# Global instance
content_generator = ContentGenerator()

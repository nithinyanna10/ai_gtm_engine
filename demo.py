#!/usr/bin/env python3
"""
Demo script for the AI GTM Engine.
This script demonstrates the key features and capabilities of the engine.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# API configuration
API_BASE_URL = "http://localhost:8000"

def make_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make API request to the backend."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def demo_lead_discovery():
    """Demonstrate real lead discovery using APIs."""
    print("🔍 Demo: Real Lead Discovery from APIs")
    print("=" * 50)
    
    print("🚀 Starting lead discovery from GitHub, News, and Reddit...")
    result = make_api_request("/discover-leads", method="POST")
    
    if "error" not in result:
        print("✅ Lead discovery started in background")
        
        # Wait for discovery to complete
        print("⏳ Waiting for lead discovery to complete...")
        time.sleep(10)
        
        # Get discovered leads
        leads = make_api_request("/leads")
        
        if "error" not in leads:
            print(f"📊 Discovered {len(leads)} real leads from APIs")
            
            # Display some discovered leads
            for i, lead in enumerate(leads[:3]):
                print(f"   {i+1}. {lead['company_name']} ({lead['domain']}) - {lead['source']}")
                
            return [lead['id'] for lead in leads]
        else:
            print(f"❌ Failed to get leads: {leads['error']}")
            return []
    else:
        print(f"❌ Failed to start lead discovery: {result['error']}")
        return []

def demo_signal_collection(lead_ids: List[int]):
    """Demonstrate signal collection for leads."""
    print("\n📡 Demo: Signal Collection")
    print("=" * 50)
    
    for lead_id in lead_ids:
        print(f"\n🔍 Collecting signals for lead ID: {lead_id}")
        
        # Start signal collection
        result = make_api_request(f"/leads/{lead_id}/collect-signals", method="POST")
        
        if "error" not in result:
            print("✅ Signal collection started")
            
            # Wait a moment for background processing
            time.sleep(2)
            
            # Check signals
            signals = make_api_request(f"/leads/{lead_id}/signals")
            
            if "error" not in signals:
                print(f"📊 Found {len(signals)} signals")
                
                # Display some sample signals
                for i, signal in enumerate(signals[:3]):
                    print(f"   {i+1}. {signal['signal_type']}: {signal['content'][:100]}...")
            else:
                print(f"❌ Failed to get signals: {signals['error']}")
        else:
            print(f"❌ Failed to start signal collection: {result['error']}")

def demo_content_generation(lead_ids: List[int]):
    """Demonstrate AI content generation."""
    print("\n🤖 Demo: AI Content Generation")
    print("=" * 50)
    
    for lead_id in lead_ids:
        print(f"\n📝 Generating content for lead ID: {lead_id}")
        
        # Contact information
        contact_info = {
            "name": "John Smith",
            "title": "CTO",
            "email": "john.smith@company.com"
        }
        
        # Generate content
        result = make_api_request(
            f"/leads/{lead_id}/generate-content",
            method="POST",
            data=contact_info
        )
        
        if "error" not in result:
            content = result["content"]
            print("✅ Content generated successfully!")
            
            # Display generated content
            print("\n📧 Email Content:")
            print("-" * 30)
            print(content.get('email', 'No email content generated'))
            
            print("\n💼 LinkedIn Message:")
            print("-" * 30)
            print(content.get('linkedin', 'No LinkedIn content generated'))
            
            print("\n🎥 Video Script:")
            print("-" * 30)
            print(content.get('video_script', 'No video script generated'))
            
            print("\n📞 Call Script:")
            print("-" * 30)
            print(content.get('call_script', 'No call script generated'))
            
        else:
            print(f"❌ Failed to generate content: {result['error']}")

def demo_outreach_creation(lead_ids: List[int]):
    """Demonstrate outreach creation and tracking."""
    print("\n📧 Demo: Outreach Creation and Tracking")
    print("=" * 50)
    
    for lead_id in lead_ids:
        print(f"\n📤 Creating outreach for lead ID: {lead_id}")
        
        # Sample outreach data
        outreach_data = {
            "channel": "email",
            "content": "Hi John, I noticed your company has been working on authentication improvements...",
            "status": "pending",
            "subject_line": "Authentication Solution for Your Team",
            "recipient_email": "john.smith@company.com",
            "recipient_name": "John Smith"
        }
        
        # Create outreach
        result = make_api_request(
            f"/leads/{lead_id}/outreach",
            method="POST",
            data=outreach_data
        )
        
        if "error" not in result:
            outreach_id = result["id"]
            print(f"✅ Outreach created with ID: {outreach_id}")
            
            # Get outreach history
            outreach_history = make_api_request(f"/leads/{lead_id}/outreach")
            
            if "error" not in outreach_history:
                print(f"📋 Total outreach attempts: {len(outreach_history)}")
            else:
                print(f"❌ Failed to get outreach history: {outreach_history['error']}")
        else:
            print(f"❌ Failed to create outreach: {result['error']}")

def demo_analytics():
    """Demonstrate analytics and insights."""
    print("\n📊 Demo: Analytics and Insights")
    print("=" * 50)
    
    # Get analytics overview
    analytics = make_api_request("/analytics/overview")
    
    if "error" not in analytics:
        print("📈 Analytics Overview:")
        print(f"   • Total Leads: {analytics.get('total_leads', 0)}")
        print(f"   • High Intent Leads: {analytics.get('high_intent_leads', 0)}")
        print(f"   • Total Signals: {analytics.get('total_signals', 0)}")
        print(f"   • Total Outreach: {analytics.get('total_outreach', 0)}")
        print(f"   • Recent Signals (7d): {analytics.get('recent_signals_7d', 0)}")
        print(f"   • Recent Outreach (7d): {analytics.get('recent_outreach_7d', 0)}")
        
        # Calculate high intent rate
        total_leads = analytics.get('total_leads', 1)
        high_intent_leads = analytics.get('high_intent_leads', 0)
        high_intent_rate = (high_intent_leads / total_leads) * 100
        
        print(f"   • High Intent Rate: {high_intent_rate:.1f}%")
    else:
        print(f"❌ Failed to get analytics: {analytics['error']}")
    
    # Get signals by type
    signals_by_type = make_api_request("/analytics/signals-by-type")
    
    if "error" not in signals_by_type:
        print("\n📡 Signals by Type:")
        for signal_type in signals_by_type:
            print(f"   • {signal_type['signal_type']}: {signal_type['count']}")
    else:
        print(f"❌ Failed to get signals by type: {signals_by_type['error']}")

def demo_lead_scoring():
    """Demonstrate lead scoring and ranking."""
    print("\n🎯 Demo: Lead Scoring and Ranking")
    print("=" * 50)
    
    # Get leads with different score thresholds
    score_thresholds = [0.3, 0.5, 0.7]
    
    for threshold in score_thresholds:
        leads = make_api_request(f"/leads?min_score={threshold}")
        
        if "error" not in leads:
            print(f"\n📊 Leads with score >= {threshold}: {len(leads)}")
            
            if leads:
                # Show top 3 leads
                top_leads = sorted(leads, key=lambda x: x['intent_score'], reverse=True)[:3]
                
                for i, lead in enumerate(top_leads, 1):
                    print(f"   {i}. {lead['company_name']} (Score: {lead['intent_score']:.2f})")
        else:
            print(f"❌ Failed to get leads: {leads['error']}")

def main():
    """Main demo function."""
    print("🚀 AI GTM Engine Demo")
    print("=" * 60)
    print("This demo showcases the key features of the AI GTM Engine")
    print("Make sure the API server is running on http://localhost:8000")
    print("=" * 60)
    
    # Check if API is running
    health = make_api_request("/health")
    if "error" in health:
        print("❌ API server is not running. Please start the server first.")
        print("Run: python start.py")
        return
    
    print("✅ API server is running")
    
    # Run demos
    try:
        # 1. Lead Creation
        created_leads = demo_lead_creation()
        
        if not created_leads:
            print("❌ No leads were created. Demo cannot continue.")
            return
        
        # 2. Signal Collection
        demo_signal_collection(created_leads)
        
        # 3. Content Generation
        demo_content_generation(created_leads)
        
        # 4. Outreach Creation
        demo_outreach_creation(created_leads)
        
        # 5. Analytics
        demo_analytics()
        
        # 6. Lead Scoring
        demo_lead_scoring()
        
        print("\n🎉 Demo completed successfully!")
        print("\n📱 Next steps:")
        print("   • Visit http://localhost:8501 to see the dashboard")
        print("   • Visit http://localhost:8000/docs for API documentation")
        print("   • Try creating your own leads and generating content")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")

if __name__ == "__main__":
    main()

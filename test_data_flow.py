#!/usr/bin/env python3
"""
Test script to populate the dashboard with real data.
"""

import requests
import time
import json

API_BASE = "http://localhost:8000"

def test_data_flow():
    """Test the complete data flow."""
    print("🚀 Testing AI GTM Engine Data Flow")
    print("=" * 50)
    
    # 1. Check API health
    print("1. Checking API health...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ API is healthy")
        else:
            print("❌ API is not responding")
            return
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return
    
    # 2. Add test leads
    print("\n2. Adding test leads...")
    test_leads = [
        {
            "company_name": "TechAuth Solutions",
            "domain": "techauth-solutions.com",
            "industry": "Technology",
            "employee_count": 120,
            "revenue_range": "10M-50M",
            "location": "Austin, TX",
            "description": "Authentication platform with security vulnerabilities",
            "tech_stack": ["React", "Node.js", "MongoDB"],
            "primary_tech": "Node.js"
        },
        {
            "company_name": "SecureBank Pro",
            "domain": "securebank-pro.com",
            "industry": "Finance",
            "employee_count": 250,
            "revenue_range": "50M-200M",
            "location": "New York, NY",
            "description": "Digital banking with login system issues",
            "tech_stack": ["Java", "Spring", "Oracle"],
            "primary_tech": "Java"
        },
        {
            "company_name": "HealthTech Secure",
            "domain": "healthtech-secure.com",
            "industry": "Healthcare",
            "employee_count": 85,
            "revenue_range": "5M-25M",
            "location": "Boston, MA",
            "description": "Healthcare software with authentication problems",
            "tech_stack": ["Python", "Django", "PostgreSQL"],
            "primary_tech": "Python"
        }
    ]
    
    lead_ids = []
    for lead_data in test_leads:
        try:
            response = requests.post(
                f"{API_BASE}/leads",
                json=lead_data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                lead_id = result.get("id")
                if lead_id:
                    lead_ids.append(lead_id)
                    print(f"✅ Added lead: {lead_data['company_name']} (ID: {lead_id})")
                else:
                    print(f"⚠️ Lead already exists: {lead_data['company_name']}")
            else:
                print(f"❌ Failed to add lead: {lead_data['company_name']}")
        except Exception as e:
            print(f"❌ Error adding lead: {e}")
    
    # 3. Trigger signal collection for each lead
    print(f"\n3. Triggering signal collection for {len(lead_ids)} leads...")
    for lead_id in lead_ids:
        try:
            response = requests.post(f"{API_BASE}/leads/{lead_id}/collect-signals")
            if response.status_code == 200:
                print(f"✅ Signal collection started for lead {lead_id}")
            else:
                print(f"❌ Failed to start signal collection for lead {lead_id}")
        except Exception as e:
            print(f"❌ Error starting signal collection: {e}")
    
    # 4. Wait for signal collection to complete
    print("\n4. Waiting for signal collection to complete...")
    time.sleep(15)
    
    # 5. Check results
    print("\n5. Checking results...")
    
    # Check leads
    try:
        response = requests.get(f"{API_BASE}/leads")
        if response.status_code == 200:
            leads = response.json()
            print(f"📊 Total leads: {len(leads)}")
            
            # Check signals
            for lead in leads[:3]:  # Show first 3 leads
                lead_id = lead.get('id')
                if lead_id:
                    signals_response = requests.get(f"{API_BASE}/leads/{lead_id}/signals")
                    if signals_response.status_code == 200:
                        signals = signals_response.json()
                        print(f"   📡 {lead['company_name']}: {len(signals)} signals")
                    else:
                        print(f"   ❌ Failed to get signals for {lead['company_name']}")
        else:
            print("❌ Failed to get leads")
    except Exception as e:
        print(f"❌ Error checking results: {e}")
    
    # 6. Check analytics
    print("\n6. Checking analytics...")
    try:
        response = requests.get(f"{API_BASE}/analytics/overview")
        if response.status_code == 200:
            analytics = response.json()
            print(f"📈 Analytics Overview:")
            print(f"   • Total Leads: {analytics.get('total_leads', 0)}")
            print(f"   • Total Signals: {analytics.get('total_signals', 0)}")
            print(f"   • High Intent Leads: {analytics.get('high_intent_leads', 0)}")
            print(f"   • Total Outreach: {analytics.get('total_outreach', 0)}")
        else:
            print("❌ Failed to get analytics")
    except Exception as e:
        print(f"❌ Error getting analytics: {e}")
    
    print("\n🎉 Data flow test completed!")
    print("📱 Check the dashboard at: http://localhost:8501")

if __name__ == "__main__":
    test_data_flow()

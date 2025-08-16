#!/usr/bin/env python3
"""
Simple test script to verify the AI GTM Engine is working.
"""

import requests
import time
import sys

def test_api_health():
    """Test if the API server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_database():
    """Test database functionality."""
    try:
        from src.core.database import get_db, Lead
        db = next(get_db())
        
        # Test creating a lead
        test_lead = Lead(
            company_name="Test Company",
            domain="testcompany.com",
            industry="Technology",
            employee_count=100
        )
        db.add(test_lead)
        db.commit()
        
        # Test retrieving leads
        leads = db.query(Lead).all()
        print(f"✅ Database working - {len(leads)} leads found")
        
        # Clean up test data
        db.delete(test_lead)
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_content_generation():
    """Test content generation (without API keys)."""
    try:
        from src.ai_processing.content_generator import content_generator
        
        # Test with fallback content generation
        contact_info = {
            "name": "John Doe",
            "title": "CTO",
            "email": "john@testcompany.com"
        }
        
        # This should work even without API keys (uses fallback)
        content = content_generator.generate_outreach_content(1, contact_info)
        
        if content and 'email' in content:
            print("✅ Content generation working")
            return True
        else:
            print("❌ Content generation failed")
            return False
    except Exception as e:
        print(f"❌ Content generation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing AI GTM Engine")
    print("=" * 40)
    
    # Test database
    print("\n1. Testing database...")
    db_ok = test_database()
    
    # Test content generation
    print("\n2. Testing content generation...")
    content_ok = test_content_generation()
    
    # Test API (if server is running)
    print("\n3. Testing API server...")
    api_ok = test_api_health()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"   Database: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"   Content Generation: {'✅ PASS' if content_ok else '❌ FAIL'}")
    print(f"   API Server: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if db_ok and content_ok:
        print("\n🎉 Core functionality is working!")
        print("\n📋 Next steps:")
        print("1. Add API keys to config/api_keys.yaml")
        print("2. Run: python start.py")
        print("3. Run: python demo.py")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


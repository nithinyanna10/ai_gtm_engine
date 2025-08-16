#!/usr/bin/env python3
"""
Test script to verify OpenAI integration is working.
"""

import sys
from src.ai_processing.content_generator import content_generator

def test_openai_integration():
    """Test OpenAI content generation."""
    print("🤖 Testing OpenAI Integration")
    print("=" * 40)
    
    # Test contact info
    contact_info = {
        "name": "Sarah Johnson",
        "title": "VP of Engineering",
        "email": "sarah.johnson@techstartup.com"
    }
    
    # Test lead data (simulating a lead with signals)
    print("📝 Generating personalized content...")
    
    try:
        # Generate content using OpenAI
        content = content_generator.generate_outreach_content(1, contact_info)
        
        if content:
            print("✅ Content generated successfully!")
            
            print("\n📧 Email Content:")
            print("-" * 30)
            print(content.get('email', 'No email content'))
            
            print("\n💼 LinkedIn Message:")
            print("-" * 30)
            print(content.get('linkedin', 'No LinkedIn content'))
            
            print("\n🎥 Video Script:")
            print("-" * 30)
            print(content.get('video_script', 'No video script'))
            
            print("\n📞 Call Script:")
            print("-" * 30)
            print(content.get('call_script', 'No call script'))
            
            return True
        else:
            print("❌ No content generated")
            return False
            
    except Exception as e:
        print(f"❌ Error generating content: {e}")
        return False

def main():
    """Main test function."""
    success = test_openai_integration()
    
    if success:
        print("\n🎉 OpenAI integration is working!")
        print("\n📋 Next steps:")
        print("1. Visit http://localhost:8501 to use the dashboard")
        print("2. Create leads and generate personalized content")
        print("3. Run: python demo.py for a full demonstration")
    else:
        print("\n❌ OpenAI integration test failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


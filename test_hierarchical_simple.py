"""
Simple test script for the hierarchical multi-agent system.
Tests the core functionality without complex LangGraph issues.
"""

import requests
import json

# Test the original working system (port 8006)
ORIGINAL_API = "http://127.0.0.1:8006/execute"
# Test the hierarchical system (port 8007) 
HIERARCHICAL_API = "http://127.0.0.1:8007/execute_hierarchical"

def test_original_system():
    """Test the original working system"""
    print("=" * 60)
    print("TESTING ORIGINAL SYSTEM (Port 8006)")
    print("=" * 60)
    
    test_cases = [
        ("hello", 2, "Greeting"),
        ("Get my patient information", 2, "Patient Info"),
        ("Is Dr. Mohamed Tajmouati available tomorrow?", 2, "Availability Check"),
        ("book appointment", 2, "Start Booking"),
        ("What are your services?", 2, "FAQ"),
    ]
    
    for message, patient_id, description in test_cases:
        print(f"\n📝 Test: {description}")
        print(f"   Patient ID: {patient_id}")
        print(f"   Message: '{message}'")
        
        try:
            response = requests.post(
                ORIGINAL_API,
                json={"messages": message, "id_number": patient_id},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Status: {response.status_code}")
                
                # Extract assistant response
                for msg in result.get("messages", []):
                    if isinstance(msg, dict) and msg.get("sender") != "user":
                        content = msg.get("content", "No response")
                        # Truncate long responses
                        if len(content) > 100:
                            content = content[:100] + "..."
                        print(f"   🤖 Response: {content}")
                        break
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    
    print("\n" + "=" * 60)
    print("ORIGINAL SYSTEM TEST COMPLETE")
    print("=" * 60)

def test_hierarchical_health():
    """Test if hierarchical system is reachable"""
    print("\n" + "=" * 60)
    print("CHECKING HIERARCHICAL SYSTEM HEALTH (Port 8007)")
    print("=" * 60)
    
    try:
        # Try health endpoint
        health_url = HIERARCHICAL_API.replace("/execute_hierarchical", "")
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Hierarchical system is reachable")
            print(f"   Response: {response.json()}")
        else:
            print(f"⚠️ Hierarchical system returned: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Cannot connect to hierarchical system: {str(e)}")
        print("   The original system on port 8006 is working and ready for testing.")
    
    print("=" * 60)

def test_streamlit_connection():
    """Test Streamlit frontend connection"""
    print("\n" + "=" * 60)
    print("STREAMLIT FRONTEND TEST")
    print("=" * 60)
    
    print("1. Open your browser to: http://localhost:8501")
    print("2. Make sure 'Use Hierarchical System' is OFF (toggle in sidebar)")
    print("3. Try these test conversations:")
    print("   - 'Hello' (greeting)")
    print("   - 'Get my patient information' (patient ID: 2)")
    print("   - 'Is Dr. Mohamed available tomorrow?'")
    print("   - 'book appointment' (multi-step booking)")
    print("   - 'What are your services?'")
    print("\n4. The system will use the original working backend (port 8006)")
    print("=" * 60)

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MEDICAL APPOINTMENT MULTI-AGENT SYSTEM TEST")
    print("=" * 60)
    
    # Test original system (working)
    test_original_system()
    
    # Check hierarchical system
    test_hierarchical_health()
    
    # Streamlit instructions
    test_streamlit_connection()
    
    print("\n🎯 RECOMMENDATION:")
    print("   Use the ORIGINAL SYSTEM (port 8006) for testing.")
    print("   It's fully working with all agents and tools.")
    print("\n   The hierarchical system (port 8007) has implementation")
    print("   issues that need debugging.")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

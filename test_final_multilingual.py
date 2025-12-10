"""
Final test of multilingual chatbot
"""

import requests
import time
import sys

def wait_for_server(url, max_attempts=30):
    """Wait for server to be ready"""
    print("Waiting for server to start...")
    for i in range(max_attempts):
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                print(f"✅ Server is ready after {i+1} seconds")
                return True
        except:
            if i % 5 == 0:
                print(f"  Attempt {i+1}/{max_attempts}...")
            time.sleep(1)
    print("❌ Server failed to start")
    return False

def test_multilingual_chatbot():
    """Test the multilingual chatbot"""
    print("=" * 60)
    print("FINAL TEST: MULTILINGUAL CHATBOT")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8006"
    
    # Wait for server
    if not wait_for_server(base_url):
        return
    
    patient_id = 2
    
    # Test cases with expected routing
    test_cases = [
        # (message, description, expected_agent)
        ("Hello", "English greeting", "FAQ"),
        ("Bonjour", "French greeting", "FAQ"),
        ("مرحبا", "Arabic greeting", "FAQ"),
        ("book appointment", "English booking", "APPOINTMENT"),
        ("réserver un rendez-vous", "French booking", "APPOINTMENT"),
        ("حجز موعد", "Arabic booking", "APPOINTMENT"),
        ("Get my patient information", "English patient info", "PATIENT"),
        ("معلومات المريض", "Arabic patient info", "PATIENT"),
        ("Informations du patient", "French patient info", "PATIENT"),
        ("What are your services?", "English services", "FAQ"),
        ("Quels sont vos services?", "French services", "FAQ"),
        ("ما هي خدماتكم؟", "Arabic services", "FAQ"),
        ("Is Dr. Mohamed available?", "English availability", "AVAILABILITY"),
        ("Dr. Mohamed disponible?", "French availability", "AVAILABILITY"),
        ("هل الدكتور محمد متاح؟", "Arabic availability", "AVAILABILITY"),
    ]
    
    results = []
    
    for user_message, description, expected_agent in test_cases:
        print(f"\n📝 Test: {description}")
        print(f"   Input: '{user_message}'")
        print(f"   Expected: {expected_agent} agent")
        
        # Prepare request
        payload = {
            "id_number": patient_id,
            "messages": user_message
        }
        
        try:
            # Send request to FastAPI
            response = requests.post(f"{base_url}/execute", json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                messages = result.get("messages", [])
                
                if len(messages) >= 2:
                    bot_response = messages[1].get("content", "No response")
                    sender = messages[1].get("sender", "unknown")
                    
                    print(f"   ✅ Status: {response.status_code}")
                    print(f"   🤖 Sender: {sender}")
                    print(f"   Response: {bot_response[:60]}...")
                    
                    # Determine which agent responded
                    agent_type = "UNKNOWN"
                    if "appointment" in sender.lower():
                        agent_type = "APPOINTMENT"
                    elif "availability" in sender.lower():
                        agent_type = "AVAILABILITY"
                    elif "patient" in sender.lower():
                        agent_type = "PATIENT"
                    elif "faq" in sender.lower() or "assistant" in sender.lower():
                        agent_type = "FAQ"
                    
                    # Check if correct agent responded
                    if agent_type == expected_agent:
                        print(f"   🎯 CORRECT: {agent_type} agent responded")
                        results.append(True)
                    else:
                        print(f"   ❌ WRONG: {agent_type} agent responded (expected {expected_agent})")
                        results.append(False)
                else:
                    print(f"   ❌ Not enough messages in response")
                    print(f"   Response: {result}")
                    results.append(False)
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
            results.append(False)
        
        # Small delay between tests
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"Total tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Multilingual chatbot is working correctly!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the logs above.")
    
    print("\n" + "=" * 60)
    print("MULTILINGUAL CHATBOT TEST COMPLETE")
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    # Start server if not running
    print("Starting multilingual chatbot test...")
    
    # Run the test
    success = test_multilingual_chatbot()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ CHATBOT IS WORKING CORRECTLY IN ALL LANGUAGES!")
        print("=" * 60)
        print("\nThe chatbot can now handle:")
        print("  • English: 'book appointment', 'get my info', etc.")
        print("  • French: 'réserver un rendez-vous', 'informations du patient', etc.")
        print("  • Arabic: 'حجز موعد', 'معلومات المريض', etc.")
        print("\nOpen in browser: http://localhost:8505")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        sys.exit(1)

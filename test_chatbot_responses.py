"""
Test chatbot responses to various inputs
"""

import requests
import json

def test_chatbot_responses():
    """Test how chatbot responds to different inputs"""
    print("=" * 60)
    print("TESTING CHATBOT RESPONSES TO VARIOUS INPUTS")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8006"
    patient_id = 2
    
    test_cases = [
        ("Hello", "English greeting"),
        ("Bonjour", "French greeting"),
        ("مرحبا", "Arabic greeting"),
        ("book appointment", "Booking request"),
        ("réserver un rendez-vous", "French booking"),
        ("حجز موعد", "Arabic booking"),
        ("Get my patient information", "Patient info"),
        ("معلومات المريض", "Arabic patient info"),
        ("Informations du patient", "French patient info"),
        ("What are your services?", "English services"),
        ("Quels sont vos services?", "French services"),
        ("ما هي خدماتكم؟", "Arabic services"),
        ("Is Dr. Mohamed available?", "Availability check"),
        ("Dr. Mohamed disponible?", "French availability"),
        ("هل الدكتور محمد متاح؟", "Arabic availability"),
        ("I need help", "General help"),
        ("J'ai besoin d'aide", "French help"),
        ("أحتاج مساعدة", "Arabic help"),
    ]
    
    for user_message, description in test_cases:
        print(f"\n📝 Test: {description}")
        print(f"   Input: '{user_message}'")
        
        # Prepare request
        payload = {
            "id_number": patient_id,
            "messages": user_message
        }
        
        try:
            # Send request to FastAPI
            response = requests.post(f"{base_url}/execute", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                messages = result.get("messages", [])
                
                if len(messages) >= 2:
                    bot_response = messages[1].get("content", "No response")
                    print(f"   ✅ Status: {response.status_code}")
                    print(f"   🤖 Response: {bot_response[:80]}...")
                    
                    # Check if response is appropriate
                    if bot_response == "No response" or len(bot_response.strip()) < 5:
                        print(f"   ⚠️ Warning: Very short or empty response")
                    elif "error" in bot_response.lower():
                        print(f"   ❌ Error in response")
                    else:
                        print(f"   👍 Good response length")
                else:
                    print(f"   ❌ Not enough messages in response")
                    print(f"   Response: {result}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("RESPONSE TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_chatbot_responses()

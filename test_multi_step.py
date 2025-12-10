"""
Test multi-step appointment booking conversation
"""

import requests
import json
import time

def test_multi_step_booking():
    """Test the complete multi-step booking conversation"""
    print("=" * 60)
    print("TESTING MULTI-STEP APPOINTMENT BOOKING CONVERSATION")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8006"
    patient_id = 2
    
    test_steps = [
        ("book appointment", "Should start booking process"),
        ("Dr. Mohamed Tajmouati", "Should ask for date"),
        ("15-12-2024", "Should ask for time"),
        ("14:30", "Should confirm appointment")
    ]
    
    conversation_history = []
    
    for user_message, description in test_steps:
        print(f"\n📝 Step: {description}")
        print(f"   User: '{user_message}'")
        
        # Prepare request
        payload = {
            "message": user_message,
            "patient_id": patient_id,
            "conversation_history": conversation_history
        }
        
        try:
            # Send request to FastAPI
            response = requests.post(f"{base_url}/execute", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                bot_response = result.get("response", "No response")
                
                print(f"   ✅ Success!")
                print(f"   🤖 Bot: {bot_response[:100]}...")
                
                # Add to conversation history
                conversation_history.append({"role": "user", "content": user_message})
                conversation_history.append({"role": "assistant", "content": bot_response})
                
                # Check if booking was successful
                if "confirmed" in bot_response.lower() or "success" in bot_response.lower():
                    print(f"   🎉 Appointment booked successfully!")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
        
        # Small delay between steps
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("MULTI-STEP CONVERSATION TEST COMPLETE")
    print("=" * 60)
    
    # Test the scenario from user's feedback
    print("\n" + "=" * 60)
    print("TESTING USER'S REPORTED SCENARIO")
    print("=" * 60)
    
    test_scenario = [
        ("book appointment", "Start booking"),
        ("Dr. Mohamed Tajmouati", "Provide doctor name"),
        ("15-12-2024", "Provide date")
    ]
    
    conversation_history = []
    
    for user_message, description in test_scenario:
        print(f"\n📝 {description}: '{user_message}'")
        
        payload = {
            "message": user_message,
            "patient_id": patient_id,
            "conversation_history": conversation_history
        }
        
        try:
            response = requests.post(f"{base_url}/execute", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                bot_response = result.get("response", "No response")
                
                print(f"   🤖 Response: {bot_response[:80]}...")
                
                # Check if conversation continues properly
                if description == "Provide date" and "time" in bot_response.lower():
                    print(f"   ✅ Conversation continues correctly (asking for time)")
                elif description == "Provide doctor name" and "date" in bot_response.lower():
                    print(f"   ✅ Conversation continues correctly (asking for date)")
                elif description == "Start booking" and "need" in bot_response.lower():
                    print(f"   ✅ Started booking process correctly")
                    
                conversation_history.append({"role": "user", "content": user_message})
                conversation_history.append({"role": "assistant", "content": bot_response})
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
        
        time.sleep(1)

if __name__ == "__main__":
    # Wait a moment for server to start
    print("Waiting for server to be ready...")
    time.sleep(3)
    test_multi_step_booking()

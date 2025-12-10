"""
Direct test of multi-step conversation without API
"""

from agents.agent import DoctorAppointmentAgent
from langchain_core.messages import HumanMessage

def test_direct_multi_step():
    """Test multi-step conversation directly"""
    print("=" * 60)
    print("DIRECT TEST OF MULTI-STEP APPOINTMENT BOOKING")
    print("=" * 60)
    
    # Initialize agent
    agent = DoctorAppointmentAgent()
    app_graph = agent.workflow()
    
    patient_id = 2
    
    test_steps = [
        ("book appointment", "Start booking process"),
        ("Dr. Mohamed Tajmouati", "Provide doctor name"),
        ("15-12-2024", "Provide date"),
        ("14:30", "Provide time")
    ]
    
    # Start with empty state
    state = {
        "messages": [],
        "id_number": patient_id,
        "next": "",
        "query": "",
        "current_reasoning": "",
        "pending_action": "",
        "pending_data": {}
    }
    
    for user_message, description in test_steps:
        print(f"\n📝 Step: {description}")
        print(f"   User: '{user_message}'")
        
        # Add user message to state
        state["messages"].append(HumanMessage(content=user_message))
        
        try:
            # Run agent
            response = app_graph.invoke(
                state,
                config={
                    "recursion_limit": 40,
                    "configurable": {"thread_id": "session_1"}
                }
            )
            
            # Extract assistant response
            assistant_response = None
            for msg in response["messages"]:
                if hasattr(msg, "content") and not isinstance(msg, HumanMessage):
                    assistant_response = msg.content
                    sender = getattr(msg, "name", "assistant")
                    break
            
            if assistant_response:
                print(f"   ✅ Success!")
                print(f"   🤖 {sender}: {assistant_response[:100]}...")
                
                # Update state for next iteration
                state = response
                
                # Check conversation flow
                if description == "Start booking process" and "need" in assistant_response.lower():
                    print(f"   ✅ Correctly started booking process")
                elif description == "Provide doctor name" and "date" in assistant_response.lower():
                    print(f"   ✅ Correctly asked for date")
                elif description == "Provide date" and "time" in assistant_response.lower():
                    print(f"   ✅ Correctly asked for time")
                elif description == "Provide time" and ("confirmed" in assistant_response.lower() or "success" in assistant_response.lower()):
                    print(f"   🎉 Appointment booked successfully!")
                    
            else:
                print(f"   ❌ No assistant response")
                print(f"   State: {state}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("DIRECT TEST COMPLETE")
    print("=" * 60)
    
    # Test the exact scenario from user feedback
    print("\n" + "=" * 60)
    print("TESTING EXACT USER FEEDBACK SCENARIO")
    print("=" * 60)
    
    # Reset state
    state = {
        "messages": [],
        "id_number": patient_id,
        "next": "",
        "query": "",
        "current_reasoning": "",
        "pending_action": "",
        "pending_data": {}
    }
    
    user_scenario = [
        ("book appointment", "User: book appointment"),
        ("Dr. Mohamed Tajmouati", "User: Dr. Mohamed Tajmouati"),
        ("15-12-2024", "User: 15-12-2024")
    ]
    
    for user_message, step_description in user_scenario:
        print(f"\n{step_description}")
        
        # Add user message
        state["messages"].append(HumanMessage(content=user_message))
        
        try:
            response = app_graph.invoke(
                state,
                config={
                    "recursion_limit": 40,
                    "configurable": {"thread_id": "session_1"}
                }
            )
            
            # Get assistant response
            assistant_response = None
            sender = "assistant"
            for msg in response["messages"]:
                if hasattr(msg, "content") and not isinstance(msg, HumanMessage):
                    assistant_response = msg.content
                    sender = getattr(msg, "name", "assistant")
                    break
            
            if assistant_response:
                print(f"   {sender}: {assistant_response[:80]}...")
                
                # Check if conversation continues
                if step_description == "User: book appointment" and "need" in assistant_response.lower():
                    print(f"   ✅ Started booking correctly")
                elif step_description == "User: Dr. Mohamed Tajmouati" and "date" in assistant_response.lower():
                    print(f"   ✅ Asked for date correctly")
                elif step_description == "User: 15-12-2024" and "time" in assistant_response.lower():
                    print(f"   ✅ Asked for time correctly - CONVERSATION CONTINUES!")
                else:
                    print(f"   ⚠️ Unexpected response")
                    
                state = response
            else:
                print(f"   ❌ No response")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    test_direct_multi_step()

"""
Test the fixed hierarchical agent system
"""

from agents.hierarchical_agent import HierarchicalAgentSystem
from langchain_core.messages import HumanMessage

def test_hierarchical_system():
    """Test the hierarchical system with various inputs"""
    print("=" * 60)
    print("TESTING FIXED HIERARCHICAL AGENT SYSTEM")
    print("=" * 60)
    
    # Initialize the system
    agent = HierarchicalAgentSystem()
    
    test_cases = [
        ("hello", 2, "Greeting → FAQ agent"),
        ("Get my patient information", 2, "Patient info → Patient agent"),
        ("Is Dr. Mohamed available tomorrow?", 2, "Availability → Availability agent"),
        ("book appointment", 2, "Booking → Appointment agent"),
        ("What are your services?", 2, "FAQ → FAQ agent"),
    ]
    
    for message, patient_id, description in test_cases:
        print(f"\n📝 Test: {description}")
        print(f"   Patient ID: {patient_id}")
        print(f"   Message: '{message}'")
        
        try:
            # Prepare input
            input_message = [HumanMessage(content=message)]
            
            # Run hierarchical agent
            response = agent.invoke(
                messages=input_message,
                patient_id=patient_id
            )
            
            print(f"   ✅ Success!")
            
            # Extract response
            for msg in response.get("messages", []):
                if hasattr(msg, "content") and not isinstance(msg, HumanMessage):
                    content = msg.content
                    # Truncate long responses
                    if len(content) > 100:
                        content = content[:100] + "..."
                    print(f"   🤖 Agent: {getattr(msg, 'name', 'unknown')}")
                    print(f"   📝 Response: {content}")
                    break
            
            # Show hierarchy info
            if response.get("current_niveau"):
                print(f"   🏗️ Level: {response.get('current_niveau')}")
                print(f"   👤 Agent: {response.get('current_agent')}")
                print(f"   📊 Logs: {len(response.get('logs', []))} entries")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("HIERARCHICAL SYSTEM TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_hierarchical_system()

#!/usr/bin/env python3
"""Test the agent directly without HTTP server."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_agent_directly():
    """Test agent directly."""
    print("Testing agent directly...")
    
    try:
        from agents.agent import DoctorAppointmentAgent
        from langchain_core.messages import HumanMessage
        
        # Create agent
        agent = DoctorAppointmentAgent()
        app_graph = agent.workflow()
        
        # Test 1: Simple greeting
        print("\nTest 1: Simple greeting 'hello'")
        query_state = {
            "messages": [HumanMessage(content="hello")],
            "id_number": 1,
            "next": "",
            "query": "",
            "current_reasoning": "",
        }
        
        response = app_graph.invoke(
            query_state,
            config={
                "recursion_limit": 40,
                "configurable": {"thread_id": "session_1"}
            }
        )
        
        print(f"Response messages: {len(response.get('messages', []))}")
        for msg in response.get("messages", []):
            if hasattr(msg, 'content'):
                print(f"  - {msg.content[:100]}...")
        
        # Test 2: Availability question
        print("\nTest 2: Availability question")
        query_state = {
            "messages": [HumanMessage(content="Is Dr. Mohamed Tajmouati available tomorrow?")],
            "id_number": 2,
            "next": "",
            "query": "",
            "current_reasoning": "",
        }
        
        response = app_graph.invoke(
            query_state,
            config={
                "recursion_limit": 40,
                "configurable": {"thread_id": "session_2"}
            }
        )
        
        print(f"Response messages: {len(response.get('messages', []))}")
        for msg in response.get("messages", []):
            if hasattr(msg, 'content'):
                print(f"  - {msg.content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run test."""
    print("=" * 60)
    print("Direct Agent Test")
    print("=" * 60)
    
    if test_agent_directly():
        print("\n✅ Agent test passed!")
        return True
    else:
        print("\n❌ Agent test failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

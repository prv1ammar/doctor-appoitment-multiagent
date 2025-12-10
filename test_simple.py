#!/usr/bin/env python3
"""Simple test to diagnose the chatbot issue."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_llm():
    """Test if LLM works."""
    print("Testing LLM...")
    try:
        from utils.llms import LLMModel
        llm = LLMModel()
        model = llm.get_model()
        
        # Test simple invocation
        response = model.invoke("Hello")
        print(f"LLM Response: {response}")
        print(f"LLM Type: {type(model)}")
        print(f"Using mock: {getattr(llm, 'using_mock', 'unknown')}")
        return True
    except Exception as e:
        print(f"LLM Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_import():
    """Test if agent imports work."""
    print("\nTesting agent imports...")
    try:
        from agents.agent import DoctorAppointmentAgent
        agent = DoctorAppointmentAgent()
        print("Agent created successfully")
        return True
    except Exception as e:
        print(f"Agent Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tools():
    """Test if tools work."""
    print("\nTesting tools...")
    try:
        from toolkit.toolkits import check_availability_by_doctor
        # Test with simple parameters
        result = check_availability_by_doctor.func("04-12-2025", "Dr.Mohamed Tajmouati")
        print(f"Tool result: {result[:100]}...")
        return True
    except Exception as e:
        print(f"Tool Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_import():
    """Test if main.py imports work."""
    print("\nTesting main.py imports...")
    try:
        # This simulates what happens when uvicorn imports main.py
        exec(open("main.py").read())
        print("main.py imports work")
        return True
    except Exception as e:
        print(f"main.py Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Diagnosing Chatbot Issues")
    print("=" * 60)
    
    tests = [
        ("LLM", test_llm),
        ("Agent Import", test_agent_import),
        ("Tools", test_tools),
        ("Main Import", test_main_import),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"Test: {name}")
        print(f"{'='*40}")
        result = test_func()
        results.append((name, result))
        if not result:
            print(f"❌ {name} FAILED")
        else:
            print(f"✅ {name} PASSED")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✅ All tests passed! The issue might be elsewhere.")
        print("Try running: python -m uvicorn main:app --reload --port 8003")
    else:
        print("\n❌ Some tests failed. Fix these issues first.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

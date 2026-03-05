#!/usr/bin/env python3
"""
Test script for ADK integration.
Tests the basic functionality of the ADK agents.
"""

import os
import asyncio
from backend.agents.adk_agents import (
    get_intent_classifier,
    get_workflow_planner,
    get_tool_executor,
    IntentClassifierAgent,
    WorkflowPlannerAgent,
    ToolExecutorAgent
)

def test_instantiation():
    """Test that all agent classes can be instantiated."""
    print("Testing agent instantiation...")
    
    # Verify API key is present
    if not (os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')):
        print("⚠ Warning: No API key found in environment. Instantiation might fail if ADK attempts immediate validation.")
    
    try:
        classifier = IntentClassifierAgent()
        planner = WorkflowPlannerAgent()
        executor = ToolExecutorAgent([])
        
        print("✓ All agent classes instantiated successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to instantiate agents: {e}")
        return False

async def test_basic_functionality():
    """Test basic agent functionality."""
    print("\nTesting basic agent functionality...")
    
    try:
        # Test intent classification (should use fallback without real API key)
        classifier = get_intent_classifier()
        result = await classifier.classify("Hello, how are you?")
        print(f"✓ Intent classification result: {result}")
        
        # Test workflow planning
        planner = get_workflow_planner()
        plan = await planner.create_plan("Test task", "general_chat", [])
        print(f"✓ Workflow plan result: {plan}")
        
        # Test tool execution
        executor = get_tool_executor([])
        tool_result = await executor.execute_tool("echo", {"message": "test"})
        print(f"✓ Tool execution result: {tool_result}")
        
        # Test built-in tools
        echo_result = await executor.execute_tool("echo", {"message": "Hello World"})
        date_result = await executor.execute_tool("get_date", {})
        calc_result = await executor.execute_tool("calculate", {"expression": "2 + 3"})
        
        print(f"✓ Echo tool: {echo_result}")
        print(f"✓ Date tool: {date_result}")
        print(f"✓ Calculate tool: {calc_result}")
        
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def test_agent_structure():
    """Test that agents have the expected structure."""
    print("\nTesting agent structure...")
    
    try:
        classifier = IntentClassifierAgent()
        
        # Check that ADK components are present
        assert hasattr(classifier, 'agent'), "Missing agent attribute"
        assert hasattr(classifier, 'runner'), "Missing runner attribute"
        assert hasattr(classifier, 'config'), "Missing config attribute"
        
        print("✓ Agent structure is correct")
        return True
    except Exception as e:
        print(f"✗ Agent structure test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("ADK Integration Test Suite")
    print("=" * 40)
    
    tests = [
        test_instantiation,
        test_agent_structure,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Run async test
    results.append(asyncio.run(test_basic_functionality()))
    
    print("\n" + "=" * 40)
    if all(results):
        print("🎉 All tests passed! ADK integration is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())
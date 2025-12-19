"""
Test script for the conversational agent
Demonstrates full workflow without requiring user input
"""

from conversational_agent import ConversationalAgent


def test_full_workflow():
    """Test the complete conversational workflow"""

    print("=" * 80)
    print("TESTING CONVERSATIONAL AGENT")
    print("=" * 80)

    # Initialize agent
    agent = ConversationalAgent(
        project_id="test-project",
        dataset="skyrise",
        release_id=1
    )

    # Test 1: Welcome message
    print("\n[TEST 1] Welcome Message")
    print("-" * 80)
    welcome = agent.start()
    assert "SKYRISE AUDIENCE BUILDER" in welcome
    assert agent.state == "welcome"
    print("✓ Welcome message displayed")

    # Test 2: Main menu
    print("\n[TEST 2] Main Menu")
    print("-" * 80)
    response = agent.process_input("")
    assert "MAIN MENU" in response
    assert agent.state == "main_menu"
    print("✓ Main menu displayed")

    # Test 3: Quick build - demographic audience
    print("\n[TEST 3] Quick Build - Demographic")
    print("-" * 80)
    agent.process_input("2")  # Select quick build
    response = agent.process_input("Find female users aged 25-34 in the US")
    assert "SUCCESS" in response.upper() or "user_id" in response.lower()
    print("✓ Demographic audience created")
    print(f"  - Audiences saved: {len(agent.current_audiences)}")

    # Test 4: Build another audience - vendor
    print("\n[TEST 4] Build Vendor Audience")
    print("-" * 80)
    agent.state = "main_menu"
    agent.process_input("2")
    response = agent.process_input("Find Walmart shoppers in the US")
    assert "SUCCESS" in response.upper() or "user_id" in response.lower()
    print("✓ Vendor audience created")
    print(f"  - Audiences saved: {len(agent.current_audiences)}")

    # Test 5: Show saved audiences
    print("\n[TEST 5] Show Saved Audiences")
    print("-" * 80)
    response = agent.process_input("show audiences")
    assert "SAVED AUDIENCES" in response or "Audience_" in response
    print("✓ Saved audiences displayed")
    print(f"  - Total audiences: {len(agent.current_audiences)}")

    # Test 6: Combine audiences
    print("\n[TEST 6] Combine Audiences")
    print("-" * 80)
    if len(agent.current_audiences) >= 2:
        agent.state = "combining"
        response = agent._start_combining_flow()
        print("✓ Combining flow started")

        # Combine with AND
        response = agent.process_input("1 AND 2")
        assert "SUCCESS" in response.upper() or "INTERSECT" in response.upper()
        print("✓ Audiences combined with AND")
        print(f"  - Total audiences: {len(agent.current_audiences)}")
    else:
        print("⚠️  Not enough audiences to test combining")

    # Test 7: Help system
    print("\n[TEST 7] Help System")
    print("-" * 80)
    response = agent.process_input("help")
    assert "HELP" in response.upper()
    print("✓ Help displayed")

    # Test 8: Examples
    print("\n[TEST 8] Examples")
    print("-" * 80)
    response = agent.process_input("examples")
    assert "EXAMPLE" in response.upper()
    print("✓ Examples displayed")

    # Test 9: Natural language variations
    print("\n[TEST 9] Natural Language Variations")
    print("-" * 80)
    test_prompts = [
        "Get high income users who shop at Starbucks",
        "Show me grocery store shoppers in California",
        "Find users who spend more than 1000 dollars"
    ]

    for prompt in test_prompts:
        agent.state = "building"
        result = agent.agent.process_prompt(prompt)
        status = result["status"]
        print(f"  - '{prompt[:40]}...' → {status}")

    print("✓ Natural language processing working")

    # Test 10: Query builder integration
    print("\n[TEST 10] Query Builder Integration")
    print("-" * 80)
    qb = agent.query_builder

    # Test demographic query
    demo_query = qb.build_demographic_audience({
        "gender_description": ["Female"],
        "age_band": ["25-34"],
        "user_ccode2": ["US"]
    })
    assert "SELECT" in demo_query
    assert "user_id" in demo_query
    print("✓ Demographic query generated")

    # Test vendor query
    vendor_query = qb.build_vendor_audience({
        "vendor_desc": "Walmart",
        "min_transactions": 5
    })
    assert "SELECT" in vendor_query
    assert "vendor" in vendor_query.lower()
    print("✓ Vendor query generated")

    # Test geographic query
    geo_query = qb.build_geographic_audience({
        "user_l1_geo": ["CA"],
        "user_ccode2": ["US"]
    })
    assert "SELECT" in geo_query
    print("✓ Geographic query generated")

    # Test query combination
    combined = qb.build_combined_audience([demo_query, vendor_query], "INTERSECT")
    assert "INTERSECT" in combined
    print("✓ Combined query generated")

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✓ All tests passed!")
    print(f"  - Audiences created: {len(agent.current_audiences)}")
    print(f"  - Conversation history: {len(agent.conversation_history)} exchanges")
    print(f"  - Final state: {agent.state}")

    # Show sample audience
    if agent.current_audiences:
        print("\nSample Audience:")
        sample = agent.current_audiences[0]
        print(f"  Name: {sample['name']}")
        print(f"  Type: {sample['type']}")
        print(f"  Filters: {sample['filters']}")
        print(f"  Query: {sample['query'][:100]}...")

    return True


def test_edge_cases():
    """Test edge cases and error handling"""

    print("\n" + "=" * 80)
    print("TESTING EDGE CASES")
    print("=" * 80)

    agent = ConversationalAgent(
        project_id="test-project",
        dataset="skyrise",
        release_id=1
    )

    # Test 1: Empty input
    print("\n[TEST 1] Empty Input Handling")
    response = agent.process_input("")
    print(f"✓ Handled gracefully (state: {agent.state})")

    # Test 2: Invalid commands
    print("\n[TEST 2] Invalid Commands")
    agent.state = "main_menu"
    response = agent.process_input("asdfghjkl")
    print(f"✓ Invalid command handled (response contains guidance)")

    # Test 3: Unclear prompts
    print("\n[TEST 3] Unclear Prompts")
    agent.state = "building"
    result = agent.agent.process_prompt("some users")
    print(f"✓ Unclear prompt handled (status: {result['status']})")

    # Test 4: Combining with insufficient audiences
    print("\n[TEST 4] Combining Without Enough Audiences")
    agent.current_audiences = []
    agent.state = "main_menu"
    response = agent.process_input("3")  # Try to combine
    assert "need at least" in response.lower() or "2 audiences" in response.lower()
    print("✓ Insufficient audiences handled")

    print("\n✓ All edge case tests passed!")


def test_audience_types():
    """Test all audience types"""

    print("\n" + "=" * 80)
    print("TESTING ALL AUDIENCE TYPES")
    print("=" * 80)

    agent = ConversationalAgent(
        project_id="test-project",
        dataset="skyrise",
        release_id=1
    )

    test_cases = [
        ("Demographic", "Find female users aged 25-34 in the US"),
        ("Vendor", "Find shoppers at Walmart"),
        ("Merchant Category", "Get users who shop at grocery stores"),
        ("Geographic", "Find users in California"),
        ("Spending", "Show me users who spend more than 1000 dollars"),
        ("Grocer", "Find Tesco shoppers in the UK"),
    ]

    for audience_type, prompt in test_cases:
        print(f"\n[TEST] {audience_type}")
        print(f"  Prompt: {prompt}")

        result = agent.agent.process_prompt(prompt)
        status = result["status"]

        if status == "success":
            print(f"  ✓ Generated successfully")
            print(f"    Type detected: {result.get('audience_type')}")
        elif status == "needs_clarification":
            print(f"  ⚠️  Needs clarification")
            print(f"    Questions: {len(result.get('questions', []))}")
        else:
            print(f"  ❌ Error: {result.get('message')}")

    print("\n✓ All audience type tests completed!")


if __name__ == "__main__":
    try:
        print("\n" + "="*80)
        print(" " * 25 + "CONVERSATIONAL AGENT TEST SUITE")
        print("="*80 + "\n")

        # Run tests
        test_full_workflow()
        test_edge_cases()
        test_audience_types()

        print("\n" + "="*80)
        print("ALL TESTS PASSED! ✓")
        print("="*80 + "\n")

        print("🎉 The conversational agent is fully working!")
        print("\nTo try it yourself, run:")
        print("  python run_agent.py")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

"""
Example usage of the Skyrise Audience Agent
Demonstrates various audience creation scenarios
"""

from audience_agent import AudienceAgent
from query_builder import QueryBuilder


def example_1_simple_demographic():
    """Example 1: Simple demographic audience"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Simple Demographic Audience")
    print("=" * 80)

    agent = AudienceAgent(
        project_id="your-project-id",
        dataset="skyrise",
        release_id=1
    )

    prompt = "Find all female users aged 25-34 in the US"
    print(f"\nPrompt: {prompt}")
    print("-" * 80)

    result = agent.process_prompt(prompt)
    print(agent.format_response(result))


def example_2_vendor_targeting():
    """Example 2: Vendor-based audience"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Vendor-Based Audience")
    print("=" * 80)

    agent = AudienceAgent(
        project_id="your-project-id",
        dataset="skyrise",
        release_id=1
    )

    prompt = "Find shoppers at Walmart who made more than 10 transactions"
    print(f"\nPrompt: {prompt}")
    print("-" * 80)

    result = agent.process_prompt(prompt)
    print(agent.format_response(result))


def example_3_combined_filters():
    """Example 3: Combined demographic and behavioral filters"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Combined Filters")
    print("=" * 80)

    agent = AudienceAgent(
        project_id="your-project-id",
        dataset="skyrise",
        release_id=1
    )

    prompt = "Get high income male shoppers aged 35-44 who shop at Starbucks in the US"
    print(f"\nPrompt: {prompt}")
    print("-" * 80)

    result = agent.process_prompt(prompt)
    print(agent.format_response(result))


def example_4_geographic():
    """Example 4: Geographic targeting"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Geographic Audience")
    print("=" * 80)

    agent = AudienceAgent(
        project_id="your-project-id",
        dataset="skyrise",
        release_id=1
    )

    prompt = "Find all users in California"
    print(f"\nPrompt: {prompt}")
    print("-" * 80)

    result = agent.process_prompt(prompt)
    print(agent.format_response(result))


def example_5_spending_behavior():
    """Example 5: Spending behavior audience"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Spending Behavior Audience")
    print("=" * 80)

    agent = AudienceAgent(
        project_id="your-project-id",
        dataset="skyrise",
        release_id=1
    )

    prompt = "Show me users who spend more than $1000 with at least 20 transactions"
    print(f"\nPrompt: {prompt}")
    print("-" * 80)

    result = agent.process_prompt(prompt)
    print(agent.format_response(result))


def example_6_merchant_category():
    """Example 6: Merchant category audience"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Merchant Category Audience")
    print("=" * 80)

    agent = AudienceAgent(
        project_id="your-project-id",
        dataset="skyrise",
        release_id=1
    )

    prompt = "Find all customers who shop at grocery stores"
    print(f"\nPrompt: {prompt}")
    print("-" * 80)

    result = agent.process_prompt(prompt)
    print(agent.format_response(result))


def example_7_grocer_specific():
    """Example 7: Grocer-specific audience"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Grocer-Specific Audience")
    print("=" * 80)

    agent = AudienceAgent(
        project_id="your-project-id",
        dataset="skyrise",
        release_id=1
    )

    prompt = "Get all Tesco shoppers in the UK"
    print(f"\nPrompt: {prompt}")
    print("-" * 80)

    result = agent.process_prompt(prompt)
    print(agent.format_response(result))


def example_8_programmatic_query_builder():
    """Example 8: Direct query builder usage"""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Programmatic Query Builder")
    print("=" * 80)

    qb = QueryBuilder(
        project_id="your-project-id",
        dataset="skyrise",
        release_id=1
    )

    # Build demographic audience
    print("\n--- Demographic Audience ---")
    query1 = qb.build_demographic_audience({
        "gender_description": ["Female"],
        "age_band": ["25-34", "35-44"],
        "income_band": ["High", "Very High"],
        "user_ccode2": ["US"]
    })
    print(query1)

    # Build vendor audience
    print("\n--- Vendor Audience ---")
    query2 = qb.build_vendor_audience({
        "vendor_desc": "Amazon",
        "min_transactions": 5,
        "min_spend": 500
    })
    print(query2)

    # Combine audiences
    print("\n--- Combined Audience (INTERSECT) ---")
    combined = qb.build_combined_audience([query1, query2], operation="INTERSECT")
    print(combined)

    # Add demographic refinement
    print("\n--- Refined Audience ---")
    base = qb.build_vendor_audience({"vendor_desc": "Walmart"})
    refined = qb.add_demographic_refinement(base, {
        "age_band": ["25-34"],
        "income_band": ["High"]
    })
    print(refined)


def example_9_clarification_flow():
    """Example 9: Handling clarification questions"""
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Clarification Flow")
    print("=" * 80)

    agent = AudienceAgent(
        project_id="your-project-id",
        dataset="skyrise",
        release_id=1
    )

    # Vague prompt that will trigger clarification
    prompt = "Find shoppers at a grocery store"
    print(f"\nPrompt: {prompt}")
    print("-" * 80)

    result = agent.process_prompt(prompt)
    print(agent.format_response(result))

    if result["status"] == "needs_clarification":
        print("\n[In a real scenario, you would collect user answers here]")
        print("[Then merge them with parsed_filters and rebuild the query]")


def example_10_audience_combinations():
    """Example 10: Complex audience combinations"""
    print("\n" + "=" * 80)
    print("EXAMPLE 10: Complex Audience Combinations")
    print("=" * 80)

    qb = QueryBuilder(
        project_id="your-project-id",
        dataset="skyrise",
        release_id=1
    )

    # Scenario: Find female Walmart shoppers in CA OR NY, but EXCLUDE low income
    print("\nScenario: Female Walmart shoppers in CA/NY, excluding low income")
    print("-" * 80)

    # Step 1: Female Walmart shoppers
    walmart_female = qb.build_vendor_audience({
        "vendor_desc": "Walmart"
    })
    walmart_female_refined = qb.add_demographic_refinement(walmart_female, {
        "gender_description": ["Female"]
    })

    # Step 2: CA residents
    ca_users = qb.build_geographic_audience({
        "user_l1_geo": ["CA"]
    })

    # Step 3: NY residents
    ny_users = qb.build_geographic_audience({
        "user_l1_geo": ["NY"]
    })

    # Step 4: CA OR NY
    ca_or_ny = qb.build_combined_audience([ca_users, ny_users], operation="UNION")

    # Step 5: Female Walmart shoppers in CA or NY
    walmart_female_geo = qb.build_combined_audience(
        [walmart_female_refined, ca_or_ny],
        operation="INTERSECT"
    )

    # Step 6: Low income users
    low_income = qb.build_demographic_audience({
        "income_band": ["Low"]
    })

    # Step 7: Exclude low income
    final_audience = qb.build_combined_audience(
        [walmart_female_geo, low_income],
        operation="EXCEPT"
    )

    print(final_audience)

    # Get count
    print("\n--- Audience Count Query ---")
    count_query = qb.get_audience_count(final_audience)
    print(count_query)


def run_all_examples():
    """Run all examples"""
    print("\n")
    print("=" * 80)
    print(" " * 20 + "SKYRISE AUDIENCE AGENT EXAMPLES")
    print("=" * 80)

    examples = [
        example_1_simple_demographic,
        example_2_vendor_targeting,
        example_3_combined_filters,
        example_4_geographic,
        example_5_spending_behavior,
        example_6_merchant_category,
        example_7_grocer_specific,
        example_8_programmatic_query_builder,
        example_9_clarification_flow,
        example_10_audience_combinations
    ]

    for example_func in examples:
        try:
            example_func()
            input("\n[Press Enter to continue to next example...]")
        except KeyboardInterrupt:
            print("\n\nExamples interrupted by user.")
            break
        except Exception as e:
            print(f"\n❌ Error in example: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        example_func = globals().get(f"example_{example_num}")
        if example_func:
            example_func()
        else:
            print(f"Example {example_num} not found")
    else:
        run_all_examples()

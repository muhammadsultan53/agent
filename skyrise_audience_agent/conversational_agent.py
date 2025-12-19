"""
Conversational Audience Builder Agent
Guides users step-by-step through building audiences with natural conversation
"""

import json
from typing import Dict, List, Any, Optional
from audience_agent import AudienceAgent
from query_builder import QueryBuilder
from schema_config import VALID_FILTERS, COMMON_MERCHANTS, COMMON_GROCERS


class ConversationalAgent:
    """
    Interactive conversational agent that guides users through audience creation
    """

    def __init__(self, project_id: str = None, dataset: str = None, release_id: int = None):
        self.agent = AudienceAgent(project_id, dataset, release_id)
        self.query_builder = QueryBuilder(project_id, dataset, release_id)

        # Conversation state
        self.state = "welcome"  # welcome, main_menu, building, combining, reviewing, help
        self.current_audiences = []  # List of built audiences
        self.current_filters = {}
        self.pending_questions = []
        self.conversation_history = []

    def start(self) -> str:
        """Start the conversation"""
        self.state = "welcome"
        return self._get_welcome_message()

    def process_input(self, user_input: str) -> str:
        """Process user input and return response"""
        self.conversation_history.append({"role": "user", "message": user_input})

        # Handle special commands
        if user_input.lower() in ["help", "?"]:
            response = self._get_help_message()
        elif user_input.lower() in ["menu", "start over", "restart"]:
            self.state = "main_menu"
            response = self._get_main_menu()
        elif user_input.lower() in ["examples", "show examples"]:
            response = self._get_examples()
        elif user_input.lower() in ["quit", "exit", "bye"]:
            response = self._get_goodbye_message()
        elif user_input.lower() in ["show audiences", "list", "list audiences"]:
            response = self._show_saved_audiences()
        else:
            # Process based on current state
            response = self._process_by_state(user_input)

        self.conversation_history.append({"role": "agent", "message": response})
        return response

    def _process_by_state(self, user_input: str) -> str:
        """Process input based on current conversation state"""

        if self.state == "welcome":
            self.state = "main_menu"
            return self._get_main_menu()

        elif self.state == "main_menu":
            return self._handle_main_menu_choice(user_input)

        elif self.state == "building":
            return self._handle_audience_building(user_input)

        elif self.state == "answering_questions":
            return self._handle_clarification_answers(user_input)

        elif self.state == "combining":
            return self._handle_audience_combining(user_input)

        elif self.state == "reviewing":
            return self._handle_review(user_input)

        else:
            return "I'm not sure what to do. Type 'menu' to go back to the main menu."

    def _get_welcome_message(self) -> str:
        """Get welcome message"""
        return """
╔══════════════════════════════════════════════════════════════════════════╗
║                   SKYRISE AUDIENCE BUILDER AGENT                        ║
║                    Your AI Audience Creation Assistant                  ║
╚══════════════════════════════════════════════════════════════════════════╝

👋 Hello! I'm your Skyrise Audience Builder assistant!

I'll help you create targeted audiences from your Skyrise transaction data.
I can guide you through:

  📊 Building audiences step-by-step
  🎯 Filtering by demographics, behavior, location, and more
  🔗 Combining multiple audiences with AND/OR logic
  📝 Generating optimized SQL queries for BigQuery
  💡 Providing examples and suggestions

Ready to get started? Press Enter to continue...
"""

    def _get_main_menu(self) -> str:
        """Get main menu options"""
        menu = """
═══════════════════════════════════════════════════════════════════════════
                              MAIN MENU
═══════════════════════════════════════════════════════════════════════════

What would you like to do?

1️⃣  Build a New Audience
   → Create an audience from scratch with step-by-step guidance

2️⃣  Quick Build (Natural Language)
   → Describe your audience in plain English and I'll build it

3️⃣  Combine Existing Audiences
   → Merge, intersect, or exclude audiences using AND/OR/NOT logic

4️⃣  Show Examples
   → See example prompts and what I can do

5️⃣  Help & Tips
   → Learn about audience types, filters, and best practices
"""

        if self.current_audiences:
            menu += f"\n📋 You have {len(self.current_audiences)} saved audience(s)"

        menu += "\n\n💬 Enter your choice (1-5) or type your request:"
        return menu

    def _handle_main_menu_choice(self, user_input: str) -> str:
        """Handle main menu selection"""
        choice = user_input.strip().lower()

        if choice in ["1", "build", "build new", "new audience"]:
            self.state = "building_guided"
            return self._start_guided_build()

        elif choice in ["2", "quick", "quick build", "natural language"]:
            self.state = "building"
            return """
╔══════════════════════════════════════════════════════════════════════════╗
║                        QUICK BUILD MODE                                 ║
╚══════════════════════════════════════════════════════════════════════════╝

Great! Just describe the audience you want in plain English.

📝 Examples:
  • "Find female users aged 25-34 in the US"
  • "Get high income shoppers at Walmart"
  • "Show me customers who spend over $1000 at coffee shops"
  • "Find grocery store shoppers in California"

💬 Describe your audience:"""

        elif choice in ["3", "combine", "merge", "join"]:
            if len(self.current_audiences) < 2:
                return """
⚠️  You need at least 2 audiences to combine them.

Let's build some audiences first! Type 'menu' to go back.
"""
            self.state = "combining"
            return self._start_combining_flow()

        elif choice in ["4", "examples", "show examples"]:
            return self._get_examples() + "\n\nType 'menu' when ready to continue."

        elif choice in ["5", "help", "tips"]:
            return self._get_help_message() + "\n\nType 'menu' when ready to continue."

        else:
            # Try to interpret as natural language
            self.state = "building"
            return self._handle_audience_building(user_input)

    def _start_guided_build(self) -> str:
        """Start guided audience building"""
        return """
╔══════════════════════════════════════════════════════════════════════════╗
║                      GUIDED AUDIENCE BUILDER                            ║
╚══════════════════════════════════════════════════════════════════════════╝

I'll guide you step-by-step to build your audience!

STEP 1: Choose Audience Type
─────────────────────────────

1️⃣  Demographic → Filter by age, gender, income, etc.
2️⃣  Store/Brand → Target customers of specific stores
3️⃣  Shopping Category → Target by merchant categories (grocery, restaurants, etc.)
4️⃣  Geographic → Filter by location (country, state, city, radius)
5️⃣  Spending Behavior → Filter by spend amounts and transaction frequency
6️⃣  Grocer Specific → Target grocery store shoppers

💬 Which type would you like? (1-6):"""

    def _handle_audience_building(self, user_input: str) -> str:
        """Handle audience building from natural language"""
        result = self.agent.process_prompt(user_input)

        if result["status"] == "needs_clarification":
            self.pending_questions = result["questions"]
            self.current_filters = result.get("parsed_filters", {})
            self.state = "answering_questions"
            return self._format_clarifying_questions(result)

        elif result["status"] == "success":
            return self._format_success_result(result)

        else:
            return f"""
❌ Oops! I encountered an error: {result['message']}

Let me help you fix this. Could you rephrase your request?
Or type 'examples' to see what I can do.
"""

    def _format_clarifying_questions(self, result: Dict[str, Any]) -> str:
        """Format clarifying questions in a conversational way"""
        output = ["\n🤔 I need a bit more information to build your audience:\n"]

        questions = result["questions"]
        for i, q in enumerate(questions, 1):
            output.append(f"\n{i}. {q['question']}")

            if q["type"] in ["choice", "choice_optional"]:
                # Show as numbered list
                output.append("   Options:")
                for j, opt in enumerate(q["options"][:8], 1):  # Show first 8
                    output.append(f"     {j}) {opt}")
                if len(q["options"]) > 8:
                    output.append(f"     ... and {len(q['options']) - 8} more")

            if q["type"] == "choice_optional":
                output.append("   (or type 'skip' to skip this filter)")

        output.append("\n💬 Please answer question 1:")
        return "\n".join(output)

    def _handle_clarification_answers(self, user_input: str) -> str:
        """Handle answers to clarifying questions"""
        if not self.pending_questions:
            self.state = "building"
            return "Something went wrong. Let's start over. Type 'menu' to return."

        # Get current question
        current_q = self.pending_questions[0]

        # Process answer
        if user_input.lower() in ["skip", "no", "none"]:
            answer = None
        else:
            answer = user_input.strip()

            # For choice questions, try to match
            if current_q["type"] in ["choice", "choice_optional"]:
                # Try exact match
                if answer not in current_q["options"]:
                    # Try partial match
                    matches = [opt for opt in current_q["options"] if answer.lower() in opt.lower()]
                    if matches:
                        answer = matches[0]
                    else:
                        return f"""
⚠️  '{answer}' is not a valid option.

Please choose from: {', '.join(current_q['options'][:5])}
{'...' if len(current_q['options']) > 5 else ''}

💬 Your answer:"""

        # Store answer
        if answer:
            self.current_filters[current_q["key"]] = answer

        # Remove answered question
        self.pending_questions.pop(0)

        # More questions?
        if self.pending_questions:
            next_q = self.pending_questions[0]
            output = [f"\n✓ Got it! {answer if answer else 'Skipped'}\n"]
            output.append(f"{len(self.current_filters) + 1}. {next_q['question']}")

            if next_q["type"] in ["choice", "choice_optional"]:
                output.append("   Options:")
                for j, opt in enumerate(next_q["options"][:8], 1):
                    output.append(f"     {j}) {opt}")
                if len(next_q["options"]) > 8:
                    output.append(f"     ... and {len(next_q['options']) - 8} more")

            output.append("\n💬 Your answer:")
            return "\n".join(output)

        # All questions answered, build the query
        else:
            # Rebuild with all filters
            audience_info = {
                "type": self.current_filters.get("_type", "demographic"),
                "filters": self.current_filters
            }

            try:
                query = self.agent._build_query_from_info(audience_info)
                result = {
                    "status": "success",
                    "query": query,
                    "filters": self.current_filters,
                    "audience_type": audience_info["type"],
                    "count_query": self.query_builder.get_audience_count(query),
                    "export_query": self.query_builder.get_audience_export(query)
                }
                return self._format_success_result(result)
            except Exception as e:
                return f"❌ Error building query: {str(e)}\n\nType 'menu' to start over."

    def _format_success_result(self, result: Dict[str, Any]) -> str:
        """Format successful query generation"""
        output = ["""
╔══════════════════════════════════════════════════════════════════════════╗
║                     ✓ AUDIENCE CREATED SUCCESSFULLY!                    ║
╚══════════════════════════════════════════════════════════════════════════╝
"""]

        # Show audience summary
        output.append(f"📊 Audience Type: {result['audience_type'].upper().replace('_', ' ')}")
        output.append("\n🎯 Applied Filters:")

        if result["filters"]:
            for key, value in result["filters"].items():
                if not key.startswith("_"):
                    output.append(f"   • {key}: {value}")
        else:
            output.append("   • No additional filters")

        # Show query
        output.append("\n" + "─" * 76)
        output.append("📝 Generated SQL Query:")
        output.append("─" * 76)
        output.append(result["query"])

        # Show count query
        output.append("\n" + "─" * 76)
        output.append("📊 To Get Audience Size:")
        output.append("─" * 76)
        output.append(result["count_query"])

        # Save audience
        audience_name = f"Audience_{len(self.current_audiences) + 1}"
        self.current_audiences.append({
            "name": audience_name,
            "type": result["audience_type"],
            "filters": result["filters"],
            "query": result["query"],
            "count_query": result["count_query"],
            "export_query": result["export_query"]
        })

        output.append(f"\n💾 Saved as: {audience_name}")

        # Next steps
        output.append("""
─────────────────────────────────────────────────────────────────────────────
What would you like to do next?

1) Save queries to file
2) Build another audience
3) Combine this with another audience
4) Return to main menu

💬 Your choice:""")

        self.state = "reviewing"
        return "\n".join(output)

    def _handle_review(self, user_input: str) -> str:
        """Handle post-creation review"""
        choice = user_input.strip().lower()

        if choice in ["1", "save"]:
            return self._save_queries_to_file()
        elif choice in ["2", "build another", "new"]:
            self.state = "main_menu"
            return self._get_main_menu()
        elif choice in ["3", "combine"]:
            if len(self.current_audiences) < 2:
                return """
⚠️  You need at least one more audience to combine.

Let's build another one first!

Type 'menu' to go back."""
            self.state = "combining"
            return self._start_combining_flow()
        elif choice in ["4", "menu", "main menu"]:
            self.state = "main_menu"
            return self._get_main_menu()
        else:
            return "Please choose 1-4, or type 'menu' for main menu."

    def _start_combining_flow(self) -> str:
        """Start the audience combining flow"""
        output = ["""
╔══════════════════════════════════════════════════════════════════════════╗
║                      COMBINE AUDIENCES                                  ║
╚══════════════════════════════════════════════════════════════════════════╝

You can combine audiences using:

🔗 AND (INTERSECT) → Users who are in BOTH audiences
   Example: "Female users" AND "Walmart shoppers" = Female Walmart shoppers

➕ OR (UNION) → Users who are in EITHER audience
   Example: "CA residents" OR "NY residents" = Users from CA or NY

➖ NOT (EXCEPT) → Users in first audience but NOT in second
   Example: "Walmart shoppers" NOT "Low income" = Walmart shoppers excluding low income

─────────────────────────────────────────────────────────────────────────────
Your Saved Audiences:
"""]

        for i, aud in enumerate(self.current_audiences, 1):
            output.append(f"{i}. {aud['name']} ({aud['type']})")
            output.append(f"   Filters: {', '.join([f'{k}={v}' for k, v in aud['filters'].items() if not k.startswith('_')][:3])}")

        output.append("""
─────────────────────────────────────────────────────────────────────────────

Let's combine! Tell me what you want:

💬 Examples:
  • "Combine 1 AND 2"
  • "1 OR 3"
  • "Intersect audience 1 and 2"
  • "1 EXCEPT 2" (users in 1 but not in 2)

Your combination:""")

        return "\n".join(output)

    def _handle_audience_combining(self, user_input: str) -> str:
        """Handle audience combination"""
        import re

        # Parse combination
        input_lower = user_input.lower()

        # Detect operation
        if "and" in input_lower or "intersect" in input_lower:
            operation = "INTERSECT"
        elif "or" in input_lower or "union" in input_lower:
            operation = "UNION"
        elif "not" in input_lower or "except" in input_lower or "exclude" in input_lower:
            operation = "EXCEPT"
        else:
            return """
⚠️  I didn't understand the operation.

Please specify: AND, OR, or NOT

Example: "Combine 1 AND 2"

💬 Try again:"""

        # Extract audience numbers
        numbers = re.findall(r'\b(\d+)\b', user_input)
        if len(numbers) < 2:
            return """
⚠️  Please specify at least 2 audiences to combine.

Example: "1 AND 2"

💬 Try again:"""

        try:
            idx1 = int(numbers[0]) - 1
            idx2 = int(numbers[1]) - 1

            if idx1 < 0 or idx1 >= len(self.current_audiences):
                return f"❌ Audience {numbers[0]} doesn't exist."
            if idx2 < 0 or idx2 >= len(self.current_audiences):
                return f"❌ Audience {numbers[1]} doesn't exist."

            aud1 = self.current_audiences[idx1]
            aud2 = self.current_audiences[idx2]

            # Combine queries
            combined_query = self.query_builder.build_combined_audience(
                [aud1["query"], aud2["query"]],
                operation=operation
            )

            # Create result
            result = {
                "status": "success",
                "query": combined_query,
                "filters": {"combination": f"{aud1['name']} {operation} {aud2['name']}"},
                "audience_type": f"combined_{operation.lower()}",
                "count_query": self.query_builder.get_audience_count(combined_query),
                "export_query": self.query_builder.get_audience_export(combined_query)
            }

            self.state = "reviewing"
            return self._format_success_result(result)

        except Exception as e:
            return f"❌ Error combining audiences: {str(e)}\n\nType 'menu' to start over."

    def _show_saved_audiences(self) -> str:
        """Show all saved audiences"""
        if not self.current_audiences:
            return "\n📋 No saved audiences yet. Let's build one!\n\nType 'menu' to get started."

        output = ["""
╔══════════════════════════════════════════════════════════════════════════╗
║                         SAVED AUDIENCES                                 ║
╚══════════════════════════════════════════════════════════════════════════╝
"""]

        for i, aud in enumerate(self.current_audiences, 1):
            output.append(f"\n{i}. {aud['name']}")
            output.append(f"   Type: {aud['type']}")
            output.append(f"   Filters: {aud['filters']}")
            output.append(f"   Query: {aud['query'][:100]}...")

        return "\n".join(output) + "\n\nType 'menu' to continue."

    def _save_queries_to_file(self) -> str:
        """Save queries to SQL file"""
        if not self.current_audiences:
            return "No audiences to save."

        filename = f"audience_queries_{len(self.current_audiences)}.sql"

        try:
            with open(filename, 'w') as f:
                f.write("-- SKYRISE AUDIENCE QUERIES\n")
                f.write("-- Generated by Skyrise Audience Builder Agent\n\n")

                for i, aud in enumerate(self.current_audiences, 1):
                    f.write(f"-- {i}. {aud['name']}\n")
                    f.write(f"-- Type: {aud['type']}\n")
                    f.write(f"-- Filters: {aud['filters']}\n\n")

                    f.write(f"-- Main Query\n")
                    f.write(aud['query'])
                    f.write("\n\n")

                    f.write(f"-- Count Query\n")
                    f.write(aud['count_query'])
                    f.write("\n\n")

                    f.write("-- " + "="*70 + "\n\n")

            return f"""
✓ Queries saved to: {filename}

Type 'menu' to continue."""

        except Exception as e:
            return f"❌ Error saving file: {str(e)}"

    def _get_examples(self) -> str:
        """Get example prompts"""
        return """
╔══════════════════════════════════════════════════════════════════════════╗
║                          EXAMPLE PROMPTS                                ║
╚══════════════════════════════════════════════════════════════════════════╝

📊 DEMOGRAPHIC TARGETING:
  • "Find all female users aged 25-34 in the US"
  • "Get high income males"
  • "Show me users aged 35-44 with credit cards"

🏪 STORE/BRAND TARGETING:
  • "Find shoppers at Walmart"
  • "Get Starbucks customers with more than 10 transactions"
  • "Show me people who spend over $500 at Amazon"

📍 GEOGRAPHIC TARGETING:
  • "Find all users in California"
  • "Get shoppers in the UK"
  • "Show me customers within 50km of New York"

🛒 CATEGORY TARGETING:
  • "Find grocery store shoppers"
  • "Get users who buy at restaurants"
  • "Show me electronics category customers"

💰 SPENDING BEHAVIOR:
  • "Users who spend more than $1000"
  • "Shoppers with at least 20 transactions"
  • "Find users who spend between $500 and $2000"

🎯 COMBINED FILTERS:
  • "Find high income females aged 35-44 who shop at Tesco in the UK"
  • "Get male coffee shop customers aged 25-34 in California"
  • "Show me high-spending Walmart shoppers in the US"
"""

    def _get_help_message(self) -> str:
        """Get help message"""
        return """
╔══════════════════════════════════════════════════════════════════════════╗
║                            HELP & TIPS                                  ║
╚══════════════════════════════════════════════════════════════════════════╝

🎯 AUDIENCE TYPES:

1. Demographic → Filter by personal characteristics
   Filters: Gender, Age band, Income, Card type, Country

2. Store/Brand → Target customers of specific stores
   Filters: Store name, Min transactions, Min spend, Date range

3. Shopping Category → Target by merchant type
   Filters: Category (grocery, restaurants, etc.), MCC codes

4. Geographic → Filter by location
   Filters: Country, State, City, Radius from coordinates

5. Spending Behavior → Filter by spending patterns
   Filters: Min/max spend, Transaction count

6. Grocer → Specialized for grocery stores
   Filters: Grocer name (Walmart, Tesco, etc.)

─────────────────────────────────────────────────────────────────────────────

💡 TIPS:

• Be specific: "Walmart shoppers" is better than "shoppers"
• Use numbers: "aged 25-34" or "spend over $1000"
• Combine filters: "high income females in California"
• Use AND/OR/NOT to combine audiences
• Type 'examples' to see what I can do

─────────────────────────────────────────────────────────────────────────────

📚 AVAILABLE FILTERS:

Gender: Male, Female, Other
Age Bands: 18-24, 25-34, 35-44, 45-54, 55-64, 65+
Income: Low, Medium, High, Very High
Countries: US, GB, CA, AU, DE, FR, ES, IT
Card Types: Credit, Debit, Prepaid

─────────────────────────────────────────────────────────────────────────────

⌨️ COMMANDS:

menu     → Return to main menu
examples → Show example prompts
help     → Show this help message
list     → Show saved audiences
quit     → Exit the agent
"""

    def _get_goodbye_message(self) -> str:
        """Get goodbye message"""
        return """
╔══════════════════════════════════════════════════════════════════════════╗
║                          THANK YOU!                                     ║
╚══════════════════════════════════════════════════════════════════════════╝

Thank you for using Skyrise Audience Builder Agent!

📊 Session Summary:
  • Audiences created: {count}
  • Queries generated: {count}

Your audiences have been saved and can be executed in BigQuery.

👋 See you next time!
""".format(count=len(self.current_audiences))


def main():
    """Run the conversational agent"""
    import sys

    print("=" * 78)
    print(" " * 20 + "INITIALIZING AGENT...")
    print("=" * 78)

    # Get configuration
    project_id = input("\nBigQuery Project ID [default: your-project-id]: ").strip()
    if not project_id:
        project_id = "your-project-id"

    dataset = input("Dataset name [default: skyrise]: ").strip()
    if not dataset:
        dataset = "skyrise"

    release_id = input("Release ID [default: 1]: ").strip()
    if not release_id:
        release_id = 1
    else:
        release_id = int(release_id)

    # Initialize agent
    agent = ConversationalAgent(project_id, dataset, release_id)

    # Start conversation
    print(agent.start())
    input()  # Wait for user to press enter

    # Main loop
    while True:
        try:
            response = agent.process_input("")
            print("\n" + response)

            user_input = input("\n💬 You: ").strip()

            if user_input.lower() in ["quit", "exit", "bye"]:
                print(agent._get_goodbye_message())
                break

            if not user_input:
                continue

            response = agent.process_input(user_input)
            print("\n" + response)

        except KeyboardInterrupt:
            print("\n\n" + agent._get_goodbye_message())
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Type 'menu' to go back to main menu.")


if __name__ == "__main__":
    main()

"""
Interactive CLI for Skyrise Audience Agent
Provides an interactive command-line interface for audience generation
"""

import sys
from typing import Dict, Any, List
from audience_agent import AudienceAgent


class InteractiveCLI:
    """Interactive command-line interface for audience generation"""

    def __init__(self):
        self.agent = None
        self.current_questions = []
        self.current_audience_info = {}

    def start(self):
        """Start the interactive CLI"""
        print("=" * 80)
        print(" " * 20 + "SKYRISE AUDIENCE GENERATION AGENT")
        print("=" * 80)
        print("\nWelcome! I'll help you create audiences from your Skyrise data.")
        print("Type 'exit' or 'quit' to end the session.\n")

        # Get configuration
        self._configure_agent()

        # Main interaction loop
        while True:
            try:
                user_input = input("\n💬 Describe your audience: ").strip()

                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Thank you for using Skyrise Audience Agent!")
                    break

                if not user_input:
                    continue

                self._process_user_input(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")

    def _configure_agent(self):
        """Configure the agent with user settings"""
        print("\n⚙️  Configuration")
        print("-" * 80)

        project_id = input("Enter your BigQuery project ID [default: your-project-id]: ").strip()
        if not project_id:
            project_id = "your-project-id"

        dataset = input("Enter your dataset name [default: skyrise]: ").strip()
        if not dataset:
            dataset = "skyrise"

        release_id = input("Enter release ID [default: 1]: ").strip()
        if not release_id:
            release_id = 1
        else:
            release_id = int(release_id)

        self.agent = AudienceAgent(
            project_id=project_id,
            dataset=dataset,
            release_id=release_id
        )

        print(f"\n✓ Agent configured with project: {project_id}, dataset: {dataset}, release: {release_id}")

    def _process_user_input(self, user_input: str):
        """Process user input and generate response"""
        result = self.agent.process_prompt(user_input)

        if result["status"] == "needs_clarification":
            self._handle_clarification(result)

        elif result["status"] == "success":
            self._display_success(result)

        else:  # error
            print(f"\n❌ {result['message']}")

    def _handle_clarification(self, result: Dict[str, Any]):
        """Handle clarification questions"""
        print(f"\n{result['message']}")
        print("-" * 80)

        self.current_questions = result["questions"]
        answers = {}

        for i, question in enumerate(self.current_questions, 1):
            answer = self._ask_question(i, question)
            if answer is not None:
                answers[question["key"]] = answer

        # Apply answers and regenerate query
        if answers:
            # Merge answers with existing filters
            updated_info = result.copy()
            updated_info["filters"].update(answers)

            # Build query with updated filters
            try:
                query = self.agent._build_query_from_info(updated_info)
                final_result = {
                    "status": "success",
                    "message": "Audience query generated successfully!",
                    "query": query,
                    "audience_type": updated_info["audience_type"],
                    "filters": updated_info["filters"],
                    "count_query": self.agent.query_builder.get_audience_count(query),
                    "export_query": self.agent.query_builder.get_audience_export(query)
                }
                self._display_success(final_result)
            except Exception as e:
                print(f"\n❌ Error generating query: {str(e)}")

    def _ask_question(self, number: int, question: Dict[str, Any]) -> Any:
        """Ask a single clarification question"""
        print(f"\n{number}. {question['question']}")

        if question["type"] == "text":
            answer = input("   Your answer: ").strip()
            return answer if answer else None

        elif question["type"] == "choice":
            print(f"   Options: {', '.join(question['options'])}")
            answer = input("   Your choice: ").strip()
            return answer if answer else None

        elif question["type"] == "choice_optional":
            print(f"   Options: {', '.join(question['options'])} (or press Enter to skip)")
            answer = input("   Your choice: ").strip()
            return answer if answer else None

        elif question["type"] == "choice_optional_multiple":
            print(f"   Options: {', '.join(question['options'])}")
            print("   Enter multiple values separated by commas (or press Enter to skip)")
            answer = input("   Your choices: ").strip()
            if answer:
                return [x.strip() for x in answer.split(",")]
            return None

        return None

    def _display_success(self, result: Dict[str, Any]):
        """Display successful query generation"""
        print("\n" + "=" * 80)
        print("✓ AUDIENCE GENERATED SUCCESSFULLY")
        print("=" * 80)

        print(f"\n📊 Audience Type: {result['audience_type'].upper()}")

        print(f"\n🎯 Applied Filters:")
        if result["filters"]:
            for key, value in result["filters"].items():
                print(f"   • {key}: {value}")
        else:
            print("   • No filters applied")

        print("\n" + "-" * 80)
        print("📝 AUDIENCE QUERY")
        print("-" * 80)
        print(result["query"])

        print("\n" + "-" * 80)
        print("📊 COUNT QUERY (to get audience size)")
        print("-" * 80)
        print(result["count_query"])

        print("\n" + "-" * 80)
        print("📋 EXPORT QUERY (with demographics)")
        print("-" * 80)
        print(result["export_query"])

        print("\n" + "=" * 80)

        # Ask if user wants to save
        save = input("\n💾 Would you like to save these queries to a file? (y/n): ").strip().lower()
        if save == 'y':
            self._save_queries(result)

    def _save_queries(self, result: Dict[str, Any]):
        """Save queries to a file"""
        filename = input("Enter filename [default: audience_queries.sql]: ").strip()
        if not filename:
            filename = "audience_queries.sql"

        if not filename.endswith('.sql'):
            filename += '.sql'

        try:
            with open(filename, 'w') as f:
                f.write("-- SKYRISE AUDIENCE QUERY\n")
                f.write(f"-- Type: {result['audience_type']}\n")
                f.write(f"-- Filters: {result['filters']}\n\n")

                f.write("-- Main Query\n")
                f.write(result["query"])
                f.write("\n\n")

                f.write("-- Count Query\n")
                f.write(result["count_query"])
                f.write("\n\n")

                f.write("-- Export Query (with demographics)\n")
                f.write(result["export_query"])
                f.write("\n")

            print(f"\n✓ Queries saved to: {filename}")

        except Exception as e:
            print(f"\n❌ Error saving file: {str(e)}")


def main():
    """Main entry point"""
    cli = InteractiveCLI()
    cli.start()


if __name__ == "__main__":
    main()

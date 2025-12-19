#!/usr/bin/env python3
"""
Skyrise Conversational Audience Builder - Main Runner
Run this file to start the interactive conversational agent
"""

import sys
import os
from conversational_agent import ConversationalAgent


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Main entry point for the conversational agent"""

    # Welcome screen
    clear_screen()
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║              SKYRISE AUDIENCE BUILDER - CONVERSATIONAL AGENT            ║
║                                                                          ║
║              Your AI-Powered Audience Creation Assistant                ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

Welcome! Let's get you set up...

""")

    # Configuration
    print("━" * 76)
    print("                        CONFIGURATION")
    print("━" * 76)

    project_id = input("\n📦 BigQuery Project ID [your-project-id]: ").strip()
    if not project_id:
        project_id = "your-project-id"

    dataset = input("📊 Dataset name [skyrise]: ").strip()
    if not dataset:
        dataset = "skyrise"

    release_input = input("🔢 Release ID [1]: ").strip()
    if not release_input:
        release_id = 1
    else:
        try:
            release_id = int(release_input)
        except:
            print("⚠️  Invalid release ID, using default: 1")
            release_id = 1

    # Ask about query execution
    print("\n" + "━" * 76)
    print("                     BIGQUERY EXECUTION")
    print("━" * 76)
    print("\nDo you want to EXECUTE queries in BigQuery and see REAL results?")
    print("(This requires valid BigQuery credentials)")
    print("\nOptions:")
    print("  1) Yes - Execute queries and show real audience counts/data")
    print("  2) No - Just generate SQL queries (no execution)")

    exec_choice = input("\n💬 Your choice [1]: ").strip()
    execute_queries = exec_choice != "2"

    credentials_path = None
    if execute_queries:
        creds_input = input("\n🔑 Path to service account JSON (or press Enter to use default credentials): ").strip()
        if creds_input:
            credentials_path = creds_input

    print(f"""
✓ Configuration saved:
  Project: {project_id}
  Dataset: {dataset}
  Release: {release_id}
  Execute Queries: {'Yes' if execute_queries else 'No'}
  Credentials: {credentials_path if credentials_path else 'Default'}
""")

    input("Press Enter to start the agent...")
    clear_screen()

    # Initialize agent
    try:
        agent = ConversationalAgent(
            project_id=project_id,
            dataset=dataset,
            release_id=release_id,
            execute_queries=execute_queries,
            credentials_path=credentials_path
        )
    except Exception as e:
        print(f"❌ Error initializing agent: {str(e)}")
        sys.exit(1)

    # Show welcome message
    print(agent.start())
    input()

    # Show main menu
    response = agent.process_input("")
    print("\n" + response)

    # Main conversation loop
    while True:
        try:
            user_input = input("\n💬 You: ").strip()

            # Handle empty input
            if not user_input:
                continue

            # Handle exit
            if user_input.lower() in ["quit", "exit", "bye", "q"]:
                print("\n" + agent._get_goodbye_message())
                break

            # Handle clear screen
            if user_input.lower() in ["clear", "cls"]:
                clear_screen()
                print(agent._get_main_menu())
                continue

            # Process input
            response = agent.process_input(user_input)
            print("\n" + response)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            print(agent._get_goodbye_message())
            break

        except Exception as e:
            print(f"\n❌ Oops! Something went wrong: {str(e)}")
            print("\n💡 Tip: Type 'menu' to go back to the main menu")
            print("        Type 'help' for assistance")
            print("        Type 'quit' to exit")

    print("\n" + "=" * 76)
    print("Thank you for using Skyrise Audience Builder!")
    print("=" * 76 + "\n")


if __name__ == "__main__":
    main()

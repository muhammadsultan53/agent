# Skyrise Audience Agent - Quick Start Guide

## What is this?

The Skyrise Audience Agent is an intelligent tool that converts natural language into SQL queries for audience creation. Just describe who you want to target, and the agent generates the BigQuery SQL for you!

## Installation

```bash
cd skyrise_audience_agent
pip install -r requirements.txt
```

## Quick Start

### Method 1: Conversational Agent (★ Recommended for Beginners)

```bash
python run_agent.py
```

The agent will:
- 🎯 Guide you step-by-step through building audiences
- 💡 Explain what filters are available
- 📚 Show examples and provide help
- 🔗 Let you combine audiences with AND/OR/NOT
- 💾 Save your queries to files

**Perfect for: Learning, exploring, and complex combinations**

### Method 2: Quick CLI (For Experienced Users)

```bash
python interactive_cli.py
```

The agent will ask you:
1. Your BigQuery project ID
2. Dataset name
3. Release ID

Then you can type natural language prompts like:

```
💬 Describe your audience: Find female users aged 25-34 in the US with high income
```

**Perfect for: Quick builds when you know exactly what you want**

The agent will generate SQL queries for you!

### Programmatic Usage

```python
from skyrise_audience_agent import AudienceAgent

# Initialize
agent = AudienceAgent(
    project_id="your-project-id",
    dataset="skyrise",
    release_id=1
)

# Generate audience
result = agent.process_prompt(
    "Find all female shoppers aged 25-34 who shop at Walmart in the US"
)

if result["status"] == "success":
    # Use the query
    sql_query = result["query"]
    count_query = result["count_query"]
    export_query = result["export_query"]
```

## What Can You Ask?

### Demographic Audiences
- "Find all female users aged 25-34 in the US"
- "Get high income males"
- "Show me users with credit cards"

### Store/Brand Targeting
- "Find shoppers at Walmart"
- "Get Starbucks customers with more than 10 transactions"
- "Show me people who spend over $500 at Amazon"

### Geographic Targeting
- "Find all users in California"
- "Get shoppers in the UK"
- "Show me customers within 50km of New York"

### Shopping Categories
- "Find grocery store shoppers"
- "Get users who buy at restaurants"
- "Show me electronics category customers"

### Spending Behavior
- "Users who spend more than $1000"
- "Shoppers with at least 20 transactions"
- "High-spending frequent customers"

### Combined Filters
- "Find high income females aged 35-44 who shop at Tesco in the UK"
- "Get male coffee shop customers aged 25-34 in California"

## Available Filters

### Demographics
- **Gender**: Male, Female, Other, Unknown
- **Age Bands**: 18-24, 25-34, 35-44, 45-54, 55-64, 65+
- **Income**: Low, Medium-Low, Medium, Medium-High, High, Very High
- **Card Type**: Credit, Debit, Prepaid

### Geographic
- **Countries**: US, GB, CA, AU, DE, FR, ES, IT
- **Regions**: State/province level
- **Radius**: Within X km of coordinates

### Behavioral
- **Minimum spend amount**
- **Transaction count**
- **Date ranges**
- **Specific vendors/stores**
- **Merchant categories**

## Output

The agent generates three queries:

1. **Main Query**: Returns user_ids matching your criteria
2. **Count Query**: Returns the size of your audience
3. **Export Query**: Returns user_ids WITH demographic details

## Next Steps

1. **Configure**: Update `schema_config.py` with your BigQuery project details
2. **Customize**: Add your specific vendors/merchants to the configuration
3. **Extend**: Use the QueryBuilder class for advanced query combinations

## Documentation

See `README.md` for complete documentation and advanced features.

## Examples

See `examples.py` for 10+ detailed examples covering all use cases.

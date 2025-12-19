# Skyrise Audience Generation Agent

An intelligent agent that converts natural language prompts into SQL queries for audience creation from Skyrise transaction data.

## Features

✨ **Natural Language Processing**: Describe your audience in plain English
🤖 **Interactive Clarification**: Agent asks follow-up questions for missing filters
🎯 **Multiple Audience Types**: Support for demographic, behavioral, geographic, and lookalike audiences
📊 **Smart Query Generation**: Automatically generates optimized BigQuery SQL
🔍 **Filter Validation**: Ensures all filters match valid schema values
💾 **Export Ready**: Generates queries for counting and exporting audiences with demographics

## Supported Audience Types

### 1. **Demographic Audiences**
Filter users by demographic attributes
- Gender (Male, Female, Other, Unknown)
- Age bands (18-24, 25-34, 35-44, 45-54, 55-64, 65+)
- Income bands (Low, Medium, High, etc.)
- Card type (Credit, Debit, Prepaid)
- User type (Active, Regular, Occasional, Inactive)
- Country

### 2. **Vendor/Merchant Audiences**
Target users who shop at specific stores or brands
- Find customers of specific vendors
- Filter by transaction frequency
- Filter by total spend
- Date range filtering

### 3. **Merchant Category Audiences**
Target users by shopping categories
- Grocery stores, Restaurants, Gas stations, etc.
- Support for MCC (Merchant Category Codes)
- Transaction count filtering

### 4. **Geographic Audiences**
Target users by location
- Country, State/Region (L1), County (L2), City (L3)
- Radius-based targeting (within X km of a location)
- Coordinate-based filtering

### 5. **Grocer Audiences**
Specialized targeting for grocery store shoppers
- Support for major chains (Walmart, Tesco, Kroger, etc.)
- Transaction frequency filtering

### 6. **Spending Behavior Audiences**
Target users by spending patterns
- Minimum/maximum spend thresholds
- Transaction count filters
- Date range filtering

### 7. **Lookalike Audiences**
Find users similar to those in a merchant category

## Installation

```bash
# Clone or download the repository
cd skyrise_audience_agent

# Install dependencies
pip install -r requirements.txt

# Configure your BigQuery credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
```

## Quick Start

### Interactive CLI Mode

```bash
python interactive_cli.py
```

The agent will guide you through:
1. Configuration (BigQuery project, dataset, release ID)
2. Natural language audience description
3. Clarifying questions for missing filters
4. Query generation and export

### Programmatic Usage

```python
from audience_agent import AudienceAgent

# Initialize the agent
agent = AudienceAgent(
    project_id="your-project-id",
    dataset="skyrise",
    release_id=1
)

# Generate audience from natural language
result = agent.process_prompt(
    "Find all female shoppers aged 25-34 who shop at Walmart in the US"
)

# Check if clarification is needed
if result["status"] == "needs_clarification":
    print(result["message"])
    for question in result["questions"]:
        print(question["question"])
        # Collect answers and reprocess

# Use the generated query
elif result["status"] == "success":
    main_query = result["query"]
    count_query = result["count_query"]
    export_query = result["export_query"]

    # Execute with BigQuery client
    from google.cloud import bigquery
    client = bigquery.Client()

    # Get audience size
    count_result = client.query(count_query).result()
    print(f"Audience size: {list(count_result)[0][0]}")

    # Export audience
    export_result = client.query(export_query).result()
    for row in export_result:
        print(row)
```

## Example Prompts

### Basic Demographic Targeting
```
"Find all female users aged 25-34 in the US"
"Get high income males"
"Show me users with credit cards"
```

### Vendor/Store Targeting
```
"Find all shoppers at Walmart"
"Get customers who shop at Starbucks with more than 10 transactions"
"Show me people who spend over $500 at Amazon"
```

### Geographic Targeting
```
"Find all users in California"
"Get shoppers within 50km of New York"
"Show me customers in the UK"
```

### Category Targeting
```
"Find all grocery store shoppers"
"Get users who buy at restaurants"
"Show me customers in the electronics category"
```

### Combined Filtering
```
"Find female shoppers aged 25-34 who shop at Tesco in the UK"
"Get high income males who spend more than $1000 at coffee shops"
"Show me users in California aged 35-44 who shop at grocery stores"
```

### Grocer-Specific
```
"Find all Walmart shoppers in the US"
"Get Tesco customers who shop weekly"
"Show me Whole Foods shoppers with high income"
```

## Query Builder API

For advanced users, use the `QueryBuilder` class directly:

```python
from query_builder import QueryBuilder

qb = QueryBuilder(
    project_id="your-project-id",
    dataset="skyrise",
    release_id=1
)

# Build demographic audience
query = qb.build_demographic_audience({
    "gender_description": ["Female"],
    "age_band": ["25-34", "35-44"],
    "user_ccode2": ["US"]
})

# Build vendor audience
query = qb.build_vendor_audience({
    "vendor_desc": "Walmart",
    "min_transactions": 5,
    "min_spend": 100
})

# Build geographic audience
query = qb.build_geographic_audience({
    "user_ccode2": ["US"],
    "user_l1_geo": ["CA", "NY"]
})

# Combine audiences with INTERSECT
query1 = qb.build_demographic_audience({"gender_description": ["Female"]})
query2 = qb.build_vendor_audience({"vendor_desc": "Walmart"})
combined = qb.build_combined_audience([query1, query2], operation="INTERSECT")

# Add demographic refinement to any query
base_query = qb.build_vendor_audience({"vendor_desc": "Starbucks"})
refined = qb.add_demographic_refinement(base_query, {
    "age_band": ["25-34"],
    "income_band": ["High"]
})

# Get count and export queries
count_query = qb.get_audience_count(query)
export_query = qb.get_audience_export(query, include_demographics=True)
```

## Configuration

### Schema Configuration (`schema_config.py`)

Update the following in `schema_config.py`:

```python
SCHEMA = {
    "project_id": "your-bigquery-project",
    "dataset": "your-dataset-name",
}

DEFAULT_RELEASE_ID = 1  # Your current release ID
```

### Valid Filter Values

The agent validates all filters against predefined values in `schema_config.py`. Modify these to match your data:

- `VALID_FILTERS`: Valid values for demographic filters
- `COMMON_MERCHANTS`: Common merchant categories in your data
- `COMMON_GROCERS`: Grocery chains to recognize

## Architecture

```
skyrise_audience_agent/
├── __init__.py              # Package initialization
├── schema_config.py         # Schema and filter definitions
├── query_builder.py         # SQL query generation
├── audience_agent.py        # Natural language processing and orchestration
├── interactive_cli.py       # Interactive command-line interface
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Component Roles

1. **schema_config.py**: Contains all schema definitions, valid filter values, table names, and query templates
2. **query_builder.py**: Generates SQL queries for different audience types with proper filtering
3. **audience_agent.py**: Parses natural language, extracts filters, asks clarifying questions, and orchestrates query generation
4. **interactive_cli.py**: Provides user-friendly command-line interface

## Advanced Features

### Combining Multiple Audiences

```python
# Find users who are BOTH female AND shop at Walmart
demographic_query = qb.build_demographic_audience({"gender_description": ["Female"]})
vendor_query = qb.build_vendor_audience({"vendor_desc": "Walmart"})
intersect_query = qb.build_combined_audience([demographic_query, vendor_query], "INTERSECT")

# Find users who are EITHER in CA OR in NY
ca_query = qb.build_geographic_audience({"user_l1_geo": ["CA"]})
ny_query = qb.build_geographic_audience({"user_l1_geo": ["NY"]})
union_query = qb.build_combined_audience([ca_query, ny_query], "UNION")

# Find Walmart shoppers who are NOT in California
walmart_query = qb.build_vendor_audience({"vendor_desc": "Walmart"})
ca_query = qb.build_geographic_audience({"user_l1_geo": ["CA"]})
except_query = qb.build_combined_audience([walmart_query, ca_query], "EXCEPT")
```

### Radius-Based Targeting

```python
# Find users within 25km of a specific location
query = qb.build_geographic_audience({
    "center_lat": 37.7749,    # San Francisco
    "center_lon": -122.4194,
    "radius_km": 25
})
```

### Spending Behavior Analysis

```python
# Find high-spending, frequent shoppers
query = qb.build_spending_behavior_audience({
    "min_total_spend": 5000,
    "min_transactions": 50
})
```

### Lookalike Audiences

```python
# Find users similar to those in a specific merchant category
query = qb.build_lookalike_audience({
    "merch_id": [123, 456],  # Merchant category IDs
    "user_ccode2": ["US"]
})
```

## Example Interaction

```
================================================================================
                    SKYRISE AUDIENCE GENERATION AGENT
================================================================================

Welcome! I'll help you create audiences from your Skyrise data.
Type 'exit' or 'quit' to end the session.

⚙️  Configuration
--------------------------------------------------------------------------------
Enter your BigQuery project ID [default: your-project-id]: my-project
Enter your dataset name [default: skyrise]: skyrise_prod
Enter release ID [default: 1]: 5

✓ Agent configured with project: my-project, dataset: skyrise_prod, release: 5

💬 Describe your audience: Find female shoppers aged 25-34 who shop at Walmart

I need some additional information to build your audience:
--------------------------------------------------------------------------------

1. Which country would you like to target?
   Options: US, GB, CA, AU, DE, FR, ES, IT
   Your choice: US

2. Would you like to filter by income band?
   Options: Low, Medium-Low, Medium, Medium-High, High, Very High (or press Enter to skip)
   Your choice: High

================================================================================
✓ AUDIENCE GENERATED SUCCESSFULLY
================================================================================

📊 Audience Type: VENDOR

🎯 Applied Filters:
   • vendor_desc: Walmart
   • gender_description: ['Female']
   • age_band: ['25-34']
   • user_ccode2: ['US']
   • income_band: ['High']

--------------------------------------------------------------------------------
📝 AUDIENCE QUERY
--------------------------------------------------------------------------------
SELECT DISTINCT uvs.user_id
FROM `my-project.skyrise_prod.skyrise_user_vendor_stats` uvs
JOIN `my-project.skyrise_prod.skyrise_vendors` v
    ON uvs.vendor_id = v.vendor_id
    AND uvs.tx_release_id = v.tx_release_id
WHERE uvs.tx_release_id = 5
AND LOWER(v.vendor_desc) LIKE '%walmart%'

[Additional queries displayed...]

💾 Would you like to save these queries to a file? (y/n): y
Enter filename [default: audience_queries.sql]: walmart_female_25_34.sql

✓ Queries saved to: walmart_female_25_34.sql
```

## Troubleshooting

### Issue: Agent doesn't recognize vendor/merchant names

**Solution**: Add the vendor/merchant to `COMMON_GROCERS` or `COMMON_MERCHANTS` in `schema_config.py`

### Issue: Invalid filter values

**Solution**: Check `VALID_FILTERS` in `schema_config.py` and ensure your data matches these values

### Issue: BigQuery authentication errors

**Solution**: Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable or configure ADC:
```bash
gcloud auth application-default login
```

### Issue: Queries returning no results

**Solution**:
1. Verify the `tx_release_id` is correct
2. Check that filter values match your actual data
3. Run simpler queries first to validate data availability

## Extending the Agent

### Adding New Audience Types

1. Add query template to `AUDIENCE_TEMPLATES` in `schema_config.py`
2. Add build method to `QueryBuilder` class in `query_builder.py`
3. Update `_parse_prompt()` in `audience_agent.py` to detect new type
4. Add clarifying questions in `_get_clarifying_questions()`

### Adding New Filters

1. Add valid values to `VALID_FILTERS` in `schema_config.py`
2. Update relevant build methods in `query_builder.py`
3. Update extraction methods in `audience_agent.py`

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing patterns
- New features include documentation
- Filter values are validated against schema

## License

[Your License Here]

## Support

For issues or questions:
- Check the Troubleshooting section
- Review example prompts
- Examine the generated SQL queries for correctness

## Roadmap

- [ ] Integration with BigQuery for direct query execution
- [ ] Audience size estimation before query execution
- [ ] Support for temporal patterns (day/hour analysis)
- [ ] Audience comparison and overlap analysis
- [ ] Export to CSV/JSON formats
- [ ] Web UI interface
- [ ] Support for custom SQL injection for advanced users
- [ ] Caching for common queries
- [ ] Audience scheduling and automation

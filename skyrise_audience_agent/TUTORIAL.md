# Skyrise Audience Builder - Complete Tutorial

## Table of Contents
1. [Getting Started](#getting-started)
2. [Understanding Audiences](#understanding-audiences)
3. [Building Your First Audience](#building-your-first-audience)
4. [Combining Audiences](#combining-audiences)
5. [Advanced Examples](#advanced-examples)
6. [Best Practices](#best-practices)

---

## Getting Started

### Installation

```bash
cd skyrise_audience_agent
pip install -r requirements.txt
```

### Running the Agent

**Conversational Mode (Recommended for beginners)**:
```bash
python run_agent.py
```

**Quick CLI Mode**:
```bash
python interactive_cli.py
```

**Programmatic Mode** (for developers):
```python
from conversational_agent import ConversationalAgent

agent = ConversationalAgent(
    project_id="your-project",
    dataset="skyrise",
    release_id=1
)
```

---

## Understanding Audiences

### What is an Audience?

An audience is a group of users from your Skyrise data who match specific criteria. For example:
- All female users aged 25-34
- Customers who shop at Walmart
- High-income users in California

### Audience Types

The agent supports 6 main audience types:

#### 1. **Demographic Audiences**
Filter users by personal characteristics.

**Available Filters:**
- Gender: Male, Female, Other, Unknown
- Age Band: 18-24, 25-34, 35-44, 45-54, 55-64, 65+
- Income Band: Low, Medium-Low, Medium, Medium-High, High, Very High
- Country: US, GB, CA, AU, DE, FR, ES, IT
- Card Type: Credit, Debit, Prepaid
- User Type: Active, Regular, Occasional, Inactive

**Examples:**
```
"Find all female users aged 25-34 in the US"
"Get high income males"
"Show me users with credit cards aged 35-44"
```

#### 2. **Store/Brand Audiences**
Target customers who shop at specific stores or brands.

**Available Filters:**
- Store/vendor name
- Minimum number of transactions
- Minimum spend amount
- Date ranges

**Examples:**
```
"Find shoppers at Walmart"
"Get Starbucks customers with more than 10 transactions"
"Show me people who spend over $500 at Amazon"
```

#### 3. **Shopping Category Audiences**
Target users by merchant categories (what type of stores they visit).

**Available Filters:**
- Merchant category (Grocery, Restaurants, Gas Stations, etc.)
- MCC (Merchant Category Code)
- Transaction thresholds

**Examples:**
```
"Find grocery store shoppers"
"Get users who buy at restaurants"
"Show me electronics category customers"
```

#### 4. **Geographic Audiences**
Filter users by location.

**Available Filters:**
- Country (US, GB, CA, AU, DE, FR, ES, IT)
- State/Region (e.g., CA, NY, TX)
- City
- Radius from coordinates (within X km of a location)

**Examples:**
```
"Find all users in California"
"Get shoppers in the UK"
"Show me customers within 50km of New York"
```

#### 5. **Spending Behavior Audiences**
Target users based on their spending patterns.

**Available Filters:**
- Minimum/maximum spend amount
- Transaction count
- Spending frequency
- Date ranges

**Examples:**
```
"Users who spend more than $1000"
"Shoppers with at least 20 transactions"
"Find users who spend between $500 and $2000"
```

#### 6. **Grocer Audiences**
Specialized for grocery store targeting (uses enhanced grocer matching).

**Supported Grocers:**
- Walmart
- Tesco
- Sainsbury's
- Kroger
- Whole Foods
- Aldi
- Lidl

**Examples:**
```
"Find Walmart shoppers"
"Get Tesco customers in the UK"
"Show me Whole Foods shoppers with high income"
```

---

## Building Your First Audience

### Step-by-Step Guide

#### Method 1: Guided Build

1. Start the agent:
   ```bash
   python run_agent.py
   ```

2. Choose option **1** (Build a New Audience)

3. Select your audience type (1-6)

4. Answer the questions the agent asks

5. Review your generated SQL query

#### Method 2: Natural Language

1. Start the agent

2. Choose option **2** (Quick Build)

3. Describe your audience in plain English:
   ```
   "Find female users aged 25-34 in the US with high income"
   ```

4. The agent will:
   - Parse your request
   - Ask clarifying questions if needed
   - Generate the SQL query

### Example Session

```
💬 You: Find female users aged 25-34 in the US

🤖 Agent:
✓ AUDIENCE CREATED SUCCESSFULLY!

📊 Audience Type: DEMOGRAPHIC

🎯 Applied Filters:
   • gender_description: ['Female']
   • age_band: ['25-34']
   • user_ccode2: ['US']

📝 Generated SQL Query:
────────────────────────────────────────
SELECT DISTINCT u.user_id
FROM `your-project.skyrise.skyrise_user_profile` u
WHERE u.tx_release_id = 1
AND u.gender_description IN ('Female')
AND u.age_band IN ('25-34')
AND u.user_ccode2 IN ('US')
```

---

## Combining Audiences

### Why Combine Audiences?

Combining audiences lets you create complex targeting:

- **AND (INTERSECT)** → Users in BOTH audiences
- **OR (UNION)** → Users in EITHER audience
- **NOT (EXCEPT)** → Users in first audience but NOT in second

### Examples

#### Example 1: Female Walmart Shoppers

**Step 1:** Build two audiences
```
Audience 1: "Find all female users"
Audience 2: "Find Walmart shoppers"
```

**Step 2:** Combine them
```
💬 You: Combine 1 AND 2
```

**Result:** Female users who shop at Walmart

#### Example 2: Multi-State Targeting

**Step 1:** Build audiences
```
Audience 1: "Users in California"
Audience 2: "Users in New York"
```

**Step 2:** Combine
```
💬 You: 1 OR 2
```

**Result:** Users from California OR New York

#### Example 3: Exclusion

**Step 1:** Build audiences
```
Audience 1: "Walmart shoppers"
Audience 2: "Low income users"
```

**Step 2:** Exclude
```
💬 You: 1 EXCEPT 2
```

**Result:** Walmart shoppers who are NOT low income

### Complex Combinations

You can chain multiple combinations:

```python
# Programmatic API for complex logic
from query_builder import QueryBuilder

qb = QueryBuilder(project_id="...", dataset="...", release_id=1)

# (Female OR Male aged 25-34) AND (Walmart shoppers) NOT (Low income)
female = qb.build_demographic_audience({"gender_description": ["Female"]})
male_young = qb.build_demographic_audience({
    "gender_description": ["Male"],
    "age_band": ["25-34"]
})
walmart = qb.build_vendor_audience({"vendor_desc": "Walmart"})
low_income = qb.build_demographic_audience({"income_band": ["Low"]})

# Combine step by step
gender_or_age = qb.build_combined_audience([female, male_young], "UNION")
walmart_targeted = qb.build_combined_audience([gender_or_age, walmart], "INTERSECT")
final = qb.build_combined_audience([walmart_targeted, low_income], "EXCEPT")
```

---

## Advanced Examples

### Example 1: High-Value Customer Segmentation

**Goal:** Find high-income, frequent Starbucks customers in major cities

```python
# Natural language approach
💬 You: Find high income users who shop at Starbucks with more than 20 transactions
```

```python
# Programmatic approach
from audience_agent import AudienceAgent

agent = AudienceAgent(project_id="...", dataset="...", release_id=1)

result = agent.process_prompt(
    "Find high income users who shop at Starbucks with more than 20 transactions"
)

# Add geographic refinement
if result["status"] == "success":
    base_query = result["query"]
    refined = agent.query_builder.add_demographic_refinement(
        base_query,
        {"user_l1_geo": ["CA", "NY", "IL"]}  # California, New York, Illinois
    )
```

### Example 2: Grocer Competitive Analysis

**Goal:** Compare customer demographics across grocery chains

```python
# Build audiences for each grocer
walmart = agent.process_prompt("Find Walmart shoppers")
tesco = agent.process_prompt("Find Tesco shoppers")
whole_foods = agent.process_prompt("Find Whole Foods shoppers")

# Export each with demographics
walmart_export = agent.query_builder.get_audience_export(
    walmart["query"],
    include_demographics=True
)

# Execute in BigQuery to compare age, income, gender distributions
```

### Example 3: Geographic Radius Targeting

**Goal:** Target users within 25km of a store location

```python
from query_builder import QueryBuilder

qb = QueryBuilder(project_id="...", dataset="...", release_id=1)

# San Francisco coordinates
query = qb.build_geographic_audience({
    "center_lat": 37.7749,
    "center_lon": -122.4194,
    "radius_km": 25,
    "user_ccode2": ["US"]
})

# Combine with demographics
refined = qb.add_demographic_refinement(query, {
    "age_band": ["25-34", "35-44"],
    "income_band": ["High", "Very High"]
})
```

### Example 4: Lookalike Audience

**Goal:** Find users similar to existing high-value customers

```python
# Build base audience of high-value customers
high_value = qb.build_spending_behavior_audience({
    "min_total_spend": 5000,
    "min_transactions": 50
})

# Get merchant categories they shop at
# (requires joining with transaction data)
# Then use lookalike_merch_users table to find similar users

lookalike = qb.build_lookalike_audience({
    "merch_id": [10, 25, 30],  # Merchant IDs from analysis
    "user_ccode2": ["US"]
})
```

---

## Best Practices

### 1. Start Simple, Then Refine

Build a broad audience first, then narrow it down:

```
Step 1: "Find Walmart shoppers"          → 1M users
Step 2: Add "in California"              → 100K users
Step 3: Add "aged 25-44"                 → 30K users
Step 4: Add "high income"                → 10K users
```

### 2. Use Appropriate Audience Types

- **Demographics** → When you know user characteristics
- **Vendor** → When targeting brand loyalists
- **Geographic** → For location-based campaigns
- **Spending** → For value-based segmentation

### 3. Test Audience Size Before Export

Always run the count query first:

```sql
-- Count query
SELECT COUNT(DISTINCT user_id) as audience_size
FROM (
  -- Your main query here
)
```

If the audience is too small (<1,000), broaden your criteria.
If too large (>1M), add more filters.

### 4. Combine Audiences Strategically

**Good combinations:**
- Demographics AND Behavior → "High income Walmart shoppers"
- Geography OR Geography → "Users in CA or NY"
- Behavior NOT Demographics → "Shoppers excluding students"

**Avoid:**
- Contradictory filters → "Male AND Female"
- Too many ANDs → Will result in tiny audiences
- Unnecessary ORs → May make audience too broad

### 5. Save and Document Your Audiences

Always save your queries to files:

```
💬 You: 1 (save to file)
```

Document the business logic:
```sql
-- HIGH VALUE WALMART CUSTOMERS
-- Target: Premium product launch in California
-- Expected size: ~15K users
-- Date: 2024-01-15

SELECT DISTINCT u.user_id...
```

### 6. Validate Your Queries

Before running on production:

1. Check the SQL syntax
2. Run the count query
3. Sample 100 users and verify they match criteria
4. Compare with expected demographics

### 7. Use the Right Release ID

Always specify the correct `tx_release_id`:

```python
agent = ConversationalAgent(
    project_id="your-project",
    dataset="skyrise",
    release_id=5  # Use your latest release
)
```

---

## Troubleshooting

### Issue: "Audience is empty"

**Solution:**
- Check if filter values match your data
- Try broader criteria
- Verify the release_id is correct

### Issue: "Query takes too long"

**Solution:**
- Add indexes on commonly filtered columns
- Limit date ranges
- Use partitioned tables in BigQuery

### Issue: "Agent doesn't understand my prompt"

**Solution:**
- Be more specific: "Walmart" instead of "a store"
- Use supported filter values
- Try the guided build mode (Option 1)
- Check examples with `examples` command

### Issue: "Can't combine audiences"

**Solution:**
- Make sure you have at least 2 saved audiences
- Use correct syntax: "1 AND 2" not "and 1 2"
- Specify the operation clearly: AND, OR, or NOT

---

## Next Steps

1. **Experiment**: Try building different audience types
2. **Combine**: Create complex audiences using AND/OR/NOT
3. **Analyze**: Export audiences and analyze demographics
4. **Optimize**: Test different criteria to hit your target size
5. **Deploy**: Use the queries in your BigQuery workflows

---

## Getting Help

- Type `help` in the agent for quick reference
- Type `examples` to see example prompts
- Type `menu` to return to main menu
- Check `README.md` for complete API documentation
- Review `examples.py` for code examples

---

## Additional Resources

- **API Reference**: See `README.md`
- **Code Examples**: See `examples.py`
- **Quick Start**: See `QUICKSTART.md`
- **Schema Reference**: See schema documentation

---

**Happy Audience Building! 🎯**

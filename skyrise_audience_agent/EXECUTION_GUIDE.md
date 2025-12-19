# BigQuery Query Execution Guide

## Overview

The Skyrise Audience Builder Agent now **EXECUTES queries in BigQuery** and shows you **REAL results** from your data!

No more just generating SQL - the agent now:
- ✅ Runs queries in BigQuery
- ✅ Shows actual audience counts
- ✅ Displays sample users
- ✅ Analyzes demographics
- ✅ Exports to CSV files

---

## Quick Start

### Step 1: Install Dependencies

```bash
cd skyrise_audience_agent
pip install -r requirements.txt
```

This installs:
- `google-cloud-bigquery` - BigQuery client
- `pandas` - Data manipulation
- `db-dtypes` - BigQuery data types

### Step 2: Set Up Credentials

**Option A: Service Account JSON (Recommended)**

1. Create a service account in Google Cloud Console
2. Download the JSON key file
3. When running the agent, provide the path to the JSON file

**Option B: Default Application Credentials**

```bash
gcloud auth application-default login
```

Then just press Enter when asked for credentials path.

### Step 3: Run the Agent

```bash
python run_agent.py
```

When prompted:
```
Do you want to EXECUTE queries in BigQuery and see REAL results?
Options:
  1) Yes - Execute queries and show real audience counts/data
  2) No - Just generate SQL queries (no execution)

💬 Your choice [1]: 1

🔑 Path to service account JSON (or press Enter for default): /path/to/credentials.json
```

---

## What You'll See

### Before (SQL Only Mode)

```
✓ AUDIENCE CREATED SUCCESSFULLY!

📝 Generated SQL Query:
SELECT DISTINCT user_id
FROM `project.dataset.skyrise_user_profile`
WHERE gender_description IN ('Female')
AND age_band IN ('25-34')
...
```

Just SQL text - no actual data.

### After (Execution Mode)

```
✓ AUDIENCE CREATED SUCCESSFULLY!

🚀 EXECUTING QUERY IN BIGQUERY...
═══════════════════════════════════════════════════════════

⏳ Getting audience size...
✓ AUDIENCE SIZE: 127,543 users

⏳ Getting sample users...
─────────────────────────────────────────────────────────
👥 SAMPLE USERS (first 10):
─────────────────────────────────────────────────────────
   user_id
0  1234567
1  2345678
2  3456789
3  4567890
4  5678901
5  6789012
6  7890123
7  8901234
8  9012345
9  1023456

⏳ Analyzing demographics...
═══════════════════════════════════════════════════════
📊 AUDIENCE DEMOGRAPHICS
═══════════════════════════════════════════════════════

📊 Gender Breakdown:
  gender_description  count
0             Female  75234
1               Male  52309

📊 Age Breakdown:
      age_band  count
0        25-34  45123
1        35-44  38456
2        45-54  25987
3        18-24  17977

📊 Income Breakdown:
    income_band  count
0          High  42123
1        Medium  51234
2           Low  34186
```

**REAL DATA from your BigQuery tables!**

---

## Features

### 1. Real Audience Counts

Get the actual number of users matching your criteria:

```
✓ AUDIENCE SIZE: 127,543 users
```

Not an estimate - this is the actual count from your data!

### 2. Sample Users

See actual user IDs from your audience:

```
👥 SAMPLE USERS (first 10):
   user_id
0  1234567
1  2345678
...
```

Verify that the query is working correctly.

### 3. Demographic Breakdowns

See how your audience breaks down by:
- **Gender** - Male/Female/Other distribution
- **Age** - Age band distribution
- **Income** - Income band distribution

All with real counts from your data!

### 4. CSV Export

Export your entire audience to a CSV file:

```
What would you like to do next?
1) Save queries to file
2) Export audience to CSV  ← NEW!
3) Build another audience
4) Combine this with another audience
5) Return to main menu

💬 Your choice: 2
```

```
🚀 Exporting Audience_1 to Audience_1_export.csv...
✓ Exported 127,543 users to Audience_1_export.csv

File: Audience_1_export.csv
Rows: 127,543
```

The CSV includes:
- user_id
- gender_description
- age_band
- income_band
- user_ccode2
- cardType
- UserType
- user_l1_geo, user_l2_geo, user_l3_geo

---

## Configuration

### Execution Modes

**Mode 1: Execute Queries (Default)**
- Runs all queries in BigQuery
- Shows real counts and data
- Requires valid credentials
- Small cost per query (usually <$0.01)

**Mode 2: SQL Only**
- Just generates SQL queries
- No BigQuery connection needed
- No costs
- Good for testing or learning

### Cost Estimation

The agent shows estimated costs before running queries:

```
Query is valid
Bytes processed: 1,234,567
Estimated cost: $0.0062
```

BigQuery pricing: **$5 per TB** scanned

Typical audience query: **<$0.01**

---

## Examples

### Example 1: Basic Demographic Audience

**Prompt:**
```
Find female users aged 25-34 in the US
```

**Execution Result:**
```
✓ AUDIENCE SIZE: 45,123 users

📊 Sample shows 10 actual user IDs
📊 Demographics confirm all are Female, 25-34, US
```

### Example 2: Vendor Audience

**Prompt:**
```
Find Walmart shoppers in California
```

**Execution Result:**
```
✓ AUDIENCE SIZE: 12,456 users

👥 Sample Users: [actual user IDs]

📊 Gender: 55% Female, 45% Male
📊 Age: 35-44 most common (4,234 users)
📊 Income: Medium-High most common (5,678 users)
```

Real demographic insights from your data!

### Example 3: Combined Audience

**Prompt 1:**
```
High income users
```
**Result:** 50,000 users

**Prompt 2:**
```
Starbucks shoppers
```
**Result:** 30,000 users

**Combine:**
```
1 AND 2
```
**Result:** 8,500 users (high income Starbucks shoppers)

All with real counts!

---

## Troubleshooting

### Issue: "BigQuery client not initialized"

**Cause:** Invalid credentials or missing permissions

**Solution:**
1. Check credentials file path is correct
2. Verify service account has BigQuery permissions:
   - `BigQuery User`
   - `BigQuery Job User`
   - `BigQuery Data Viewer`
3. Try using default credentials:
   ```bash
   gcloud auth application-default login
   ```

### Issue: "Permission denied on dataset"

**Cause:** Service account doesn't have access to the dataset

**Solution:**
1. Go to BigQuery console
2. Select your dataset
3. Click "Share Dataset"
4. Add your service account email
5. Grant "BigQuery Data Viewer" role

### Issue: "Query execution failed"

**Cause:** Query syntax error or missing tables

**Solution:**
1. Check that `project_id` and `dataset` are correct
2. Verify `tx_release_id` exists in your data
3. Check table names match your schema
4. Review the SQL query that was generated

### Issue: "Query is too expensive"

**Cause:** Query scans too much data

**Solution:**
1. Add more filters to narrow down the audience
2. Use partitioned tables if available
3. Check the estimated cost before confirming
4. Consider using the SQL-only mode for testing

---

## Performance Tips

### 1. Use Specific Filters

**Slower:**
```
Find shoppers
```
(Scans entire vendor table)

**Faster:**
```
Find Walmart shoppers in the US
```
(Uses indexed columns)

### 2. Partition by Date

If your tables are partitioned by date:
```
Find users from last 30 days
```

### 3. Limit Sample Size

When previewing, limit results:
```python
executor.get_audience_sample(query, sample_size=10)
```

### 4. Cache Results

BigQuery caches results for 24 hours - repeated queries are free!

---

## Programmatic Usage

For developers who want to use the executor programmatically:

```python
from bigquery_executor import BigQueryExecutor

# Initialize
executor = BigQueryExecutor(
    project_id="your-project",
    credentials_path="/path/to/credentials.json"
)

# Execute query
result = executor.execute_query("""
    SELECT user_id
    FROM `project.dataset.skyrise_user_profile`
    WHERE gender_description = 'Female'
    AND age_band = '25-34'
""")

if result["status"] == "success":
    df = result["data"]
    print(f"Rows: {len(df)}")
    print(df.head())

# Get count
count = executor.get_audience_count(query)
print(f"Audience size: {count['formatted']}")

# Get demographics
stats = executor.get_audience_stats(query)
print(stats["gender"])
print(stats["age"])
print(stats["income"])

# Export to CSV
executor.export_audience(query, "my_audience.csv", format='csv')
```

---

## Security Best Practices

### 1. Service Account Permissions

**Minimum Required:**
- `bigquery.jobs.create` - Create query jobs
- `bigquery.tables.getData` - Read table data
- `bigquery.datasets.get` - View dataset metadata

**Grant only what's needed** - don't give Editor or Owner roles.

### 2. Credentials Storage

**DO:**
- ✅ Store credentials in a secure location
- ✅ Use environment variables
- ✅ Restrict file permissions (chmod 600)
- ✅ Use different credentials for dev/prod

**DON'T:**
- ❌ Commit credentials to git
- ❌ Share credentials in plain text
- ❌ Use personal credentials for production

### 3. Cost Controls

Set up BigQuery quotas:
```
Per-user query limit: 10 GB/day
Per-project query limit: 100 GB/day
```

Prevent accidental expensive queries.

---

## Next Steps

1. ✅ **Try it now**: `python run_agent.py`
2. 📊 **Build an audience** and see real results
3. 📈 **Analyze demographics** to understand your audience
4. 💾 **Export to CSV** for further analysis
5. 🔗 **Combine audiences** to create complex segments

---

## FAQ

**Q: Is there a cost to execute queries?**

A: Yes, BigQuery charges $5 per TB scanned. Typical audience queries cost <$0.01.

**Q: Can I use this without BigQuery credentials?**

A: Yes! Choose option 2 (SQL only mode) and the agent will just generate SQL without executing.

**Q: How long do queries take?**

A: Usually 2-5 seconds for audience counts, 5-10 seconds for full demographic analysis.

**Q: Can I export more than 100,000 users?**

A: Yes, but export time increases. Consider exporting in batches for very large audiences.

**Q: Does this work with other data warehouses?**

A: Currently only BigQuery is supported. Support for other warehouses (Snowflake, Redshift) coming soon!

---

**Ready to see real results? Start now!**

```bash
python run_agent.py
```

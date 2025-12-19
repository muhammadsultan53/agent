# 🚀 Getting Started with Skyrise Audience Builder

Welcome! This guide will get you up and running in 5 minutes.

## What You Have

A **fully working conversational AI agent** that helps you build audiences from Skyrise data. The agent:

- 🗣️ **Talks to you** - Guides you step-by-step
- 🧠 **Understands natural language** - Just describe what you want
- 🔗 **Combines audiences** - Use AND/OR/NOT logic
- 📊 **Generates SQL** - Optimized BigQuery queries
- 💾 **Saves your work** - Export to SQL files

## Quick Start (60 seconds)

### Step 1: Navigate to the directory
```bash
cd skyrise_audience_agent
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the agent!
```bash
python run_agent.py
```

That's it! The agent will guide you through the rest.

## Your First Audience

When the agent starts, you'll see a menu. Here's what to do:

1. **Enter your configuration** (project ID, dataset, release ID)

2. **Choose option 2** - "Quick Build (Natural Language)"

3. **Type something like:**
   ```
   Find female users aged 25-34 in the US
   ```

4. **Get your SQL query!** The agent generates:
   - Main query (get user IDs)
   - Count query (get audience size)
   - Export query (get users with demographics)

## What Can You Build?

### Simple Audiences

```
"Find high income males"
"Get Walmart shoppers"
"Show me users in California"
"Find users who spend over $1000"
```

### Complex Audiences

```
"Find high income females aged 35-44 who shop at Tesco in the UK"
"Get male coffee shop customers aged 25-34 in California"
"Show me users who spend over $500 at restaurants with at least 10 transactions"
```

### Combined Audiences

Build two audiences, then combine them:

```
Audience 1: "Female users aged 25-34"
Audience 2: "Walmart shoppers"

Combine: "1 AND 2"  →  Female Walmart shoppers aged 25-34
```

## Features at Your Fingertips

### Main Menu Options

1. **Build a New Audience** - Step-by-step guided experience
2. **Quick Build** - Natural language (fastest)
3. **Combine Audiences** - Merge with AND/OR/NOT
4. **Show Examples** - See what's possible
5. **Help & Tips** - Learn about filters and best practices

### Built-in Commands

While using the agent, you can type:

- `help` - Get help anytime
- `examples` - See example prompts
- `menu` - Return to main menu
- `list` - Show your saved audiences
- `quit` - Exit the agent

## Available Filters

### Demographics
- **Gender**: Male, Female, Other, Unknown
- **Age**: 18-24, 25-34, 35-44, 45-54, 55-64, 65+
- **Income**: Low, Medium-Low, Medium, Medium-High, High, Very High

### Geography
- **Countries**: US, GB, CA, AU, DE, FR, ES, IT
- **States**: CA, NY, TX, FL, etc.
- **Radius**: Within X km of a location

### Behavior
- **Stores**: Walmart, Tesco, Starbucks, Amazon, etc.
- **Categories**: Grocery, Restaurants, Gas Stations, etc.
- **Spending**: Min/max amounts, transaction counts

## Example Session

```
╔══════════════════════════════════════════════════════════════╗
║            SKYRISE AUDIENCE BUILDER AGENT                   ║
╚══════════════════════════════════════════════════════════════╝

💬 You: Find female users aged 25-34 who shop at Walmart

🤖 Agent:
🤔 I need a bit more information:
1. Which country would you like to target?
   Options: US, GB, CA, AU, DE, FR, ES, IT

💬 You: US

🤖 Agent:
✓ AUDIENCE CREATED SUCCESSFULLY!

📊 Audience Type: VENDOR
🎯 Applied Filters:
   • vendor_desc: walmart
   • gender_description: ['Female']
   • age_band: ['25-34']
   • user_ccode2: ['US']

📝 Generated SQL Query:
SELECT DISTINCT uvs.user_id
FROM `your-project.skyrise.skyrise_user_vendor_stats` uvs
JOIN `your-project.skyrise.skyrise_vendors` v
    ON uvs.vendor_id = v.vendor_id
WHERE uvs.tx_release_id = 1
AND LOWER(v.vendor_desc) LIKE '%walmart%'
...

What would you like to do next?
1) Save queries to file
2) Build another audience
3) Combine with another audience
4) Return to main menu
```

## Pro Tips

### Tip 1: Start Broad, Then Narrow

```
Build 1: "Find Walmart shoppers"         → 500K users
Build 2: "Add California filter"         → 50K users
Build 3: "Add high income"               → 10K users
```

### Tip 2: Use the Guided Builder for Learning

Choose option **1** (Build a New Audience) to see all available filters and learn what's possible.

### Tip 3: Combine for Complex Logic

Instead of trying to describe complex logic in one sentence, build simple audiences and combine them:

```
Audience 1: "Female users"
Audience 2: "Male users aged 25-34"
Combine: "1 OR 2"  →  Females OR young males
```

### Tip 4: Save Your Queries

Always save your queries to files! You can run them in BigQuery or share with your team.

## Common Use Cases

### Use Case 1: Campaign Targeting
```
"Find high income females aged 35-54 in the US who shop at premium stores"
```

### Use Case 2: Geographic Expansion
```
Build: "Walmart shoppers in California"
Then: Build for other states and compare
```

### Use Case 3: Competitive Analysis
```
Build: "Tesco shoppers"
Build: "Sainsbury's shoppers"
Compare demographics and spending patterns
```

### Use Case 4: Customer Segmentation
```
High Value: "Users who spend over $5000"
Frequent: "Users with 50+ transactions"
Combine: "High Value OR Frequent"  →  Valuable customers
```

## Troubleshooting

### "Agent doesn't understand my prompt"

✅ **Solution**: Be specific!
- ❌ "Find shoppers" → Too vague
- ✅ "Find Walmart shoppers in the US" → Clear

### "Audience is empty"

✅ **Solution**: Check your filters
- Verify filter values match your data
- Try broader criteria
- Check the release_id is correct

### "Need more information"

✅ **Solution**: Just answer the questions!
The agent will ask for missing filters. Answer them or type 'skip' to skip optional ones.

## Next Steps

1. ✅ **Try it now**: Run `python run_agent.py`
2. 📚 **Learn more**: Read `TUTORIAL.md` for detailed examples
3. 🔧 **Customize**: Edit `schema_config.py` to add your vendors/categories
4. 🚀 **Deploy**: Use the generated SQL in your BigQuery workflows

## Documentation

- **QUICKSTART.md** - Quick reference (this file)
- **TUTORIAL.md** - Step-by-step tutorial with examples
- **README.md** - Complete API documentation
- **examples.py** - Code examples for developers

## Support

Got stuck? The agent has built-in help:

```
Type 'help' - Get help on commands and filters
Type 'examples' - See example prompts
Type 'menu' - Return to main menu
```

---

**Ready to build your first audience? Let's go! 🚀**

```bash
python run_agent.py
```

"""
Skyrise Database Schema Configuration
Contains table definitions and valid filter values for audience generation
"""

# Schema Configuration
SCHEMA = {
    "project_id": "your-project-id",  # Update with your actual BigQuery project
    "dataset": "skyrise",  # Update with your actual dataset name
}

# Valid filter values from the Skyrise schema
VALID_FILTERS = {
    "gender_description": [
        "Male",
        "Female",
        "Other",
        "Unknown"
    ],

    "age_band": [
        "18-24",
        "25-34",
        "35-44",
        "45-54",
        "55-64",
        "65+"
    ],

    "income_band": [
        "Low",
        "Medium-Low",
        "Medium",
        "Medium-High",
        "High",
        "Very High"
    ],

    "standard_income_band": [
        "Low",
        "Medium",
        "High"
    ],

    "spend_power_cat3": [
        "Low",
        "Medium",
        "High"
    ],

    "spend_power_cat5": [
        "Very Low",
        "Low",
        "Medium",
        "High",
        "Very High"
    ],

    "UserType": [
        "Active",
        "Regular",
        "Occasional",
        "Inactive"
    ],

    "cardType": [
        "Credit",
        "Debit",
        "Prepaid"
    ],

    "user_ccode2": [
        "US",
        "GB",
        "CA",
        "AU",
        "DE",
        "FR",
        "ES",
        "IT"
    ],

    "vendor_ccode2": [
        "US",
        "GB",
        "CA",
        "AU",
        "DE",
        "FR",
        "ES",
        "IT"
    ]
}

# Common merchant categories
COMMON_MERCHANTS = [
    "Grocery Stores",
    "Restaurants",
    "Gas Stations",
    "Department Stores",
    "Clothing Stores",
    "Electronics",
    "Pharmacies",
    "Fast Food",
    "Coffee Shops",
    "Online Retail"
]

# Common grocer chains (for grocer-specific audiences)
COMMON_GROCERS = [
    "Walmart",
    "Tesco",
    "Sainsbury's",
    "Kroger",
    "Whole Foods",
    "Aldi",
    "Lidl"
]

# Table definitions for query building
TABLES = {
    "user_profile": "skyrise_user_profile",
    "users": "skyrise_users",
    "vendors": "skyrise_vendors",
    "merchants": "skyrise_merchants",
    "txns": "skyrise_txns",
    "user_vendor_stats": "skyrise_user_vendor_stats",
    "user_vendor_stats_geo": "skyrise_user_vendor_stats_geo__vendor_id",
    "user_geo": "dref_user_geo_zip",
    "vendor_geo": "dref_vendor_geo_resolved",
    "lookalike_merch_users": "dref_lookalike_merch_users",
    "lookalike_vendor_profile": "dref_lookalike_vendor_profile",
    "grocer_matches": "dref_grocer_vendor_matches",
    "profile_calc_income": "dref_profile_calc_income_band",
    "user_vendor_dwh": "skyrise_user_vendor_dwh",
    "ccode2_weightings": "ref_ccode2_weightings"
}

# Geographic levels
GEO_LEVELS = {
    "home": "user_home_geo",
    "l1": "user_l1_geo",  # State/Region
    "l2": "user_l2_geo",  # County/District
    "l3": "user_l3_geo"   # City/Town
}

# Query templates for different audience types
AUDIENCE_TEMPLATES = {
    "demographic": """
        SELECT DISTINCT u.user_id
        FROM `{project}.{dataset}.{user_profile_table}` u
        WHERE u.tx_release_id = {release_id}
        {filters}
    """,

    "vendor_shoppers": """
        SELECT DISTINCT uvs.user_id
        FROM `{project}.{dataset}.{user_vendor_stats_table}` uvs
        JOIN `{project}.{dataset}.{vendors_table}` v
            ON uvs.vendor_id = v.vendor_id
            AND uvs.tx_release_id = v.tx_release_id
        WHERE uvs.tx_release_id = {release_id}
        {filters}
    """,

    "merchant_category": """
        SELECT DISTINCT uvs.user_id
        FROM `{project}.{dataset}.{user_vendor_stats_table}` uvs
        JOIN `{project}.{dataset}.{vendors_table}` v
            ON uvs.vendor_id = v.vendor_id
            AND uvs.tx_release_id = v.tx_release_id
        JOIN `{project}.{dataset}.{merchants_table}` m
            ON v.merch_id = m.merch_id
            AND v.tx_release_id = m.tx_release_id
        WHERE uvs.tx_release_id = {release_id}
        {filters}
    """,

    "geographic": """
        SELECT DISTINCT ug.user_id
        FROM `{project}.{dataset}.{user_geo_table}` ug
        WHERE ug.tx_release_id = {release_id}
        {filters}
    """,

    "lookalike": """
        SELECT DISTINCT lvu.user_id
        FROM `{project}.{dataset}.{lookalike_table}` lvu
        WHERE lvu.tx_release_id = {release_id}
        {filters}
    """,

    "spending_behavior": """
        SELECT DISTINCT uvs.user_id
        FROM `{project}.{dataset}.{user_vendor_stats_table}` uvs
        WHERE uvs.tx_release_id = {release_id}
        {filters}
    """,

    "grocer": """
        SELECT DISTINCT uvs.user_id
        FROM `{project}.{dataset}.{user_vendor_stats_table}` uvs
        JOIN `{project}.{dataset}.{grocer_matches_table}` gm
            ON uvs.vendor_id = gm.vendor_id
            AND uvs.tx_release_id = gm.tx_release_id
        WHERE uvs.tx_release_id = {release_id}
        {filters}
    """
}

# Default release ID (should be configured or fetched dynamically)
DEFAULT_RELEASE_ID = 1

"""
Query Builder for Skyrise Audience Generation
Generates BigQuery SQL based on filters and audience requirements
"""

from typing import Dict, List, Optional, Any
from schema_config import TABLES, AUDIENCE_TEMPLATES, SCHEMA, DEFAULT_RELEASE_ID, GEO_LEVELS


class QueryBuilder:
    """Builds BigQuery SQL queries for audience generation"""

    def __init__(self, project_id: str = None, dataset: str = None, release_id: int = None):
        self.project_id = project_id or SCHEMA["project_id"]
        self.dataset = dataset or SCHEMA["dataset"]
        self.release_id = release_id or DEFAULT_RELEASE_ID

    def build_demographic_audience(self, filters: Dict[str, Any]) -> str:
        """
        Build query for demographic-based audience

        Args:
            filters: Dict with keys like gender_description, age_band, income_band, etc.

        Returns:
            SQL query string
        """
        where_clauses = []

        if filters.get("gender_description"):
            where_clauses.append(f"u.gender_description IN ({self._format_list(filters['gender_description'])})")

        if filters.get("age_band"):
            where_clauses.append(f"u.age_band IN ({self._format_list(filters['age_band'])})")

        if filters.get("income_band"):
            where_clauses.append(f"u.income_band IN ({self._format_list(filters['income_band'])})")

        if filters.get("user_ccode2"):
            where_clauses.append(f"u.user_ccode2 IN ({self._format_list(filters['user_ccode2'])})")

        if filters.get("cardType"):
            where_clauses.append(f"u.cardType IN ({self._format_list(filters['cardType'])})")

        if filters.get("UserType"):
            where_clauses.append(f"u.UserType IN ({self._format_list(filters['UserType'])})")

        if filters.get("OpenBankingFlag") is not None:
            where_clauses.append(f"u.OpenBankingFlag = {filters['OpenBankingFlag']}")

        filter_sql = "AND " + " AND ".join(where_clauses) if where_clauses else ""

        query = AUDIENCE_TEMPLATES["demographic"].format(
            project=self.project_id,
            dataset=self.dataset,
            user_profile_table=TABLES["user_profile"],
            release_id=self.release_id,
            filters=filter_sql
        )

        return query

    def build_vendor_audience(self, filters: Dict[str, Any]) -> str:
        """
        Build query for vendor-based audience (users who shop at specific vendors)

        Args:
            filters: Dict with vendor_desc, vendor_id, min_transactions, min_spend, etc.

        Returns:
            SQL query string
        """
        where_clauses = []

        if filters.get("vendor_desc"):
            where_clauses.append(f"LOWER(v.vendor_desc) LIKE '%{filters['vendor_desc'].lower()}%'")

        if filters.get("vendor_id"):
            vendor_ids = filters['vendor_id'] if isinstance(filters['vendor_id'], list) else [filters['vendor_id']]
            where_clauses.append(f"v.vendor_id IN ({','.join(map(str, vendor_ids))})")

        if filters.get("vendor_ccode2"):
            where_clauses.append(f"v.vendor_ccode2 IN ({self._format_list(filters['vendor_ccode2'])})")

        if filters.get("min_transactions"):
            where_clauses.append(f"uvs.count_tx >= {filters['min_transactions']}")

        if filters.get("min_spend"):
            where_clauses.append(f"uvs.total_spend >= {filters['min_spend']}")

        if filters.get("date_from"):
            where_clauses.append(f"uvs.max_dt >= '{filters['date_from']}'")

        if filters.get("date_to"):
            where_clauses.append(f"uvs.min_dt <= '{filters['date_to']}'")

        filter_sql = "AND " + " AND ".join(where_clauses) if where_clauses else ""

        query = AUDIENCE_TEMPLATES["vendor_shoppers"].format(
            project=self.project_id,
            dataset=self.dataset,
            user_vendor_stats_table=TABLES["user_vendor_stats"],
            vendors_table=TABLES["vendors"],
            release_id=self.release_id,
            filters=filter_sql
        )

        return query

    def build_merchant_category_audience(self, filters: Dict[str, Any]) -> str:
        """
        Build query for merchant category-based audience

        Args:
            filters: Dict with merch_desc, merch_id, mcc, etc.

        Returns:
            SQL query string
        """
        where_clauses = []

        if filters.get("merch_desc"):
            where_clauses.append(f"LOWER(m.merch_desc) LIKE '%{filters['merch_desc'].lower()}%'")

        if filters.get("merch_id"):
            merch_ids = filters['merch_id'] if isinstance(filters['merch_id'], list) else [filters['merch_id']]
            where_clauses.append(f"m.merch_id IN ({','.join(map(str, merch_ids))})")

        if filters.get("mcc"):
            mccs = filters['mcc'] if isinstance(filters['mcc'], list) else [filters['mcc']]
            where_clauses.append(f"v.mcc IN ({','.join(map(str, mccs))})")

        if filters.get("min_transactions"):
            where_clauses.append(f"uvs.count_tx >= {filters['min_transactions']}")

        filter_sql = "AND " + " AND ".join(where_clauses) if where_clauses else ""

        query = AUDIENCE_TEMPLATES["merchant_category"].format(
            project=self.project_id,
            dataset=self.dataset,
            user_vendor_stats_table=TABLES["user_vendor_stats"],
            vendors_table=TABLES["vendors"],
            merchants_table=TABLES["merchants"],
            release_id=self.release_id,
            filters=filter_sql
        )

        return query

    def build_geographic_audience(self, filters: Dict[str, Any]) -> str:
        """
        Build query for geographic-based audience

        Args:
            filters: Dict with geo_level, geo_value, lat/lon, radius, etc.

        Returns:
            SQL query string
        """
        where_clauses = []

        if filters.get("user_ccode2"):
            where_clauses.append(f"ug.user_ccode2 IN ({self._format_list(filters['user_ccode2'])})")

        # Geographic filtering by level
        if filters.get("user_l1_geo"):
            where_clauses.append(f"ug.user_l1_geo IN ({self._format_list(filters['user_l1_geo'])})")

        if filters.get("user_l2_geo"):
            where_clauses.append(f"ug.user_l2_geo IN ({self._format_list(filters['user_l2_geo'])})")

        if filters.get("user_l3_geo"):
            where_clauses.append(f"ug.user_l3_geo IN ({self._format_list(filters['user_l3_geo'])})")

        # Radius-based filtering
        if filters.get("center_lat") and filters.get("center_lon") and filters.get("radius_km"):
            lat = filters["center_lat"]
            lon = filters["center_lon"]
            radius = filters["radius_km"]
            where_clauses.append(f"""
                ST_DISTANCE(
                    ST_GEOGPOINT(ug.user_home_lon, ug.user_home_lat),
                    ST_GEOGPOINT({lon}, {lat})
                ) <= {radius * 1000}
            """)

        filter_sql = "AND " + " AND ".join(where_clauses) if where_clauses else ""

        query = AUDIENCE_TEMPLATES["geographic"].format(
            project=self.project_id,
            dataset=self.dataset,
            user_geo_table=TABLES["user_geo"],
            release_id=self.release_id,
            filters=filter_sql
        )

        return query

    def build_grocer_audience(self, filters: Dict[str, Any]) -> str:
        """
        Build query for grocer-specific audience

        Args:
            filters: Dict with grocer_desc (e.g., "Walmart", "Tesco")

        Returns:
            SQL query string
        """
        where_clauses = []

        if filters.get("grocer_desc"):
            where_clauses.append(f"gm.grocer_desc IN ({self._format_list(filters['grocer_desc'])})")

        if filters.get("min_transactions"):
            where_clauses.append(f"uvs.count_tx >= {filters['min_transactions']}")

        filter_sql = "AND " + " AND ".join(where_clauses) if where_clauses else ""

        query = AUDIENCE_TEMPLATES["grocer"].format(
            project=self.project_id,
            dataset=self.dataset,
            user_vendor_stats_table=TABLES["user_vendor_stats"],
            grocer_matches_table=TABLES["grocer_matches"],
            release_id=self.release_id,
            filters=filter_sql
        )

        return query

    def build_lookalike_audience(self, filters: Dict[str, Any]) -> str:
        """
        Build query for lookalike audience based on merchant category

        Args:
            filters: Dict with merch_id, user_ccode2, etc.

        Returns:
            SQL query string
        """
        where_clauses = []

        if filters.get("merch_id"):
            merch_ids = filters['merch_id'] if isinstance(filters['merch_id'], list) else [filters['merch_id']]
            where_clauses.append(f"lvu.merch_id IN ({','.join(map(str, merch_ids))})")

        if filters.get("user_ccode2"):
            where_clauses.append(f"lvu.user_ccode2 IN ({self._format_list(filters['user_ccode2'])})")

        filter_sql = "AND " + " AND ".join(where_clauses) if where_clauses else ""

        query = AUDIENCE_TEMPLATES["lookalike"].format(
            project=self.project_id,
            dataset=self.dataset,
            lookalike_table=TABLES["lookalike_merch_users"],
            release_id=self.release_id,
            filters=filter_sql
        )

        return query

    def build_spending_behavior_audience(self, filters: Dict[str, Any]) -> str:
        """
        Build query for spending behavior-based audience

        Args:
            filters: Dict with min_spend, max_spend, min_transactions, date ranges

        Returns:
            SQL query string
        """
        where_clauses = []

        if filters.get("min_total_spend"):
            where_clauses.append(f"uvs.total_spend >= {filters['min_total_spend']}")

        if filters.get("max_total_spend"):
            where_clauses.append(f"uvs.total_spend <= {filters['max_total_spend']}")

        if filters.get("min_transactions"):
            where_clauses.append(f"uvs.count_tx >= {filters['min_transactions']}")

        if filters.get("max_transactions"):
            where_clauses.append(f"uvs.count_tx <= {filters['max_transactions']}")

        filter_sql = "AND " + " AND ".join(where_clauses) if where_clauses else ""

        query = AUDIENCE_TEMPLATES["spending_behavior"].format(
            project=self.project_id,
            dataset=self.dataset,
            user_vendor_stats_table=TABLES["user_vendor_stats"],
            release_id=self.release_id,
            filters=filter_sql
        )

        return query

    def build_combined_audience(self, audience_queries: List[str], operation: str = "INTERSECT") -> str:
        """
        Combine multiple audience queries with INTERSECT, UNION, or EXCEPT

        Args:
            audience_queries: List of SQL queries
            operation: INTERSECT, UNION, or EXCEPT

        Returns:
            Combined SQL query
        """
        valid_operations = ["INTERSECT", "UNION", "EXCEPT"]
        if operation.upper() not in valid_operations:
            raise ValueError(f"Operation must be one of {valid_operations}")

        return f"\n{operation.upper()} DISTINCT\n".join(audience_queries)

    def add_demographic_refinement(self, base_query: str, demographic_filters: Dict[str, Any]) -> str:
        """
        Add demographic filtering to an existing audience query

        Args:
            base_query: Base audience query
            demographic_filters: Demographic filters to apply

        Returns:
            Refined query with demographic filters
        """
        refinement_clauses = []

        if demographic_filters.get("gender_description"):
            refinement_clauses.append(f"up.gender_description IN ({self._format_list(demographic_filters['gender_description'])})")

        if demographic_filters.get("age_band"):
            refinement_clauses.append(f"up.age_band IN ({self._format_list(demographic_filters['age_band'])})")

        if demographic_filters.get("income_band"):
            refinement_clauses.append(f"up.income_band IN ({self._format_list(demographic_filters['income_band'])})")

        if not refinement_clauses:
            return base_query

        refinement_sql = " AND ".join(refinement_clauses)

        refined_query = f"""
        SELECT base.user_id
        FROM ({base_query}) base
        JOIN `{self.project_id}.{self.dataset}.{TABLES['user_profile']}` up
            ON base.user_id = up.user_id
            AND up.tx_release_id = {self.release_id}
        WHERE {refinement_sql}
        """

        return refined_query

    def _format_list(self, values) -> str:
        """Format list of values for SQL IN clause"""
        if isinstance(values, str):
            values = [values]
        return ", ".join([f"'{v}'" for v in values])

    def get_audience_count(self, query: str) -> str:
        """Wrap query to get count"""
        return f"SELECT COUNT(DISTINCT user_id) as audience_size FROM ({query})"

    def get_audience_export(self, query: str, include_demographics: bool = True) -> str:
        """
        Create export query with user details

        Args:
            query: Base audience query
            include_demographics: Include demographic info

        Returns:
            Export query with user details
        """
        if include_demographics:
            return f"""
            SELECT
                base.user_id,
                up.gender_description,
                up.age_band,
                up.income_band,
                up.user_ccode2,
                up.cardType,
                up.UserType,
                ug.user_l1_geo,
                ug.user_l2_geo,
                ug.user_l3_geo
            FROM ({query}) base
            JOIN `{self.project_id}.{self.dataset}.{TABLES['user_profile']}` up
                ON base.user_id = up.user_id
                AND up.tx_release_id = {self.release_id}
            LEFT JOIN `{self.project_id}.{self.dataset}.{TABLES['user_geo']}` ug
                ON base.user_id = ug.user_id
                AND ug.tx_release_id = {self.release_id}
            """
        else:
            return query

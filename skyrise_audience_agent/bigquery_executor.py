"""
BigQuery Executor - Actually runs queries and shows real results
"""

from typing import Dict, List, Any, Optional
import pandas as pd


class BigQueryExecutor:
    """
    Executes queries in BigQuery and returns actual results
    """

    def __init__(self, project_id: str, credentials_path: Optional[str] = None):
        """
        Initialize BigQuery client

        Args:
            project_id: Your GCP project ID
            credentials_path: Path to service account JSON (optional, uses default credentials if not provided)
        """
        self.project_id = project_id
        self.client = None
        self._initialize_client(credentials_path)

    def _initialize_client(self, credentials_path: Optional[str] = None):
        """Initialize BigQuery client"""
        try:
            from google.cloud import bigquery
            import os

            if credentials_path:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

            self.client = bigquery.Client(project=self.project_id)
            print(f"✓ Connected to BigQuery project: {self.project_id}")

        except ImportError:
            print("⚠️  google-cloud-bigquery not installed. Install with:")
            print("   pip install google-cloud-bigquery")
            self.client = None

        except Exception as e:
            print(f"⚠️  Could not connect to BigQuery: {str(e)}")
            print("   Make sure you have valid credentials set up.")
            self.client = None

    def is_connected(self) -> bool:
        """Check if BigQuery client is connected"""
        return self.client is not None

    def execute_query(self, query: str, max_results: int = 1000) -> Dict[str, Any]:
        """
        Execute a query and return results

        Args:
            query: SQL query to execute
            max_results: Maximum number of rows to return

        Returns:
            Dict with status, data, and metadata
        """
        if not self.client:
            return {
                "status": "error",
                "message": "BigQuery client not initialized. Check your credentials.",
                "data": None
            }

        try:
            # Run the query
            query_job = self.client.query(query)

            # Wait for results
            results = query_job.result(max_results=max_results)

            # Convert to pandas DataFrame
            df = results.to_dataframe()

            # Get row count (total, not just returned)
            total_rows = results.total_rows

            return {
                "status": "success",
                "data": df,
                "total_rows": total_rows,
                "returned_rows": len(df),
                "columns": list(df.columns),
                "bytes_processed": query_job.total_bytes_processed,
                "execution_time": query_job.ended - query_job.started if query_job.ended else None
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    def get_audience_count(self, query: str) -> Dict[str, Any]:
        """
        Get count of users in audience

        Args:
            query: Audience query (returns user_ids)

        Returns:
            Dict with count and status
        """
        count_query = f"""
        SELECT COUNT(DISTINCT user_id) as audience_size
        FROM ({query})
        """

        result = self.execute_query(count_query, max_results=1)

        if result["status"] == "success" and result["data"] is not None:
            count = int(result["data"]['audience_size'].iloc[0])
            return {
                "status": "success",
                "count": count,
                "formatted": f"{count:,}"
            }
        else:
            return {
                "status": "error",
                "message": result.get("message", "Failed to get count"),
                "count": 0
            }

    def get_audience_sample(self, query: str, sample_size: int = 10) -> Dict[str, Any]:
        """
        Get sample users from audience

        Args:
            query: Audience query
            sample_size: Number of users to sample

        Returns:
            Dict with sample data
        """
        sample_query = f"""
        {query}
        LIMIT {sample_size}
        """

        return self.execute_query(sample_query, max_results=sample_size)

    def get_audience_with_demographics(self, query: str, max_results: int = 100) -> Dict[str, Any]:
        """
        Get audience with demographic information

        Args:
            query: Audience query (returns user_ids)
            max_results: Maximum users to return

        Returns:
            Dict with user demographics
        """
        # This would use the export query that includes demographics
        # For now, just return the audience
        return self.execute_query(query, max_results=max_results)

    def get_audience_stats(self, query: str) -> Dict[str, Any]:
        """
        Get statistical breakdown of audience

        Args:
            query: Audience query

        Returns:
            Dict with demographic breakdowns
        """
        if not self.client:
            return {"status": "error", "message": "BigQuery client not initialized"}

        try:
            # Get gender breakdown
            gender_query = f"""
            SELECT
                up.gender_description,
                COUNT(DISTINCT aud.user_id) as count
            FROM ({query}) aud
            JOIN `{self.project_id}.skyrise.skyrise_user_profile` up
                ON aud.user_id = up.user_id
            GROUP BY up.gender_description
            ORDER BY count DESC
            """

            gender_result = self.execute_query(gender_query, max_results=10)

            # Get age breakdown
            age_query = f"""
            SELECT
                up.age_band,
                COUNT(DISTINCT aud.user_id) as count
            FROM ({query}) aud
            JOIN `{self.project_id}.skyrise.skyrise_user_profile` up
                ON aud.user_id = up.user_id
            GROUP BY up.age_band
            ORDER BY count DESC
            """

            age_result = self.execute_query(age_query, max_results=10)

            # Get income breakdown
            income_query = f"""
            SELECT
                up.income_band,
                COUNT(DISTINCT aud.user_id) as count
            FROM ({query}) aud
            JOIN `{self.project_id}.skyrise.skyrise_user_profile` up
                ON aud.user_id = up.user_id
            GROUP BY up.income_band
            ORDER BY count DESC
            """

            income_result = self.execute_query(income_query, max_results=10)

            return {
                "status": "success",
                "gender": gender_result["data"] if gender_result["status"] == "success" else None,
                "age": age_result["data"] if age_result["status"] == "success" else None,
                "income": income_result["data"] if income_result["status"] == "success" else None
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def export_audience(self, query: str, output_file: str, format: str = 'csv') -> Dict[str, Any]:
        """
        Export audience to file

        Args:
            query: Audience query
            output_file: Output filename
            format: 'csv' or 'json'

        Returns:
            Dict with export status
        """
        # Execute query with no limit for full export
        result = self.execute_query(query, max_results=100000)

        if result["status"] != "success":
            return result

        try:
            df = result["data"]

            if format == 'csv':
                df.to_csv(output_file, index=False)
            elif format == 'json':
                df.to_json(output_file, orient='records', indent=2)
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported format: {format}"
                }

            return {
                "status": "success",
                "message": f"Exported {len(df):,} users to {output_file}",
                "rows_exported": len(df),
                "file": output_file
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Export failed: {str(e)}"
            }

    def validate_query(self, query: str) -> Dict[str, Any]:
        """
        Validate query without executing it (dry run)

        Args:
            query: SQL query to validate

        Returns:
            Dict with validation status
        """
        if not self.client:
            return {"status": "error", "message": "BigQuery client not initialized"}

        try:
            from google.cloud import bigquery

            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            query_job = self.client.query(query, job_config=job_config)

            return {
                "status": "success",
                "message": "Query is valid",
                "bytes_processed": query_job.total_bytes_processed,
                "estimated_cost": f"${(query_job.total_bytes_processed / 1e12) * 5:.4f}"  # $5 per TB
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Query validation failed: {str(e)}"
            }


def format_dataframe(df: pd.DataFrame, max_rows: int = 20) -> str:
    """Format pandas DataFrame for display"""
    if df is None or len(df) == 0:
        return "No data"

    # Set pandas display options
    pd.set_option('display.max_rows', max_rows)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)

    return df.to_string()


def format_stats(stats: Dict[str, Any]) -> str:
    """Format audience statistics for display"""
    if stats["status"] != "success":
        return f"Error: {stats.get('message', 'Unknown error')}"

    output = []

    if stats.get("gender") is not None:
        output.append("\n📊 Gender Breakdown:")
        output.append(format_dataframe(stats["gender"]))

    if stats.get("age") is not None:
        output.append("\n📊 Age Breakdown:")
        output.append(format_dataframe(stats["age"]))

    if stats.get("income") is not None:
        output.append("\n📊 Income Breakdown:")
        output.append(format_dataframe(stats["income"]))

    return "\n".join(output) if output else "No statistics available"

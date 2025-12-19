"""
Skyrise Audience Generation Agent
Interactive agent that takes natural language prompts and generates SQL queries for audience creation
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from query_builder import QueryBuilder
from schema_config import VALID_FILTERS, COMMON_MERCHANTS, COMMON_GROCERS


class AudienceAgent:
    """
    Interactive agent for audience generation
    Takes natural language prompts and generates audiences
    """

    def __init__(self, project_id: str = None, dataset: str = None, release_id: int = None):
        self.query_builder = QueryBuilder(project_id, dataset, release_id)
        self.context = {}  # Store conversation context
        self.pending_filters = {}  # Store filters that need clarification

    def process_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """
        Process user prompt and determine audience requirements

        Args:
            user_prompt: Natural language prompt from user

        Returns:
            Dict with status, message, query, and questions
        """
        prompt_lower = user_prompt.lower()

        # Parse the prompt to identify audience type and filters
        audience_info = self._parse_prompt(prompt_lower, user_prompt)

        # Check if we need clarification
        questions = self._get_clarifying_questions(audience_info)

        if questions:
            return {
                "status": "needs_clarification",
                "message": "I need some additional information to build your audience:",
                "questions": questions,
                "audience_type": audience_info["type"],
                "parsed_filters": audience_info["filters"]
            }

        # Build the query
        try:
            query = self._build_query_from_info(audience_info)

            return {
                "status": "success",
                "message": "Audience query generated successfully!",
                "query": query,
                "audience_type": audience_info["type"],
                "filters": audience_info["filters"],
                "count_query": self.query_builder.get_audience_count(query),
                "export_query": self.query_builder.get_audience_export(query)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating query: {str(e)}",
                "audience_type": audience_info["type"],
                "filters": audience_info["filters"]
            }

    def _parse_prompt(self, prompt_lower: str, original_prompt: str) -> Dict[str, Any]:
        """Parse user prompt to identify audience type and filters"""

        audience_info = {
            "type": None,
            "filters": {},
            "operations": []
        }

        # Detect audience type
        # Check for grocer first (more specific than vendor)
        if any(keyword in prompt_lower for keyword in ["grocery", "grocer", "supermarket"]):
            audience_info["type"] = "grocer"
            # Extract grocer name
            grocer_match = self._extract_grocer_name(prompt_lower, original_prompt)
            if grocer_match:
                audience_info["filters"]["grocer_desc"] = grocer_match

        # Check for vendor patterns
        elif any(keyword in prompt_lower for keyword in ["shop at", "shopping at", "customer of", "customers of", "buy at", "purchase at", "buying at"]):
            audience_info["type"] = "vendor"
            # Extract vendor name
            vendor_match = self._extract_vendor_name(prompt_lower, original_prompt)
            if vendor_match:
                audience_info["filters"]["vendor_desc"] = vendor_match

        # Check for "[vendor] shoppers/customers" pattern
        elif re.search(r'([a-zA-Z0-9\s&\'-]+)\s+(shoppers?|customers?)', prompt_lower):
            # Try to extract vendor name first
            match = re.search(r'([a-zA-Z0-9&\'-]+)\s+(shoppers?|customers?)', prompt_lower)
            if match:
                potential_vendor = match.group(1).strip()
                # Check if it's a known grocer
                if any(grocer.lower() == potential_vendor.lower() for grocer in COMMON_GROCERS):
                    audience_info["type"] = "grocer"
                    audience_info["filters"]["grocer_desc"] = potential_vendor
                # Otherwise treat as vendor (if not a generic/demographic word)
                elif potential_vendor.lower() not in ["all", "the", "some", "any", "new", "existing", "female", "male", "young", "old"]:
                    audience_info["type"] = "vendor"
                    audience_info["filters"]["vendor_desc"] = potential_vendor
                else:
                    # Generic demographic word, treat as demographic audience
                    audience_info["type"] = "demographic"

        elif any(keyword in prompt_lower for keyword in ["category", "merchant type", "mcc", "merchant category"]):
            audience_info["type"] = "merchant_category"
            # Extract merchant category
            merch_match = self._extract_merchant_category(prompt_lower, original_prompt)
            if merch_match:
                audience_info["filters"]["merch_desc"] = merch_match

        elif any(keyword in prompt_lower for keyword in ["location", "geographic", "region", "state", "city", "near", "within"]):
            audience_info["type"] = "geographic"
            # Extract geographic filters
            geo_filters = self._extract_geographic_filters(prompt_lower, original_prompt)
            audience_info["filters"].update(geo_filters)

        elif any(keyword in prompt_lower for keyword in ["lookalike", "similar to", "like customers who"]):
            audience_info["type"] = "lookalike"

        elif any(keyword in prompt_lower for keyword in ["spend", "spending", "transaction", "purchase amount"]):
            audience_info["type"] = "spending_behavior"
            # Extract spending filters
            spend_filters = self._extract_spending_filters(prompt_lower, original_prompt)
            audience_info["filters"].update(spend_filters)

        else:
            # Default to demographic if no specific type detected
            audience_info["type"] = "demographic"

        # Extract demographic filters (applicable to all types)
        demographic_filters = self._extract_demographic_filters(prompt_lower, original_prompt)
        audience_info["filters"].update(demographic_filters)

        return audience_info

    def _extract_vendor_name(self, prompt_lower: str, original: str) -> Optional[str]:
        """Extract vendor name from prompt"""
        patterns = [
            r'shop(?:s|ping|pers)? at ([a-zA-Z0-9\s&\'-]+?)(?:\s+in\s+|\s+from\s+|\s+with\s+|\s+who\s+|\s+that\s+|\s+and\s+|$)',
            r'customers? of ([a-zA-Z0-9\s&\'-]+?)(?:\s+in\s+|\s+from\s+|\s+with\s+|\s+who\s+|\s+that\s+|\s+and\s+|$)',
            r'buy(?:s|ing)? at ([a-zA-Z0-9\s&\'-]+?)(?:\s+in\s+|\s+from\s+|\s+with\s+|\s+who\s+|\s+that\s+|\s+and\s+|$)',
            r'purchase(?:d|s|ing)? at ([a-zA-Z0-9\s&\'-]+?)(?:\s+in\s+|\s+from\s+|\s+with\s+|\s+who\s+|\s+that\s+|\s+and\s+|$)',
            r'vendor (?:is |named )?["\']?([a-zA-Z0-9\s&\'-]+?)["\']?(?:\s+in\s+|\s+from\s+|\s+with\s+|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                vendor = match.group(1).strip()
                return vendor

        return None

    def _extract_grocer_name(self, prompt_lower: str, original: str) -> Optional[str]:
        """Extract grocer name from prompt"""
        # Check for common grocer names
        for grocer in COMMON_GROCERS:
            if grocer.lower() in prompt_lower:
                return grocer

        # Only extract if there's a specific pattern with quotes or "named"
        patterns = [
            r'(?:grocery|grocer|supermarket)\s+(?:named|called)\s+["\']?([a-zA-Z0-9\s&\'-]+?)["\']?(?:\s+in\s+|\s+from\s+|$)',
            r'["\']([a-zA-Z0-9\s&\'-]+)["\']?\s+(?:grocery|grocer|supermarket)'
        ]

        for pattern in patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                name = match.group(1).strip()
                # Don't return generic words like "stores", "store"
                if name.lower() not in ["store", "stores", "shop", "shops"]:
                    return name

        return None

    def _extract_merchant_category(self, prompt_lower: str, original: str) -> Optional[str]:
        """Extract merchant category from prompt"""
        # Check for common merchant categories
        for merchant in COMMON_MERCHANTS:
            if merchant.lower() in prompt_lower:
                return merchant

        patterns = [
            r'category (?:is |of )?["\']?([a-zA-Z0-9\s&\'-]+)["\']?',
            r'merchant (?:category|type) (?:is |of )?["\']?([a-zA-Z0-9\s&\'-]+)["\']?'
        ]

        for pattern in patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                return match.group(1).strip()

        return None

    def _extract_demographic_filters(self, prompt_lower: str, original: str) -> Dict[str, Any]:
        """Extract demographic filters from prompt"""
        filters = {}

        # Gender - check female first since it contains "male"
        if "female" in prompt_lower or "women" in prompt_lower:
            filters["gender_description"] = ["Female"]
        elif re.search(r'\bmale\b|\bmen\b', prompt_lower):
            filters["gender_description"] = ["Male"]

        # Age bands
        age_patterns = [
            (r'\b18[-\s]?24\b', "18-24"),
            (r'\b25[-\s]?34\b', "25-34"),
            (r'\b35[-\s]?44\b', "35-44"),
            (r'\b45[-\s]?54\b', "45-54"),
            (r'\b55[-\s]?64\b', "55-64"),
            (r'\b65\+|65 and (over|older|above)\b', "65+"),
            (r'young adults?|millennials?', "25-34"),
            (r'middle[-\s]?aged?', "35-54"),
            (r'seniors?|elderly|retired', "65+")
        ]

        age_bands = []
        for pattern, band in age_patterns:
            if re.search(pattern, prompt_lower):
                age_bands.append(band)

        if age_bands:
            filters["age_band"] = age_bands

        # Income bands
        income_keywords = {
            "high income": ["High", "Very High"],
            "low income": ["Low"],
            "medium income": ["Medium"],
            "wealthy": ["High", "Very High"],
            "affluent": ["High", "Very High"],
            "budget": ["Low", "Medium-Low"]
        }

        for keyword, bands in income_keywords.items():
            if keyword in prompt_lower:
                filters["income_band"] = bands
                break

        # Country - use word boundaries to avoid false matches
        country_patterns = [
            (r'\bthe\s+us\b|\bus\b|\busa\b|\bunited\s+states\b|\bamerica\b', "US"),
            (r'\bthe\s+uk\b|\buk\b|\bbritain\b|\bengland\b|\bunited\s+kingdom\b', "GB"),
            (r'\bcanada\b|\bcanadian\b', "CA"),
            (r'\baustralia\b|\baustralian\b', "AU"),
            (r'\bgermany\b|\bgerman\b', "DE"),
            (r'\bfrance\b|\bfrench\b', "FR"),
            (r'\bspain\b|\bspanish\b', "ES"),
            (r'\bitaly\b|\bitalian\b', "IT")
        ]

        for pattern, code in country_patterns:
            if re.search(pattern, prompt_lower):
                filters["user_ccode2"] = [code]
                break

        return filters

    def _extract_geographic_filters(self, prompt_lower: str, original: str) -> Dict[str, Any]:
        """Extract geographic filters from prompt"""
        filters = {}

        # Extract radius if specified
        radius_match = re.search(r'within (\d+)\s?(km|kilometers?|miles?)', prompt_lower)
        if radius_match:
            radius = int(radius_match.group(1))
            unit = radius_match.group(2)
            if 'mile' in unit:
                radius = int(radius * 1.60934)  # Convert miles to km
            filters["radius_km"] = radius

        # Extract state/region (L1)
        state_match = re.search(r'(?:in|from) ([A-Z]{2}|[A-Z][a-z]+(?:\s[A-Z][a-z]+)?)', original)
        if state_match:
            filters["user_l1_geo"] = [state_match.group(1)]

        return filters

    def _extract_spending_filters(self, prompt_lower: str, original: str) -> Dict[str, Any]:
        """Extract spending behavior filters from prompt"""
        filters = {}

        # Extract minimum spend
        min_spend_match = re.search(r'spend(?:ing)? (?:at least|more than|over|above) \$?(\d+(?:,\d{3})*(?:\.\d{2})?)', prompt_lower)
        if min_spend_match:
            filters["min_total_spend"] = float(min_spend_match.group(1).replace(',', ''))

        # Extract maximum spend
        max_spend_match = re.search(r'spend(?:ing)? (?:less than|under|below) \$?(\d+(?:,\d{3})*(?:\.\d{2})?)', prompt_lower)
        if max_spend_match:
            filters["max_total_spend"] = float(max_spend_match.group(1).replace(',', ''))

        # Extract minimum transactions
        min_tx_match = re.search(r'(?:at least|more than|over) (\d+) transactions?', prompt_lower)
        if min_tx_match:
            filters["min_transactions"] = int(min_tx_match.group(1))

        return filters

    def _get_clarifying_questions(self, audience_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate clarifying questions for missing or ambiguous filters
        Only returns REQUIRED questions that block query generation"""
        questions = []

        audience_type = audience_info["type"]
        filters = audience_info["filters"]

        # Required questions based on audience type
        if audience_type == "vendor" and not filters.get("vendor_desc"):
            questions.append({
                "key": "vendor_desc",
                "question": "Which vendor/store would you like to target? (e.g., Walmart, Amazon, Starbucks)",
                "type": "text",
                "required": True
            })

        if audience_type == "grocer" and not filters.get("grocer_desc"):
            questions.append({
                "key": "grocer_desc",
                "question": f"Which grocer would you like to target?",
                "type": "choice",
                "options": COMMON_GROCERS,
                "required": True
            })

        if audience_type == "merchant_category" and not filters.get("merch_desc"):
            questions.append({
                "key": "merch_desc",
                "question": "Which merchant category would you like to target?",
                "type": "choice",
                "options": COMMON_MERCHANTS,
                "required": True
            })

        # Only ask for country if not specified and needed for certain audience types
        if not filters.get("user_ccode2") and audience_type in ["demographic", "geographic"]:
            questions.append({
                "key": "user_ccode2",
                "question": "Which country would you like to target?",
                "type": "choice",
                "options": VALID_FILTERS["user_ccode2"],
                "required": True
            })

        return questions

    def _build_query_from_info(self, audience_info: Dict[str, Any]) -> str:
        """Build SQL query from audience information"""
        audience_type = audience_info["type"]
        filters = audience_info["filters"]

        query_method_map = {
            "demographic": self.query_builder.build_demographic_audience,
            "vendor": self.query_builder.build_vendor_audience,
            "merchant_category": self.query_builder.build_merchant_category_audience,
            "geographic": self.query_builder.build_geographic_audience,
            "grocer": self.query_builder.build_grocer_audience,
            "lookalike": self.query_builder.build_lookalike_audience,
            "spending_behavior": self.query_builder.build_spending_behavior_audience
        }

        build_method = query_method_map.get(audience_type)
        if not build_method:
            raise ValueError(f"Unknown audience type: {audience_type}")

        return build_method(filters)

    def apply_user_answers(self, answers: Dict[str, Any]) -> None:
        """Apply user answers to pending filters"""
        self.pending_filters.update(answers)

    def format_response(self, result: Dict[str, Any]) -> str:
        """Format the response for display"""
        if result["status"] == "needs_clarification":
            output = [f"\n{result['message']}\n"]
            for i, q in enumerate(result["questions"], 1):
                output.append(f"{i}. {q['question']}")
                if q["type"] in ["choice", "choice_optional", "choice_optional_multiple"]:
                    output.append(f"   Options: {', '.join(q['options'])}")
            return "\n".join(output)

        elif result["status"] == "success":
            output = [
                f"\n✓ {result['message']}",
                f"\nAudience Type: {result['audience_type']}",
                f"\nApplied Filters:",
            ]
            for key, value in result["filters"].items():
                output.append(f"  - {key}: {value}")

            output.extend([
                f"\n--- AUDIENCE QUERY ---",
                result["query"],
                f"\n--- COUNT QUERY ---",
                result["count_query"],
                f"\n--- EXPORT QUERY (with demographics) ---",
                result["export_query"]
            ])
            return "\n".join(output)

        else:  # error
            return f"\n✗ {result['message']}"


def main():
    """Example usage"""
    agent = AudienceAgent(
        project_id="your-project-id",
        dataset="skyrise",
        release_id=1
    )

    # Example prompts
    example_prompts = [
        "Find all female shoppers aged 25-34 who shop at Walmart in the US",
        "Get me high income males who buy at coffee shops",
        "Show me customers in California who spend more than $1000",
        "Find shoppers at Tesco grocery stores in the UK",
        "Get users in the restaurant category"
    ]

    print("=" * 80)
    print("SKYRISE AUDIENCE GENERATION AGENT")
    print("=" * 80)

    for prompt in example_prompts:
        print(f"\n\nUser Prompt: {prompt}")
        print("-" * 80)
        result = agent.process_prompt(prompt)
        print(agent.format_response(result))


if __name__ == "__main__":
    main()

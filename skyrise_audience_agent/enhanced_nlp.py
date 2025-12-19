"""
Enhanced NLP Parser - Understands complex audience requests
Handles multiple vendors, age comparisons, automatic joins, personas
"""

import re
from typing import Dict, List, Any, Optional, Tuple


class EnhancedNLPParser:
    """
    Advanced natural language parser for audience requests
    """

    def __init__(self):
        self.vendor_keywords = [
            "walmart", "tesco", "sainsbury", "aldi", "lidl", "asda",
            "ikea", "amazon", "starbucks", "costa", "pret",
            "morrisons", "waitrose", "marks & spencer", "m&s"
        ]

    def parse_complex_request(self, prompt: str) -> Dict[str, Any]:
        """
        Parse complex audience requests with multiple conditions

        Returns:
            {
                "vendors": ["Tesco", "IKEA"],
                "age_filters": {"max": 50},
                "demographics": {"gender": "Female"},
                "location": {"country": "GB"},
                "combine_logic": "AND",
                "complexity": "multi_vendor_with_filters"
            }
        """
        prompt_lower = prompt.lower()
        parsed = {
            "vendors": [],
            "age_filters": {},
            "demographics": {},
            "location": {},
            "spending": {},
            "combine_logic": "AND",
            "complexity": "simple"
        }

        # 1. Extract multiple vendors
        vendors = self._extract_multiple_vendors(prompt_lower, prompt)
        if vendors:
            parsed["vendors"] = vendors
            if len(vendors) > 1:
                parsed["complexity"] = "multi_vendor"

        # 2. Extract age comparisons (under 50, over 30, between 25-35)
        age_filters = self._extract_age_comparisons(prompt_lower)
        if age_filters:
            parsed["age_filters"] = age_filters
            parsed["complexity"] = "multi_vendor_with_filters" if vendors else "filtered"

        # 3. Extract demographics
        demographics = self._extract_demographics(prompt_lower)
        if demographics:
            parsed["demographics"] = demographics

        # 4. Extract location
        location = self._extract_location(prompt_lower)
        if location:
            parsed["location"] = location

        # 5. Detect combine logic (AND vs OR)
        if " and " in prompt_lower or " & " in prompt_lower:
            parsed["combine_logic"] = "AND"
        elif " or " in prompt_lower:
            parsed["combine_logic"] = "OR"

        return parsed

    def _extract_multiple_vendors(self, prompt_lower: str, original: str) -> List[str]:
        """Extract all mentioned vendors from prompt"""
        found_vendors = []
        found_names = set()  # Track found names to avoid duplicates

        # Check for common vendors with word boundaries
        for vendor in self.vendor_keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(vendor) + r'\b'
            if re.search(pattern, prompt_lower):
                if vendor not in found_names:
                    found_vendors.append(vendor.title())
                    found_names.add(vendor)

        return found_vendors

    def _extract_age_comparisons(self, prompt_lower: str) -> Dict[str, Any]:
        """Extract age comparisons (under X, over Y, between X-Y)"""
        age_filters = {}

        # Under X
        under_match = re.search(r'under\s+(\d+)', prompt_lower)
        if under_match:
            max_age = int(under_match.group(1))
            age_filters["max"] = max_age
            age_filters["bands"] = self._age_to_bands(None, max_age)

        # Over X
        over_match = re.search(r'over\s+(\d+)', prompt_lower)
        if over_match:
            min_age = int(over_match.group(1))
            age_filters["min"] = min_age
            age_filters["bands"] = self._age_to_bands(min_age, None)

        # Between X and Y
        between_match = re.search(r'between\s+(\d+)\s+and\s+(\d+)', prompt_lower)
        if between_match:
            min_age = int(between_match.group(1))
            max_age = int(between_match.group(2))
            age_filters["min"] = min_age
            age_filters["max"] = max_age
            age_filters["bands"] = self._age_to_bands(min_age, max_age)

        # Aged X-Y
        aged_match = re.search(r'aged?\s+(\d+)[-\s](\d+)', prompt_lower)
        if aged_match:
            min_age = int(aged_match.group(1))
            max_age = int(aged_match.group(2))
            age_filters["min"] = min_age
            age_filters["max"] = max_age
            age_filters["bands"] = self._age_to_bands(min_age, max_age)

        return age_filters

    def _age_to_bands(self, min_age: Optional[int], max_age: Optional[int]) -> List[str]:
        """Convert age range to standard age bands"""
        all_bands = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        band_ranges = {
            "18-24": (18, 24),
            "25-34": (25, 34),
            "35-44": (35, 44),
            "45-54": (45, 54),
            "55-64": (55, 64),
            "65+": (65, 100)
        }

        matching_bands = []
        for band, (band_min, band_max) in band_ranges.items():
            # Check if band overlaps with requested range
            if min_age is None:
                min_age = 0
            if max_age is None:
                max_age = 100

            if band_max >= min_age and band_min <= max_age:
                matching_bands.append(band)

        return matching_bands

    def _extract_demographics(self, prompt_lower: str) -> Dict[str, Any]:
        """Extract demographic filters"""
        demographics = {}

        # Gender
        if "female" in prompt_lower or "women" in prompt_lower:
            demographics["gender"] = "Female"
        elif re.search(r'\bmale\b|\bmen\b', prompt_lower):
            demographics["gender"] = "Male"

        # Income
        income_keywords = {
            "high income": "High",
            "low income": "Low",
            "medium income": "Medium",
            "wealthy": "High",
            "affluent": "High",
            "budget": "Low"
        }

        for keyword, band in income_keywords.items():
            if keyword in prompt_lower:
                demographics["income"] = band
                break

        return demographics

    def _extract_location(self, prompt_lower: str) -> Dict[str, str]:
        """Extract location filters"""
        location = {}

        # Country codes
        country_patterns = [
            (r'\buk\b|\bbritain\b|\bengland\b', "GB"),
            (r'\bus\b|\busa\b|\bunited states\b|\bamerica\b', "US"),
            (r'\bcanada\b', "CA"),
            (r'\baustralia\b', "AU"),
        ]

        for pattern, code in country_patterns:
            if re.search(pattern, prompt_lower):
                location["country"] = code
                break

        # Specific locations
        if "based in" in prompt_lower or "in the" in prompt_lower or "from" in prompt_lower:
            # Already handled by country patterns
            pass

        return location

    def build_query_from_parsed(self, parsed: Dict[str, Any], query_builder) -> Dict[str, Any]:
        """
        Build query from parsed complex request

        Returns query info with automatic combining if needed
        """
        if parsed["complexity"] == "simple":
            return None  # Use standard flow

        # Multi-vendor case
        if len(parsed["vendors"]) > 1:
            queries = []

            for vendor in parsed["vendors"]:
                # Build individual vendor query
                filters = {"vendor_desc": vendor}

                # Add location if specified
                if parsed["location"].get("country"):
                    filters["user_ccode2"] = [parsed["location"]["country"]]

                query = query_builder.build_vendor_audience(filters)
                queries.append(query)

            # Combine based on logic
            if parsed["combine_logic"] == "AND":
                combined = query_builder.build_combined_audience(queries, "INTERSECT")
            else:
                combined = query_builder.build_combined_audience(queries, "UNION")

            # Add demographic filters if needed
            if parsed["age_filters"].get("bands"):
                combined = query_builder.add_demographic_refinement(combined, {
                    "age_band": parsed["age_filters"]["bands"]
                })

            if parsed["demographics"].get("gender"):
                combined = query_builder.add_demographic_refinement(combined, {
                    "gender_description": [parsed["demographics"]["gender"]]
                })

            return {
                "query": combined,
                "vendors": parsed["vendors"],
                "combine_logic": parsed["combine_logic"],
                "filters": parsed
            }

        return None

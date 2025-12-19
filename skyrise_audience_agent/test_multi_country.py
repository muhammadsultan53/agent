#!/usr/bin/env python3
"""
Test multi-country parsing in EnhancedNLPParser
"""

from enhanced_nlp import EnhancedNLPParser

def test_multi_country():
    parser = EnhancedNLPParser()

    # Test 1: Single country
    print("Test 1: Single country")
    result = parser.parse_complex_request("Find users in UK")
    print(f"  Location: {result['location']}")
    assert result['location']['country'] == 'GB'
    print("  ✓ PASS\n")

    # Test 2: Multi-country
    print("Test 2: Multi-country (UK and IT)")
    result = parser.parse_complex_request("Find users in UK and IT")
    print(f"  Location: {result['location']}")
    assert result['location']['multi_country'] == True
    assert 'GB' in result['location']['countries']
    assert 'IT' in result['location']['countries']
    print("  ✓ PASS\n")

    # Test 3: Multi-country with vendors
    print("Test 3: Multi-country with vendors (Tesco shoppers in US or Canada)")
    result = parser.parse_complex_request("Find Tesco shoppers in US or Canada")
    print(f"  Vendors: {result['vendors']}")
    print(f"  Location: {result['location']}")
    print(f"  Combine Logic: {result['combine_logic']}")
    assert 'Tesco' in result['vendors']
    assert result['location']['multi_country'] == True
    assert 'US' in result['location']['countries']
    assert 'CA' in result['location']['countries']
    print("  ✓ PASS\n")

    # Test 4: Multi-vendor + multi-country
    print("Test 4: Multi-vendor + multi-country (IKEA and Tesco in UK and Germany)")
    result = parser.parse_complex_request("Find IKEA and Tesco shoppers in UK and Germany")
    print(f"  Vendors: {result['vendors']}")
    print(f"  Location: {result['location']}")
    print(f"  Complexity: {result['complexity']}")
    assert 'Ikea' in result['vendors']
    assert 'Tesco' in result['vendors']
    assert result['location']['multi_country'] == True
    assert 'GB' in result['location']['countries']
    assert 'DE' in result['location']['countries']
    assert result['combine_logic'] == 'AND'
    print("  ✓ PASS\n")

    # Test 5: Multi-country alternative patterns
    print("Test 5: Alternative country names (Britain and Italy)")
    result = parser.parse_complex_request("Find users in Britain and Italy")
    print(f"  Location: {result['location']}")
    assert 'GB' in result['location']['countries']
    assert 'IT' in result['location']['countries']
    print("  ✓ PASS\n")

    print("=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)

if __name__ == "__main__":
    test_multi_country()

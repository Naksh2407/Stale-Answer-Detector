"""Extractor tests for Stale-Answer Detector - offline using saved LLM responses."""
import sys, json
sys.path.insert(0, ".")
from app.extractor import extract_claims, _parse_json_array

def test_parse_json_array():
    # Test basic parsing
    result = _parse_json_array('[{"text": "test claim", "type": "pricing", "subject": "test"}]')
    assert len(result) == 1
    assert result[0]["text"] == "test claim"

    # Test multiline/whitespace handling
    result = _parse_json_array('```json\n[{"text": "claim", "type": "api_version"}]\n```')
    assert len(result) == 1
    assert result[0]["type"] == "api_version"

def test_extractor_with_mock():
    # When extract_claims is called with a mock setup, it should parse claims
    # This test just verifies the parsing function works independently
    answer = "The Pro plan costs $20 per month."
    items = _parse_json_array('[{"text": "The Pro plan costs $20 per month.", "type": "pricing", "subject": "Pro plan"}]')
    assert len(items) == 1
    assert items[0]["type"] == "pricing"

if __name__ == "__main__":
    test_parse_json_array()
    test_extractor_with_mock()
    print("All extractor tests passed!")
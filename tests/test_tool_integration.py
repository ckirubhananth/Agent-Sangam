"""
Test script to verify tool integration is working correctly.

Run this after starting the server:
    python tests/test_tool_integration.py
"""

import httpx
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://127.0.0.1:8000"

def test_tool_registry():
    """Test that tool registry endpoint works."""
    logger.info("=" * 60)
    logger.info("TEST 1: Tool Registry Discovery")
    logger.info("=" * 60)
    
    try:
        response = httpx.get(f"{BASE_URL}/tools/registry")
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"✅ Tool Registry accessible")
        logger.info(f"   Total tools: {data['total_tools']}")
        logger.info(f"   Tools: {data['tools']}")
        
        assert data['total_tools'] == 4, f"Expected 4 tools, got {data['total_tools']}"
        assert 'pdf_search' in data['tools'], "pdf_search tool not found"
        assert 'extract_entities' in data['tools'], "extract_entities tool not found"
        assert 'pdf_summary' in data['tools'], "pdf_summary tool not found"
        assert 'retrieve_context' in data['tools'], "retrieve_context tool not found"
        
        logger.info("✅ All 4 tools registered correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ Tool registry test failed: {e}")
        return False


def test_tool_metadata():
    """Test that individual tool metadata is accessible."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Tool Metadata")
    logger.info("=" * 60)
    
    tools = ['pdf_search', 'extract_entities', 'pdf_summary', 'retrieve_context']
    all_passed = True
    
    for tool_name in tools:
        try:
            response = httpx.get(f"{BASE_URL}/tools/{tool_name}")
            response.raise_for_status()
            
            data = response.json()
            assert data['name'] == tool_name, f"Tool name mismatch: {data['name']} != {tool_name}"
            assert 'metadata' in data, "metadata field missing"
            assert 'description' in data['metadata'], f"description missing for {tool_name}"
            
            logger.info(f"✅ {tool_name}: {data['metadata']['description'][:60]}...")
            
        except Exception as e:
            logger.error(f"❌ Failed to get metadata for {tool_name}: {e}")
            all_passed = False
    
    return all_passed


def test_tool_schema():
    """Test that OpenAPI schema is generated correctly."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: OpenAPI Schema Generation")
    logger.info("=" * 60)
    
    try:
        response = httpx.get(f"{BASE_URL}/tools/registry")
        response.raise_for_status()
        
        data = response.json()
        schema = data['schema']
        
        assert 'tools' in schema, "schema.tools missing"
        assert schema['total'] == 4, f"Expected 4 tools in schema, got {schema['total']}"
        
        logger.info(f"✅ OpenAPI schema generated with {schema['total']} tools")
        
        # Check each tool has required schema fields
        for tool_name, tool_schema in schema['tools'].items():
            assert 'description' in tool_schema, f"{tool_name} missing description"
            assert 'parameters' in tool_schema, f"{tool_name} missing parameters"
            logger.info(f"   - {tool_name}: {tool_schema['description'][:50]}...")
        
        logger.info("✅ All tools have proper schema")
        return True
        
    except Exception as e:
        logger.error(f"❌ OpenAPI schema test failed: {e}")
        return False


def test_tool_parameters():
    """Test that tool parameters are properly defined."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Tool Parameters Validation")
    logger.info("=" * 60)
    
    try:
        response = httpx.get(f"{BASE_URL}/tools/registry")
        response.raise_for_status()
        
        metadata = response.json()['metadata']
        
        # pdf_search should have pdf_session_id and query
        pdf_search = metadata['pdf_search']
        assert 'pdf_session_id' in pdf_search['parameters']['properties'], \
            "pdf_search missing pdf_session_id parameter"
        assert 'query' in pdf_search['parameters']['properties'], \
            "pdf_search missing query parameter"
        logger.info("✅ pdf_search has correct parameters")
        
        # extract_entities should have pdf_session_id
        extract_ent = metadata['extract_entities']
        assert 'pdf_session_id' in extract_ent['parameters']['properties'], \
            "extract_entities missing pdf_session_id parameter"
        logger.info("✅ extract_entities has correct parameters")
        
        # retrieve_context should have pdf_session_id and question
        retrieve = metadata['retrieve_context']
        assert 'pdf_session_id' in retrieve['parameters']['properties'], \
            "retrieve_context missing pdf_session_id parameter"
        assert 'question' in retrieve['parameters']['properties'], \
            "retrieve_context missing question parameter"
        logger.info("✅ retrieve_context has correct parameters")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Tool parameters validation failed: {e}")
        return False


def test_server_status():
    """Test that server is running and responsive."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 0: Server Status")
    logger.info("=" * 60)
    
    try:
        response = httpx.get(f"{BASE_URL}/")
        response.raise_for_status()
        logger.info(f"✅ Server is running: {response.json()['message']}")
        return True
    except Exception as e:
        logger.error(f"❌ Server not running or not responding: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 70)
    logger.info("AGENT SANGAM - TOOL INTEGRATION TEST SUITE")
    logger.info("=" * 70)
    
    results = {}
    
    # Check server first
    if not test_server_status():
        logger.error("\n❌ Server is not running. Start it with: ./start_server.ps1")
        return False
    
    # Run all tests
    results['Tool Registry'] = test_tool_registry()
    results['Tool Metadata'] = test_tool_metadata()
    results['OpenAPI Schema'] = test_tool_schema()
    results['Tool Parameters'] = test_tool_parameters()
    
    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✅ PASS" if passed_flag else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("=" * 70)
    logger.info(f"Result: {passed}/{total} tests passed")
    logger.info("=" * 70)
    
    if passed == total:
        logger.info("\n🎉 All tests passed! Tool integration is working correctly.")
        return True
    else:
        logger.error(f"\n❌ {total - passed} test(s) failed. See above for details.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

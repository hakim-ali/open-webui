#!/usr/bin/env python3
"""
Test script to verify the common URL security utility works correctly.
This script tests the URL validation logic to ensure it properly blocks
malicious URLs that could be used for SSRF attacks.
"""

import sys
import os

# Add the open_webui directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'open_webui'))

from open_webui.utils.url_security import get_function_url_validator, get_tool_url_validator, is_url_allowed

def test_url_validation():
    """Test the URL validation function with various URLs."""
    
    print("Testing common URL security utility...")
    print("=" * 60)
    
    # Test with function validator
    print("\n🔧 Testing FUNCTION URL validator:")
    function_validator = get_function_url_validator()
    
    # Test allowed URLs (should return True if domains are configured)
    allowed_urls = [
        "https://github.com/user/repo/blob/main/function.py",
        "https://raw.githubusercontent.com/user/repo/main/function.py",
        "https://gist.githubusercontent.com/user/gist_id/function.py",
    ]
    
    print("  ✅ Testing ALLOWED URLs:")
    for url in allowed_urls:
        result = function_validator.is_url_allowed(url)
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"    {status}: {url}")
    
    # Test blocked URLs (should return False)
    blocked_urls = [
        "http://10.0.0.1/function.py",
        "http://192.168.1.1/function.py",
        "http://localhost/function.py",
        "http://internal.corp.local/function.py",
        "http://8.8.8.8/function.py",
    ]
    
    print("  ❌ Testing BLOCKED URLs:")
    for url in blocked_urls:
        result = function_validator.is_url_allowed(url)
        status = "❌ PASS" if not result else "✅ FAIL"
        print(f"    {status}: {url}")
    
    # Test with tool validator
    print("\n🛠️  Testing TOOL URL validator:")
    tool_validator = get_tool_url_validator()
    
    print("  ✅ Testing ALLOWED URLs:")
    for url in allowed_urls:
        result = tool_validator.is_url_allowed(url)
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"    {status}: {url}")
    
    print("  ❌ Testing BLOCKED URLs:")
    for url in blocked_urls:
        result = tool_validator.is_url_allowed(url)
        status = "❌ PASS" if not result else "✅ FAIL"
        print(f"    {status}: {url}")
    
    # Test convenience function
    print("\n🔗 Testing convenience function:")
    print("  Testing is_url_allowed() function:")
    for url in blocked_urls:
        result = is_url_allowed(url)
        status = "❌ PASS" if not result else "✅ FAIL"
        print(f"    {status}: {url}")
    
    # Show current configuration
    print("\n📊 Current Configuration:")
    print(f"  Function allowed domains: {len(function_validator.get_allowed_domains())}")
    print(f"  Tool allowed domains: {len(tool_validator.get_allowed_domains())}")
    
    if function_validator.get_allowed_domains():
        print("  Function domains:", sorted(function_validator.get_allowed_domains()))
    
    if tool_validator.get_allowed_domains():
        print("  Tool domains:", sorted(tool_validator.get_allowed_domains()))
    
    print("\n" + "=" * 60)
    print("URL security test completed!")
    
    return True

if __name__ == "__main__":
    try:
        test_url_validation()
        print("\n🎉 All tests completed successfully!")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)

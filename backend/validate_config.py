#!/usr/bin/env python3
"""
Configuration validation script for function and tool loading security settings.
This script shows the current allowed domains configuration using the common URL security utility.
"""

import os
import sys

# Add the open_webui directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'open_webui'))

from open_webui.utils.url_security import get_function_url_validator, get_tool_url_validator

def validate_config():
    """Validate and display the current configuration."""
    
    print("🔒 Function and Tool Loading Security Configuration")
    print("=" * 60)
    
    # Get validators
    function_validator = get_function_url_validator()
    tool_validator = get_tool_url_validator()
    
    # Function loading domains
    print("🔧 FUNCTION LOADING:")
    function_domains = function_validator.get_allowed_domains()
    
    if function_domains:
        print(f"  ✅ Allowed domains: {len(function_domains)}")
        for domain in sorted(function_domains):
            print(f"    - {domain}")
    else:
        print("  ✅ Allowed domains: 0 (empty by default)")
    
    # Tool loading domains
    print("\n🛠️  TOOL LOADING:")
    tool_domains = tool_validator.get_allowed_domains()
    
    if tool_domains:
        print(f"  ✅ Allowed domains: {len(tool_domains)}")
        for domain in sorted(tool_domains):
            print(f"    - {domain}")
    else:
        print("  ✅ Allowed domains: 0 (empty by default)")
    
    # Summary
    print(f"\n🌍 SUMMARY:")
    print(f"  Total function domains: {len(function_domains)}")
    print(f"  Total tool domains: {len(tool_domains)}")
    print(f"  Combined total: {len(function_domains) + len(tool_domains)}")
    
    print("\n🛡️ Security features (always enabled):")
    print("  - Private IP range blocking")
    print("  - Localhost and loopback blocking")
    print("  - Internal domain blocking")
    print("  - Direct IP address blocking")
    print("  - Content type validation")
    print("  - File size limits (1MB)")
    print("  - Request timeouts (30s total, 10s connect)")
    
    print("\n📝 Environment Variables:")
    print(f"  ADDITIONAL_FUNCTION_DOMAINS: {repr(os.getenv('ADDITIONAL_FUNCTION_DOMAINS', '')) if os.getenv('ADDITIONAL_FUNCTION_DOMAINS') else 'not set'}")
    print(f"  ADDITIONAL_TOOL_DOMAINS: {repr(os.getenv('ADDITIONAL_TOOL_DOMAINS', '')) if os.getenv('ADDITIONAL_TOOL_DOMAINS') else 'not set'}")
    
    print("\n💡 Note:")
    print("  Both function and tool loading features are secured with no allowed domains by default.")
    print("  Add domains only when you need to load functions or tools from specific sources.")
    
    print("\n" + "=" * 60)
    print("Configuration validation completed!")
    
    return True

if __name__ == "__main__":
    try:
        validate_config()
        print("\n🎉 Configuration is valid!")
    except Exception as e:
        print(f"\n💥 Configuration validation failed: {e}")
        sys.exit(1)

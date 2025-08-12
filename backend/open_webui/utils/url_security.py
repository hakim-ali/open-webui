"""
URL Security Utilities for preventing SSRF attacks.
This module provides common URL validation functions used by both
function and tool loading endpoints.
"""

import os
import re
import logging
from urllib.parse import urlparse
from typing import Set

log = logging.getLogger(__name__)


class URLSecurityValidator:
    """URL security validator to prevent SSRF attacks."""
    
    def __init__(self, allowed_domains: Set[str] = None):
        """
        Initialize the URL validator.
        
        Args:
            allowed_domains: Set of allowed domains. If None, uses environment variable.
        """
        if allowed_domains is None:
            self.allowed_domains = set()
        else:
            self.allowed_domains = allowed_domains.copy()
    
    def add_domains_from_env(self, env_var_name: str) -> None:
        """
        Add domains from environment variable.
        
        Args:
            env_var_name: Name of environment variable containing comma-separated domains
        """
        env_domains = os.getenv(env_var_name, "")
        if env_domains:
            additional_domains = {domain.strip().lower() for domain in env_domains.split(",") if domain.strip()}
            self.allowed_domains.update(additional_domains)
            log.info(f"Added {len(additional_domains)} domains from {env_var_name}: {additional_domains}")
    
    def is_url_allowed(self, url: str) -> bool:
        """
        Validate if the URL is allowed based on the strict allow-list.
        This prevents SSRF attacks by only permitting connections to approved domains.
        
        Args:
            url: The URL to validate
            
        Returns:
            bool: True if the URL is allowed, False otherwise
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove port number if present
            if ':' in domain:
                domain = domain.split(':')[0]
            
            # Check if the domain is in our allow-list
            if domain in self.allowed_domains:
                return True
                
            # Block private IP ranges
            if domain.startswith(('10.', '172.16.', '172.17.', '172.18.', '172.19.', 
                                 '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
                                 '172.25.', '172.26.', '172.27.', '172.28.', '172.29.',
                                 '172.30.', '172.31.', '192.168.', '127.', '169.254.')):
                log.warning(f"Blocked private IP range access attempt: {domain}")
                return False
                
            # Block localhost and loopback
            if domain in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
                log.warning(f"Blocked localhost/loopback access attempt: {domain}")
                return False
                
            # Block internal/private domains
            if domain.endswith(('.local', '.internal', '.home', '.lan', '.corp', '.localdomain')):
                log.warning(f"Blocked internal domain access attempt: {domain}")
                return False
            
            # Block any IP address that's not in our allow-list
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain):
                log.warning(f"Blocked direct IP access attempt: {domain}")
                return False
                
            # Log blocked domains for security monitoring
            log.warning(f"Blocked unauthorized domain access attempt: {domain}")
            return False
            
        except Exception as e:
            log.warning(f"Error parsing URL {url}: {e}")
            return False
    
    def get_allowed_domains(self) -> Set[str]:
        """Get the current set of allowed domains."""
        return self.allowed_domains.copy()
    
    def add_domain(self, domain: str) -> None:
        """Add a single domain to the allowed list."""
        self.allowed_domains.add(domain.lower())
    
    def remove_domain(self, domain: str) -> None:
        """Remove a domain from the allowed list."""
        self.allowed_domains.discard(domain.lower())


# Pre-configured validators for common use cases
def get_function_url_validator() -> URLSecurityValidator:
    """Get a URL validator configured for function loading."""
    validator = URLSecurityValidator()
    validator.add_domains_from_env("ADDITIONAL_FUNCTION_DOMAINS")
    return validator


def get_tool_url_validator() -> URLSecurityValidator:
    """Get a URL validator configured for tool loading."""
    validator = URLSecurityValidator()
    validator.add_domains_from_env("ADDITIONAL_TOOL_DOMAINS")
    return validator


# Convenience function for backward compatibility
def is_url_allowed(url: str, allowed_domains: Set[str] = None) -> bool:
    """
    Convenience function to check if a URL is allowed.
    
    Args:
        url: The URL to validate
        allowed_domains: Set of allowed domains. If None, uses function domains.
        
    Returns:
        bool: True if the URL is allowed, False otherwise
    """
    if allowed_domains is None:
        validator = get_function_url_validator()
    else:
        validator = URLSecurityValidator(allowed_domains)
    
    return validator.is_url_allowed(url)

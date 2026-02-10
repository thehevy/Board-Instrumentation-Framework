#!/usr/bin/env python3
"""
Quick test script to verify PyPI connectivity check functionality.
Run this to see what the proxy check will report in your environment.
"""

from biff_agents_core.utils.environment_validator import EnvironmentValidator

def main():
    print("="*60)
    print("PyPI Connectivity Test")
    print("="*60)
    print()
    
    validator = EnvironmentValidator()
    
    print("Testing PyPI access...")
    print()
    
    result = validator.check_pypi_access()
    
    print("-"*60)
    print("Results:")
    print("-"*60)
    print(f"PyPI Accessible: {result['accessible']}")
    print(f"HTTPS Works: {result['https_works']}")
    print(f"Proxy Configured: {result['proxy_configured']}")
    
    if result['proxy_env_vars']:
        print("\nProxy Environment Variables:")
        for var, value in result['proxy_env_vars'].items():
            print(f"  {var} = {value}")
    
    if result['error']:
        print(f"\nError: {result['error']}")
    
    print()
    print("-"*60)
    print("Validator Messages:")
    print("-"*60)
    
    if validator.info:
        print("\nInfo:")
        for msg in validator.info:
            print(f"  {msg}")
    
    if validator.warnings:
        print("\nWarnings:")
        for msg in validator.warnings:
            print(f"  {msg}")
    
    if validator.issues:
        print("\nIssues:")
        for msg in validator.issues:
            print(f"  {msg}")
    
    print()
    print("="*60)

if __name__ == "__main__":
    main()

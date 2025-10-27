#!/usr/bin/env python3
"""
Test script for outbound call functionality
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_outbound_call(phone_number):
    """
    Test making an outbound call
    
    Args:
        phone_number (str): The phone number to call
    """
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    
    # Prepare the request
    url = f"{base_url}/make-call"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'to_number': phone_number
    }
    
    print(f"Making outbound call to {phone_number}...")
    print(f"Request URL: {url}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Call initiated successfully!")
            print(f"Call SID: {result.get('sid')}")
            print(f"Call Status: {result.get('status')}")
            print(f"To: {result.get('to')}")
            print(f"From: {result.get('from')}")
            
            # Test getting call status
            test_call_status(result.get('sid'), base_url)
            
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        print(f"Raw response: {response.text}")

def test_call_status(call_sid, base_url):
    """
    Test getting call status
    
    Args:
        call_sid (str): The call SID to check
        base_url (str): The base URL of the application
    """
    print(f"\nChecking call status for SID: {call_sid}")
    
    try:
        response = requests.get(f"{base_url}/call-status/{call_sid}")
        
        if response.status_code == 200:
            status = response.json()
            print(f"Call Status: {status}")
        else:
            print(f"Error getting call status: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def main():
    """Main function"""
    print("=== Outbound Call Test Script ===")
    print()
    
    # Check environment variables
    required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_NUMBER']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        return
    
    print("Environment variables check: ✓")
    print(f"Twilio Number: {os.getenv('TWILIO_NUMBER')}")
    print()
    
    # Get phone number from user
    phone_number = input("Enter the phone number to call (with country code, e.g., +1234567890): ").strip()
    
    if not phone_number:
        print("No phone number provided. Exiting.")
        return
    
    # Validate phone number format (basic check)
    if not phone_number.startswith('+'):
        print("Warning: Phone number should start with '+' and include country code")
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            return
    
    print()
    test_outbound_call(phone_number)

if __name__ == "__main__":
    main()


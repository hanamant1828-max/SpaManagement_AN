#!/usr/bin/env python3
import os
import sys
import requests
import json

if not os.environ.get("SESSION_SECRET"):
    os.environ["SESSION_SECRET"] = "1578063aca108928c78100b516702a5765d2d05e85b4fb8bb29a75db0bfc34ca"

from app import app

def test_create_student_offer():
    """Test creating a student offer called 'hanamanrt 30'"""
    
    with app.test_client() as client:
        login_response = client.post('/api/login', 
            data=json.dumps({'identifier': 'admin', 'password': 'admin'}),
            content_type='application/json')
        
        print(f"Login response: {login_response.status_code}")
        
        student_offer_data = {
            'service_ids': [1, 2, 3],
            'discount_percentage': 30,
            'valid_from': '2025-10-06',
            'valid_to': '2026-04-06',
            'valid_days': 'Mon-Fri',
            'conditions': 'hanamanrt 30 - Valid with Student ID only',
            'is_active': True
        }
        
        response = client.post('/packages/api/student-offers',
            data=json.dumps(student_offer_data),
            content_type='application/json')
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response body: {response.get_data(as_text=True)}")
        
        if response.status_code == 200:
            result = response.get_json()
            if result.get('success'):
                print("\n✅ Student offer created successfully!")
                print(f"Offer ID: {result.get('offer_id')}")
            else:
                print(f"\n❌ Error: {result.get('error')}")
        else:
            print(f"\n❌ HTTP Error {response.status_code}")
            print(response.get_data(as_text=True))

if __name__ == "__main__":
    with app.app_context():
        test_create_student_offer()

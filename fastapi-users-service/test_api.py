#!/usr/bin/env python3
"""
Simple test script to demonstrate the FastAPI Users Service functionality.
Run this after starting the server to test the API endpoints.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get("http://localhost:8000/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_create_user():
    """Test creating a user"""
    print("Testing user creation...")
    
    user_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        return response.json()["id"]
    return None

def test_get_users():
    """Test getting all users"""
    print("Testing get all users...")
    response = requests.get(f"{BASE_URL}/users/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_get_user(user_id):
    """Test getting a specific user"""
    print(f"Testing get user {user_id}...")
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_update_user(user_id):
    """Test updating a user"""
    print(f"Testing update user {user_id}...")
    
    update_data = {
        "name": "John Updated",
        "email": "john.updated@example.com"
    }
    
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_delete_user(user_id):
    """Test deleting a user"""
    print(f"Testing delete user {user_id}...")
    response = requests.delete(f"{BASE_URL}/users/{user_id}")
    print(f"Status: {response.status_code}")
    print("User deleted successfully" if response.status_code == 204 else "Failed to delete user")
    print()

def main():
    """Run all tests"""
    print("FastAPI Users Service - API Test")
    print("=" * 40)
    
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    try:
        # Test health check
        test_health_check()
        
        # Test user creation
        user_id = test_create_user()
        
        if user_id:
            # Test getting all users
            test_get_users()
            
            # Test getting specific user
            test_get_user(user_id)
            
            # Test updating user
            test_update_user(user_id)
            
            # Test getting updated user
            test_get_user(user_id)
            
            # Test deleting user
            test_delete_user(user_id)
            
            # Verify user is deleted
            test_get_user(user_id)
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main() 
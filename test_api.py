import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import FastAPI app and database setup from main
from main import app, Base, FeedbackModel, SessionLocal

client = TestClient(app)

def run_tests():
    print("Starting test suite for Baptism Feedback API...")

    # Test 1: Serve Index Page
    print("\n[Test 1] Testing index page serving...")
    response = client.get("/")
    assert response.status_code == 200
    assert "Baptism Feedback" in response.text
    print("Index page served successfully.")

    # Test 2: Submit Valid Feedback
    print("\n[Test 2] Testing valid feedback submission...")
    valid_payload = {
        "name": "Jane Doe",
        "relationship": "Friend",
        "invitation_rating": 5,
        "overall_rating": 4,
        "food_rating": "Excellent",
        "improvements": "No improvements, everything was wonderful!"
    }
    response = client.post("/api/feedback", json=valid_payload)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
    
    data = response.json()
    assert data["status"] == "success"
    assert "id" in data
    feedback_id = data["id"]
    print(f"Feedback submitted successfully. ID returned: {feedback_id}")

    # Verify database entry
    print("Checking database for saved record...")
    db = SessionLocal()
    db_record = db.query(FeedbackModel).filter(FeedbackModel.id == feedback_id).first()
    db.close()
    assert db_record is not None
    assert db_record.name == "Jane Doe"
    assert db_record.relationship == "Friend"
    assert db_record.invitation_rating == 5
    assert db_record.overall_rating == 4
    assert db_record.food_rating == "Excellent"
    assert db_record.improvements == "No improvements, everything was wonderful!"
    print("Database verification passed.")

    # Test 3: Validation Error - Missing fields
    print("\n[Test 3] Testing missing required fields...")
    invalid_payload = {
        "name": "",
        "relationship": "Friend",
        "invitation_rating": 5,
        "overall_rating": 4,
        "food_rating": "Excellent"
    }
    response = client.post("/api/feedback", json=invalid_payload)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("Validation error caught missing fields (name is empty).")

    # Test 4: Validation Error - Invalid Relationship
    print("\n[Test 4] Testing invalid relationship option...")
    invalid_payload = {
        "name": "Alex Smith",
        "relationship": "Stranger", # Invalid
        "invitation_rating": 5,
        "overall_rating": 4,
        "food_rating": "Excellent"
    }
    response = client.post("/api/feedback", json=invalid_payload)
    assert response.status_code == 422
    print("Validation error caught invalid relationship value.")

    # Test 5: Validation Error - Rating Out of Range
    print("\n[Test 5] Testing invalid rating range...")
    invalid_payload = {
        "name": "Alex Smith",
        "relationship": "Neighbor",
        "invitation_rating": 6, # Invalid (> 5)
        "overall_rating": 4,
        "food_rating": "Excellent"
    }
    response = client.post("/api/feedback", json=invalid_payload)
    assert response.status_code == 422
    print("Validation error caught out of bounds rating scale.")

    # Test 6: Validation Error - Invalid Food Rating option
    print("\n[Test 6] Testing invalid food rating option...")
    invalid_payload = {
        "name": "Alex Smith",
        "relationship": "Neighbor",
        "invitation_rating": 5,
        "overall_rating": 4,
        "food_rating": "Tasty" # Invalid
    }
    response = client.post("/api/feedback", json=invalid_payload)
    assert response.status_code == 422
    print("Validation error caught invalid food rating.")

    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        print(f"\nTest validation failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error running tests: {str(e)}")
        sys.exit(1)

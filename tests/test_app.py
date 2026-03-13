"""
Tests for the Mergington High School API using AAA testing pattern
"""

from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self):
        """Test that GET /activities returns all activities"""
        # Arrange: None (using existing data)
        
        # Act: Make GET request to /activities
        response = client.get("/activities")
        
        # Assert: Check status code and response content
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Soccer Team" in data
        assert len(data) == 9

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        # Arrange: None (using existing data)
        
        # Act: Make GET request to /activities
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Check that each activity has required fields
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestRootRedirect:
    """Tests for the GET / endpoint"""

    def test_root_redirects_to_static(self):
        """Test that GET / redirects to /static/index.html"""
        # Arrange: None
        
        # Act: Make GET request to root without following redirects
        response = client.get("/", follow_redirects=False)
        
        # Assert: Check redirect status and location
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def setup_method(self):
        """Arrange: Create a test activity for signup tests"""
        activities["Test Activity"] = {
            "description": "A test activity",
            "schedule": "Test schedule",
            "max_participants": 5,
            "participants": []
        }

    def teardown_method(self):
        """Clean up test activity after each test"""
        if "Test Activity" in activities:
            del activities["Test Activity"]

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        # Arrange: Set up test data
        email = "student@mergington.edu"
        
        # Act: Make POST request to signup
        response = client.post(
            "/activities/Test Activity/signup",
            params={"email": email}
        )
        
        # Assert: Check response and that participant was added
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in activities["Test Activity"]["participants"]

    def test_signup_for_existing_activity(self):
        """Test signup for an existing activity with participants"""
        # Arrange: Use existing activity
        email = "newstudent@mergington.edu"
        
        # Act: Make POST request to signup
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Assert: Check response and participant addition
        assert response.status_code == 200
        assert email in activities["Chess Club"]["participants"]

    def test_signup_for_nonexistent_activity(self):
        """Test signup for an activity that doesn't exist"""
        # Arrange: Use non-existent activity name
        email = "student@mergington.edu"
        
        # Act: Make POST request to signup
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": email}
        )
        
        # Assert: Check error response
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_already_signed_up(self):
        """Test signup when student is already signed up"""
        # Arrange: Use email that's already signed up
        email = "michael@mergington.edu"
        
        # Act: Make POST request to signup
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Assert: Check error response
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_students(self):
        """Test multiple students signing up for the same activity"""
        # Arrange: Set up multiple emails
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Act: Sign up each student
        for email in emails:
            response = client.post(
                "/activities/Test Activity/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert: Check all participants were added
        assert len(activities["Test Activity"]["participants"]) == 3
        for email in emails:
            assert email in activities["Test Activity"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint"""

    def setup_method(self):
        """Arrange: Create a test activity with a participant for unregister tests"""
        activities["Test Activity"] = {
            "description": "A test activity",
            "schedule": "Test schedule",
            "max_participants": 5,
            "participants": ["testuser@mergington.edu"]
        }

    def teardown_method(self):
        """Clean up test activity after each test"""
        if "Test Activity" in activities:
            del activities["Test Activity"]

    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        # Arrange: Set up test data
        email = "testuser@mergington.edu"
        
        # Act: Make DELETE request to unregister
        response = client.delete(
            "/activities/Test Activity/signup",
            params={"email": email}
        )
        
        # Assert: Check response and that participant was removed
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email not in activities["Test Activity"]["participants"]

    def test_unregister_from_existing_activity(self):
        """Test unregistration from an existing activity"""
        # Arrange: Use existing participant
        email = "michael@mergington.edu"
        
        # Act: Make DELETE request to unregister
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Assert: Check response and participant removal
        assert response.status_code == 200
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_from_nonexistent_activity(self):
        """Test unregistration from an activity that doesn't exist"""
        # Arrange: Use non-existent activity
        email = "student@mergington.edu"
        
        # Act: Make DELETE request to unregister
        response = client.delete(
            "/activities/Nonexistent Club/signup",
            params={"email": email}
        )
        
        # Assert: Check error response
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_not_signed_up(self):
        """Test unregistration when student is not signed up"""
        # Arrange: Use email not in participants
        email = "notstudent@mergington.edu"
        
        # Act: Make DELETE request to unregister
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Assert: Check error response
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_multiple_times(self):
        """Test that unregistration only works once"""
        # Arrange: Set up participant
        email = "testuser@mergington.edu"
        
        # Act: First unregistration
        response1 = client.delete(
            "/activities/Test Activity/signup",
            params={"email": email}
        )
        
        # Assert: First attempt succeeds
        assert response1.status_code == 200
        
        # Act: Second unregistration attempt
        response2 = client.delete(
            "/activities/Test Activity/signup",
            params={"email": email}
        )
        
        # Assert: Second attempt fails
        assert response2.status_code == 400

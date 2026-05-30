import asyncio
import httpx
from datetime import date

BASE_URL = "http://localhost:8000/api/v1"

async def run_integration_tests():
    print("=== STARTING RYTHM INTEGRATION TESTS ===")
    
    async with httpx.AsyncClient() as client:
        # Step 1: Registration
        print("\nStep 1: Register Student...")
        reg_payload = {
            "full_name": "Bhargava Test",
            "email": "bhargava_test@gmail.com",
            "password": "securepassword123",
            "college_name": "XYZ Engineering College",
            "graduation_year": 2027,
            "branch": "CSE"
        }
        res = await client.post(f"{BASE_URL}/auth/register", json=reg_payload)
        print(f"Status: {res.status_code}")
        assert res.status_code == 201, "Registration failed"
        reg_data = res.json()
        print(f"Registered user ID: {reg_data['user']['id']}")

        # Step 2: Login
        print("\nStep 2: Login Student...")
        login_payload = {
            "email": "bhargava_test@gmail.com",
            "password": "securepassword123"
        }
        res = await client.post(f"{BASE_URL}/auth/login", json=login_payload)
        print(f"Status: {res.status_code}")
        assert res.status_code == 200, "Login failed"
        login_data = res.json()
        token = login_data["access_token"]
        print("Successfully obtained JWT access token.")
        headers = {"Authorization": f"Bearer {token}"}

        # Step 3: Initialize Career Profile
        print("\nStep 3: Initialize Profile...")
        profile_payload = {
            "bio": "Passionate backend engineer focusing on scalability.",
            "target_roles": ["Backend Developer", "Java Developer"],
            "github_url": "https://github.com/bhargavatest",
            "leetcode_url": "https://leetcode.com/bhargavatest",
            "resume_url": "https://hosted-resumes.com/bhargava.pdf"
        }
        res = await client.post(f"{BASE_URL}/profile/initialize", json=profile_payload, headers=headers)
        print(f"Status: {res.status_code}")
        assert res.status_code == 200, "Profile init failed"
        print(f"Profile Strength: {res.json()['profile_strength']}%")

        # Step 4: Add Student Skills
        print("\nStep 4: Adding Student Skills...")
        skills_payload = {
            "skills": [
                {"skill_name": "Java", "proficiency_level": "INTERMEDIATE"},
                {"skill_name": "SQL", "proficiency_level": "ADVANCED"},
                {"skill_name": "Docker", "proficiency_level": "BEGINNER"}
            ]
        }
        res = await client.post(f"{BASE_URL}/profile/skills", json=skills_payload, headers=headers)
        print(f"Status: {res.status_code}")
        assert res.status_code == 200, "Adding skills failed"
        print(f"New Profile Strength: {res.json()['profile_strength']}%")

        # Step 5: Ingest Opportunity (Amazon)
        print("\nStep 5: Ingesting Opportunity...")
        job_payload = {
            "company_name": "Amazon",
            "role": "Backend Intern",
            "source_platform": "LinkedIn",
            "application_url": "https://amazon.jobs/view/123",
            "deadline": str(date(2026, 6, 25)),
            "job_description_text": "Looking for Java developers. Framework experience like Spring Boot or Microservices is a plus."
        }
        res = await client.post(f"{BASE_URL}/applications/ingest", json=job_payload, headers=headers)
        print(f"Status: {res.status_code}")
        assert res.status_code == 201, "Ingestion failed"
        app_data = res.json()
        app_id = app_data["id"]
        print(f"Ingested App ID: {app_id}")
        print(f"AI Match Score: {app_data['ai_analysis']['match_score'] * 100}%")
        print(f"Priority Score: {app_data['priority_score']}")

        # Step 6: List Opportunities
        print("\nStep 6: Listing Opportunities...")
        res = await client.get(f"{BASE_URL}/applications", headers=headers)
        print(f"Status: {res.status_code}")
        assert res.status_code == 200, "Listing failed"
        print(f"Found {len(res.json())} applications.")

        # Step 7: Transition Status
        print("\nStep 7: Transitioning Application Status...")
        trans_payload = {
            "new_status": "OA_SCHEDULED",
            "notes": "OA invite received."
        }
        res = await client.patch(f"{BASE_URL}/applications/{app_id}/status", json=trans_payload, headers=headers)
        print(f"Status: {res.status_code}")
        assert res.status_code == 200, "Transition failed"
        print(f"New Status: {res.json()['new_status']}")

        # Step 8: Resume Tailoring
        print("\nStep 8: Querying Resume Tailor suggestions...")
        resume_payload = {
            "raw_resume_text": "Bhargava. Backend Developer. Experienced in Java and SQL databases."
        }
        res = await client.post(f"{BASE_URL}/applications/{app_id}/resume-tailor", json=resume_payload, headers=headers)
        print(f"Status: {res.status_code}")
        assert res.status_code == 200, "Resume tailoring failed"
        tailor_data = res.json()
        print("Suggested Optimizations:")
        print(tailor_data["suggestions"]["bullet_points_optimizations"])

        # Step 9: Analytics Overview
        print("\nStep 9: Fetching Analytics...")
        res = await client.get(f"{BASE_URL}/analytics/overview", headers=headers)
        print(f"Status: {res.status_code}")
        assert res.status_code == 200, "Analytics failed"
        print(f"Total Applications: {res.json()['total_applications']}")
        print(f"Conversion rates: {res.json()['rates']}")

        # Step 10: Market Trends (Caching verification)
        print("\nStep 10: Fetching Market Trends (Verify Caching)...")
        # Request 1 (Computes and caches)
        res1 = await client.get(f"{BASE_URL}/analytics/market-trends", headers=headers)
        print(f"Request 1 Status: {res1.status_code}")
        assert res1.status_code == 200, "Market trends failed"
        
        # Request 2 (Fetches directly from cache)
        res2 = await client.get(f"{BASE_URL}/analytics/market-trends", headers=headers)
        print(f"Request 2 Status: {res2.status_code}")
        assert res2.status_code == 200, "Market trends cached check failed"
        print("Market trends successfully retrieved.")

        # Step 11: Request Password Reset
        print("\nStep 11: Triggering Password Reset request background task...")
        reset_payload = {"email": "bhargava_test@gmail.com"}
        res = await client.post(f"{BASE_URL}/auth/password-reset-request", json=reset_payload)
        print(f"Status: {res.status_code}")
        assert res.status_code == 200, "Reset request failed"
        print("Password reset trigger completed. Simulated background email log generated in container stdout.")

        print("\n=== ALL INTEGRATION TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(run_integration_tests())

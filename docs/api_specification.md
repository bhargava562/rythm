# REST API Endpoint Specification: Rythm

This document defines the complete backend API surface for Rythm. All endpoints reside under the base path `/api/v1`. Communication is performed exclusively over HTTPS with JSON payloads.

---

## 1. Authentication Endpoints

### 1.1 Student Registration
* **Endpoint**: `POST /auth/register`
* **Authentication**: None
* **Request Header**: `Content-Type: application/json`
* **Request Body**:
```json
{
  "full_name": "Bhargava",
  "email": "bhargava@gmail.com",
  "password": "raw_password_string",
  "college_name": "XYZ Engineering College",
  "graduation_year": 2027,
  "branch": "CSE"
}
```
* **Success Response** (`201 Created`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "ref_token_uuid_or_jwt...",
  "token_type": "bearer",
  "user": {
    "id": "e5b8e967-b50a-4712-ba29-373d32ef7491",
    "email": "bhargava@gmail.com",
    "full_name": "Bhargava"
  }
}
```
* **Error Response** (`400 Bad Request`):
```json
{
  "detail": "Email already registered"
}
```

### 1.2 Student Login
* **Endpoint**: `POST /auth/login`
* **Authentication**: None
* **Request Body**:
```json
{
  "email": "bhargava@gmail.com",
  "password": "raw_password_string"
}
```
* **Success Response** (`200 OK`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "ref_token_uuid_or_jwt...",
  "token_type": "bearer"
}
```
* **Error Response** (`401 Unauthorized`):
```json
{
  "detail": "Incorrect email or password"
}
```

---

## 2. Career Profile Endpoints

### 2.1 Initialize Career Profile
* **Endpoint**: `POST /profile/initialize`
* **Authentication**: Bearer JWT Token
* **Request Body**:
```json
{
  "bio": "Passionate backend engineer working with distributed systems.",
  "target_roles": ["Backend Developer", "Java Developer"],
  "github_url": "https://github.com/bhargava",
  "leetcode_url": "https://leetcode.com/bhargava",
  "resume_url": "https://s3.amazonaws.com/rythm-resumes/uuid.pdf"
}
```
* **Success Response** (`200 OK`):
```json
{
  "student_id": "e5b8e967-b50a-4712-ba29-373d32ef7491",
  "profile_strength": 42,
  "target_roles": ["Backend Developer", "Java Developer"],
  "updated_at": "2026-05-27T12:00:00Z"
}
```

### 2.2 Add Student Skills
* **Endpoint**: `POST /profile/skills`
* **Authentication**: Bearer JWT Token
* **Request Body**:
```json
{
  "skills": [
    {
      "skill_name": "Java",
      "proficiency_level": "INTERMEDIATE"
    },
    {
      "skill_name": "SQL",
      "proficiency_level": "ADVANCED"
    },
    {
      "skill_name": "Docker",
      "proficiency_level": "BEGINNER"
    }
  ]
}
```
* **Success Response** (`200 OK`):
```json
{
  "message": "Skills updated successfully",
  "profile_strength": 65,
  "skills_added_count": 3
}
```

---

## 3. Opportunity Ingestion & Tracking

### 3.1 Ingest Opportunity
Pasts raw text. Triggers asynchronous parsing, matching, and priority indexing.
* **Endpoint**: `POST /applications/ingest`
* **Authentication**: Bearer JWT Token
* **Request Body**:
```json
{
  "company_name": "Amazon",
  "role": "Backend Intern",
  "source_platform": "LinkedIn",
  "application_url": "https://www.linkedin.com/jobs/view/12345",
  "deadline": "2026-06-15",
  "job_description_text": "We are looking for Java Spring Boot developers. Experience with Docker and Microservices is a plus."
}
```
* **Success Response** (`201 Created`):
```json
{
  "id": "a9d8f6b5-0c9f-4318-8f8d-db321d4576ee",
  "company_name": "Amazon",
  "role": "Backend Intern",
  "status": "SAVED",
  "priority_score": 0.87,
  "ai_analysis": {
    "extracted_domain": "Backend Engineering",
    "extracted_experience_level": "Intern",
    "required_skills": ["Java", "Spring Boot", "Docker", "Microservices"],
    "match_score": 0.50,
    "matching_skills": ["Java", "Docker"],
    "missing_skills": ["Spring Boot", "Microservices"]
  }
}
```

### 3.2 List Opportunities
Get all opportunities, ordered by priority score descending.
* **Endpoint**: `GET /applications`
* **Authentication**: Bearer JWT Token
* **Query Parameters**:
  * `status`: Filter by status (e.g. `SAVED`, `APPLIED`, `INTERVIEW`)
  * `sort`: Sort parameters (`priority_score`, `deadline`)
* **Success Response** (`200 OK`):
```json
[
  {
    "id": "f89d7b65-e9df-4a67-b50a-32ef4f772412",
    "company_name": "Google",
    "role": "SWE Intern",
    "deadline": "2026-06-30",
    "status": "SAVED",
    "priority_score": 0.92,
    "match_score": 0.75
  },
  {
    "id": "a9d8f6b5-0c9f-4318-8f8d-db321d4576ee",
    "company_name": "Amazon",
    "role": "Backend Intern",
    "deadline": "2026-06-15",
    "status": "SAVED",
    "priority_score": 0.87,
    "match_score": 0.50
  }
]
```

### 3.3 Transition Application Status
* **Endpoint**: `PATCH /applications/{id}/status`
* **Authentication**: Bearer JWT Token
* **Request Body**:
```json
{
  "new_status": "OA_SCHEDULED",
  "notes": "Received Online Assessment link via email. Scheduled for Friday."
}
```
* **Success Response** (`200 OK`):
```json
{
  "application_id": "a9d8f6b5-0c9f-4318-8f8d-db321d4576ee",
  "old_status": "SAVED",
  "new_status": "OA_SCHEDULED",
  "transitioned_at": "2026-05-27T12:05:00Z"
}
```

---

## 4. AI & Intelligence Engines

### 4.1 Resume Tailoring suggestions
* **Endpoint**: `POST /applications/{id}/resume-tailor`
* **Authentication**: Bearer JWT Token
* **Request Body**:
```json
{
  "raw_resume_text": "Bhargava. Backend Developer. Experienced in Java and PostgreSQL database architecture..."
}
```
* **Success Response** (`200 OK`):
```json
{
  "application_id": "a9d8f6b5-0c9f-4318-8f8d-db321d4576ee",
  "target_role": "Backend Intern (Amazon)",
  "matching_score_estimate": 0.55,
  "suggestions": {
    "missing_keywords": ["Spring Boot", "Microservices", "REST APIs"],
    "bullet_points_optimizations": [
      {
        "original": "Worked on database design for college projects.",
        "replacement": "Architected normalized PostgreSQL schema (UUID keys, composite index overlays) to drive career tracking operations."
      }
    ],
    "skills_to_highlight": ["Java", "Docker", "SQL Databases"]
  }
}
```

---

## 5. Analytics & Macro Trends

### 5.1 Student Analytics Overview
* **Endpoint**: `GET /analytics/overview`
* **Authentication**: Bearer JWT Token
* **Success Response** (`200 OK`):
```json
{
  "total_applications": 42,
  "funnel": {
    "saved": 15,
    "applied": 18,
    "oa_scheduled": 5,
    "interview": 3,
    "offers": 1,
    "rejected": 10
  },
  "rates": {
    "interview_rate": 0.18,
    "offer_rate": 0.04
  },
  "skill_deficits": [
    { "skill_name": "Spring Boot", "missing_count": 8 },
    { "skill_name": "Microservices", "missing_count": 5 },
    { "skill_name": "Kafka", "missing_count": 3 }
  ]
}
```

### 5.2 Market Trend Intelligence
System-wide aggregates.
* **Endpoint**: `GET /analytics/market-trends`
* **Authentication**: Bearer JWT Token
* **Success Response** (`200 OK`):
```json
{
  "measured_date": "2026-05-27",
  "hottest_skills": [
    { "skill_name": "Kafka", "demand_count": 142, "growth_weekly": 0.32 },
    { "skill_name": "Redis", "demand_count": 118, "growth_weekly": 0.18 },
    { "skill_name": "Spring Boot", "demand_count": 95, "growth_weekly": 0.12 }
  ],
  "recommendations": "Based on 32% growth in Kafka listings, integrating message queues in backend applications is highly advised."
}
```

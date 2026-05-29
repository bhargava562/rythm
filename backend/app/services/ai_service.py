import os
import json
import httpx
from typing import List, Dict, Any

POPULAR_SKILLS = {
    "Java": ["java"],
    "Spring Boot": ["spring boot", "springboot", "spring-boot"],
    "Docker": ["docker"],
    "SQL": ["sql", "mysql", "sqlite"],
    "PostgreSQL": ["postgres", "postgresql"],
    "Redis": ["redis"],
    "Kafka": ["kafka"],
    "Microservices": ["microservice", "microservices"],
    "REST APIs": ["rest api", "rest apis", "restful"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Python": ["python"],
    "Django": ["django"],
    "FastAPI": ["fastapi"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript", "ts"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node.js", "nodejs", "node"],
    "AWS": ["aws", "amazon web services"],
    "Git": ["git", "github"],
    "MongoDB": ["mongodb", "mongo"]
}

class AIService:
    @staticmethod
    def fallback_extract(text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        extracted_skills = []
        
        for skill_name, keywords in POPULAR_SKILLS.items():
            for kw in keywords:
                if kw in text_lower:
                    extracted_skills.append(skill_name)
                    break
        
        domain = "Software Engineering"
        if any(x in text_lower for x in ["backend", "server", "database", "api"]):
            domain = "Backend Engineering"
        elif any(x in text_lower for x in ["frontend", "ui", "ux", "css", "react"]):
            domain = "Frontend Engineering"
        elif any(x in text_lower for x in ["data science", "machine learning", "ml", "ai"]):
            domain = "Data Science"

        level = "Junior / Intern"
        if any(x in text_lower for x in ["senior", "lead", "architect", "principal"]):
            level = "Senior"
        elif "mid" in text_lower or "experience" in text_lower:
            level = "Mid-Level"

        return {
            "skills": list(set(extracted_skills)) if extracted_skills else ["Java", "SQL"],
            "domain": domain,
            "experience_level": level
        }

    @classmethod
    async def extract_skills_from_jd(cls, job_description: str) -> Dict[str, Any]:
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            return cls.fallback_extract(job_description)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_key}"
        prompt = (
            "You are an expert HR applicant parsing system. Extract: "
            "1. A list of technical skills/frameworks. "
            "2. The primary domain (e.g. Backend Engineering, Frontend Engineering). "
            "3. The required experience level (e.g. Intern, Mid, Senior).\n"
            f"Job description: {job_description}\n"
            "Return ONLY a clean JSON object containing keys: 'skills' (array of strings), "
            "'domain' (string), and 'experience_level' (string). No markdown, no triple backticks."
        )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=10.0
                )
            if response.status_code == 200:
                res_json = response.json()
                content = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1].rsplit("\n", 1)[0]
                return json.loads(content)
        except Exception as e:
            print(f"AI API call failed: {str(e)}. Triggering fallback regex parsing.")
        
        return cls.fallback_extract(job_description)

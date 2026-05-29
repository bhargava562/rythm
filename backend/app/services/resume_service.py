import os
import json
import httpx
from typing import Dict, Any, List

class ResumeService:
    @staticmethod
    def fallback_resume_tailoring(
        company_name: str, 
        role: str, 
        missing_skills: List[str], 
        student_skills: List[str]
    ) -> Dict[str, Any]:
        bullet_points = []
        if missing_skills:
            primary_missing = missing_skills[0]
            bullet_points.append({
                "original": "Worked on backend feature developments.",
                "replacement": f"Architected scalable backend microservices using {primary_missing} for data flow operations."
            })
        else:
            bullet_points.append({
                "original": "Responsible for managing standard project tasks.",
                "replacement": f"Led development of backend systems using {' and '.join(student_skills[:2]) if student_skills else 'Java and SQL'}."
            })

        return {
            "missing_keywords": missing_skills if missing_skills else ["Rest APIs", "System Architecture"],
            "bullet_points_optimizations": bullet_points,
            "skills_to_highlight": student_skills if student_skills else ["Software Engineering"]
        }

    @classmethod
    async def generate_resume_suggestions(
        cls,
        company_name: str,
        role: str,
        resume_text: str,
        required_skills: List[str],
        missing_skills: List[str],
        student_skills: List[str]
    ) -> Dict[str, Any]:
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            return cls.fallback_resume_tailoring(company_name, role, missing_skills, student_skills)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_key}"
        prompt = (
            "You are an expert resume writer and ATS optimization engine. "
            f"Analyze the student's resume against the '{role}' opening at '{company_name}'.\n"
            f"Required skills: {', '.join(required_skills)}\n"
            f"Missing skills: {', '.join(missing_skills)}\n"
            f"Student current skills: {', '.join(student_skills)}\n\n"
            f"Student Resume text:\n{resume_text}\n\n"
            "Return a JSON object containing recommendations:\n"
            "1. 'missing_keywords' (array of strings from required skills missing on resume)\n"
            "2. 'bullet_points_optimizations' (array of objects with 'original' and 'replacement' text keys)\n"
            "3. 'skills_to_highlight' (array of strings representing student strengths to emphasize)\n"
            "Return ONLY the raw JSON object, no triple backticks, no markdown tags."
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=12.0
                )
            if response.status_code == 200:
                res_json = response.json()
                content = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1].rsplit("\n", 1)[0]
                return json.loads(content)
        except Exception as e:
            print(f"Resume Tailoring API call failed: {str(e)}. Running local parser.")

        return cls.fallback_resume_tailoring(company_name, role, missing_skills, student_skills)

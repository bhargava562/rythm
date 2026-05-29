import asyncio
from sqlalchemy.future import select
from backend.app.database import engine, Base, async_session
from backend.app.models.skill import SkillsMaster, SkillTrend

# Initial skills catalog seeds
SEED_SKILLS = [
    {"skill_name": "Java", "category": "Language"},
    {"skill_name": "Spring Boot", "category": "Framework"},
    {"skill_name": "Docker", "category": "Tool"},
    {"skill_name": "SQL", "category": "Database"},
    {"skill_name": "PostgreSQL", "category": "Database"},
    {"skill_name": "Redis", "category": "Database"},
    {"skill_name": "Kafka", "category": "Tool"},
    {"skill_name": "Microservices", "category": "Architecture"},
    {"skill_name": "REST APIs", "category": "Architecture"},
    {"skill_name": "Kubernetes", "category": "Tool"},
    {"skill_name": "Python", "category": "Language"},
    {"skill_name": "Django", "category": "Framework"},
    {"skill_name": "FastAPI", "category": "Framework"},
    {"skill_name": "JavaScript", "category": "Language"},
    {"skill_name": "TypeScript", "category": "Language"},
    {"skill_name": "React", "category": "Framework"},
    {"skill_name": "Node.js", "category": "Framework"},
    {"skill_name": "AWS", "category": "Cloud"},
    {"skill_name": "Git", "category": "Tool"},
    {"skill_name": "MongoDB", "category": "Database"}
]

# Initial market trends seeds
SEED_TRENDS = [
    {"skill_name": "Kafka", "demand_count": 142, "trend_percentage": 32.0},
    {"skill_name": "Redis", "demand_count": 118, "trend_percentage": 18.0},
    {"skill_name": "Spring Boot", "demand_count": 95, "trend_percentage": 12.0},
    {"skill_name": "Docker", "demand_count": 87, "trend_percentage": 8.0}
]

async def seed_data():
    print("Connecting to database engine...")
    async with engine.begin() as conn:
        print("Creating tables if not exists...")
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        print("Seeding skills_master...")
        for skill in SEED_SKILLS:
            # Check if exists
            result = await session.execute(
                select(SkillsMaster).where(SkillsMaster.skill_name == skill["skill_name"])
            )
            existing = result.scalar_one_or_none()
            if not existing:
                new_skill = SkillsMaster(
                    skill_name=skill["skill_name"],
                    category=skill["category"]
                )
                session.add(new_skill)
                print(f"Added skill: {skill['skill_name']}")
            else:
                print(f"Skill already exists: {skill['skill_name']}")

        print("Seeding skill_trends...")
        for trend in SEED_TRENDS:
            result = await session.execute(
                select(SkillTrend).where(SkillTrend.skill_name == trend["skill_name"])
            )
            existing = result.scalar_one_or_none()
            if not existing:
                new_trend = SkillTrend(
                    skill_name=trend["skill_name"],
                    demand_count=trend["demand_count"],
                    trend_percentage=trend["trend_percentage"]
                )
                session.add(new_trend)
                print(f"Added trend: {trend['skill_name']}")
            else:
                # Update existing trend
                existing.demand_count = trend["demand_count"]
                existing.trend_percentage = trend["trend_percentage"]
                session.add(existing)
                print(f"Updated trend: {trend['skill_name']}")

        await session.commit()
        print("Seeding process completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())

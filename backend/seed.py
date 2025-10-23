# backend/seed.py
import json
from sqlalchemy.orm import sessionmaker
from app import Base, Profile, create_db, engine, json_dumps

SessionLocal = sessionmaker(bind=engine)

def seed():
    create_db()
    with SessionLocal() as db:
        # Delete old data if present
        db.query(Profile).delete()

        # ✅ Add your real data here
        profile = Profile(
            name="Vamsi Gudipudi",
            email="gudipudi.krishna.22031@iitgoa.ac.in",
            education="B.Tech Computer Science, IIT Goa (4th Year)",
            skills=json_dumps([
                "Python", "C++", "Flask", "SQL", "Docker"
            ]),
            projects=json_dumps([
                {
                    "id": 1,
                    "title": "Hostel Management System",
                    "description": "Flask-based CRUD web app with room allocation, capacity enforcement, and role-based access control.",
                    "links": ["https://github.com/gvkvamsi1410/Hostel-Management-System"],
                    "skills": ["Python", "Flask", "SQL", "HTML"]
                },
                {
                    "id": 2,
                    "title": "Metro Crew Scheduling Solver",
                    "description": "Optimization-based solver for periodic train crew scheduling using Python and PuLP.",
                    "links": ["https://github.com/gvkvamsi1410/Metro-Scheduling"],
                    "skills": ["Python", "Optimization", "Pandas", "PuLP"]
                },
                {
                    "id": 3,
                    "title": "Memory Usage Monitoring Daemon",
                    "description": "System-level daemon written in C to continuously log memory usage statistics of processes.",
                    "links": ["https://github.com/gvkvamsi1410/OS-PROJECT"],
                    "skills": ["C", "Linux", "System Programming"]
                }
            ]),
            links=json_dumps({
                "github": "https://github.com/gvkvamsi1410",
                "linkedin": "https://linkedin.com/in/vamsigudipudi",
                "portfolio": "https://vamsi.dev"
            })
        )

        db.add(profile)
        db.commit()
        print(" Database seeded successfully with sample profile & projects!")

if __name__ == "__main__":
    seed()

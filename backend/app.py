import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///me_playground.db")

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def json_loads(text):
    try:
        return json.loads(text) if text else []
    except Exception:
        return []

def json_dumps(obj):
    return json.dumps(obj or [])

class Profile(Base):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    email = Column(String(200))
    education = Column(Text)
    skills = Column(Text)
    projects = Column(Text)
    links = Column(Text)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "education": self.education,
            "skills": json_loads(self.skills),
            "projects": json_loads(self.projects),
            "links": json_loads(self.links),
        }

def create_db():
    Base.metadata.create_all(bind=engine)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# --- NEW HOME ROUTE ---
@app.route("/", methods=["GET"])
def home():
    return """
    <html>
    <head>
      <title>Me-API Playground</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #0d6efd; }
        a { color: #0d6efd; text-decoration: none; }
      </style>
    </head>
    <body>
      <h1>Welcome to Me-API Playground </h1>
      <p>This API exposes your personal data via REST endpoints.</p>
      <h3>Available Endpoints:</h3>
      <ul>
        <li><a href="/health">GET /health</a> – Check server status</li>
        <li><a href="/profile">GET /profile</a> – View your profile</li>
        <li><a href="/projects">GET /projects</a> – List all projects</li>
        <li><a href="/skills/top">GET /skills/top</a> – Top skills by frequency</li>
        <li><a href="/search?q=python">GET /search?q=python</a> – Search profile & projects</li>
      </ul>
      <p>Frontend: open <code>frontend/index.html</code> in your browser to explore visually.</p>
    </body>
    </html>
    """, 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/profile", methods=["GET"])
def get_profile():
    with SessionLocal() as db:
        p = db.query(Profile).first()
        if not p:
            return jsonify({}), 204
        return jsonify(p.to_dict()), 200


@app.route("/profile", methods=["POST", "PUT"])
def create_or_update_profile():
    data = request.get_json() or {}
    if not data.get("name") or not data.get("email"):
        return jsonify({"error": "name and email are required"}), 400
    with SessionLocal() as db:
        p = db.query(Profile).first()
        if not p:
            p = Profile()
        p.name = data.get("name")
        p.email = data.get("email")
        p.education = data.get("education") or ""
        p.skills = json_dumps(data.get("skills", []))
        p.projects = json_dumps(data.get("projects", []))
        p.links = json_dumps(data.get("links", {}))
        db.add(p)
        db.commit()
        db.refresh(p)
        return jsonify(p.to_dict()), 201


@app.route("/projects", methods=["GET"])
def list_projects():
    skill_query = request.args.get("skill")
    with SessionLocal() as db:
        p = db.query(Profile).first()
        if not p:
            return jsonify([]), 200
        projects = json_loads(p.projects)
        if skill_query:
            skill_lower = skill_query.strip().lower()
            filtered = [
                proj for proj in projects
                if any(skill_lower in s.lower() for s in proj.get("skills", []))
                or skill_lower in proj.get("title", "").lower()
                or skill_lower in proj.get("description", "").lower()
            ]
            return jsonify(filtered), 200
        return jsonify(projects), 200


@app.route("/projects", methods=["POST"])
def add_project():
    data = request.get_json() or {}
    required = ["title", "description"]
    if not all(k in data for k in required):
        return jsonify({"error": "title and description required"}), 400
    with SessionLocal() as db:
        p = db.query(Profile).first()
        if not p:
            return jsonify({"error": "create profile first"}), 400
        projects = json_loads(p.projects)
        new_proj = {
            "id": (max([pr.get("id", 0) for pr in projects]) + 1) if projects else 1,
            "title": data.get("title"),
            "description": data.get("description"),
            "links": data.get("links", []),
            "skills": data.get("skills", []),
        }
        projects.append(new_proj)
        p.projects = json_dumps(projects)
        db.add(p)
        db.commit()
        return jsonify(new_proj), 201


@app.route("/skills/top", methods=["GET"])
def top_skills():
    with SessionLocal() as db:
        p = db.query(Profile).first()
        if not p:
            return jsonify([]), 200
        skills = {}
        for s in json_loads(p.skills):
            skills[s] = skills.get(s, 0) + 1
        for proj in json_loads(p.projects):
            for s in proj.get("skills", []):
                skills[s] = skills.get(s, 0) + 1
        sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
        return jsonify([{"skill": k, "count": v} for k, v in sorted_skills]), 200


@app.route("/search", methods=["GET"])
def search():
    q = (request.args.get("q") or "").strip().lower()
    if not q:
        return jsonify({"error": "q param required"}), 400
    results = {"profile": None, "projects": [], "skills": []}
    with SessionLocal() as db:
        p = db.query(Profile).first()
        if not p:
            return jsonify(results), 200
        if q in (p.name or "").lower() or q in (p.education or "").lower():
            results["profile"] = p.to_dict()
        for pr in json_loads(p.projects):
            if (
                q in pr.get("title", "").lower()
                or q in pr.get("description", "").lower()
                or any(q in s.lower() for s in pr.get("skills", []))
            ):
                results["projects"].append(pr)
        for s in json_loads(p.skills):
            if q in s.lower():
                results["skills"].append(s)
    return jsonify(results), 200


if __name__ == "__main__":
    create_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

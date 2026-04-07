from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import json

app = Flask(__name__)
CORS(app)

client = Groq(api_key="GROQ_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "AI CI/CD Reviewer is running!"})

@app.route("/review", methods=["POST"])
def review_pipeline():
    try:
        data = request.json
        yaml_content = data.get("yaml", "")

        if not yaml_content:
            return jsonify({"error": "No YAML provided"}), 400

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a DevOps security expert. Always respond with valid JSON only. No markdown, no explanation, just raw JSON array."
                },
                {
                    "role": "user",
                    "content": build_prompt(yaml_content)
                }
            ],
            temperature=0.3
        )

        raw = response.choices[0].message.content.strip()

        # Clean markdown if model wraps in ```json
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        issues = json.loads(raw.strip())
        return jsonify({"review": issues, "total": len(issues)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def build_prompt(yaml_content):
    return f"""
Review this CI/CD pipeline YAML and return ONLY a JSON array.

Each item must have:
- "category": one of [Security, Performance, BestPractice]
- "severity": one of [Critical, Warning, Suggestion]
- "issue": short title of the problem
- "fix": exact fix they should apply

YAML to review:
{yaml_content}

Return ONLY the JSON array. No explanation. No markdown. No extra text.
"""

if __name__ == "__main__":
    app.run(debug=True, port=5000)
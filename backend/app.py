from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import json
import os

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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
                {"role": "system", "content": "You are a DevOps security expert. Always respond with valid JSON only. No markdown, no explanation, just raw JSON array."},
                {"role": "user", "content": build_prompt(yaml_content)}
            ],
            temperature=0.3
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith(" ` "):
            raw = raw.split(" ` ")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        issues = json.loads(raw.strip())
        return jsonify({"review": issues, "total": len(issues)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def build_prompt(yaml_content):
    return f"Review this CI/CD pipeline YAML and return ONLY a JSON array. Each item must have category (Security/Performance/BestPractice), severity (Critical/Warning/Suggestion), issue (short title), fix (exact fix). YAML: {yaml_content}. Return ONLY JSON array."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)

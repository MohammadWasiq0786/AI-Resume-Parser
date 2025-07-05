from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
import os, json, re
from euriai import EuriaiClient

app = Flask(__name__)
EURI_API_KEY = os.getenv("EURI_API_KEY")
client = EuriaiClient(api_key=EURI_API_KEY, model="gpt-4.1-nano")

def remove_json_comments(text):
    # Remove // ... style comments (even inside array/object)
    # Also strips trailing commas (common LLM bug for JSON!)
    def strip_trailing_commas(s):
        # Remove trailing commas before } or ]
        return re.sub(r',(\s*[\]}])', r'\1', s)
    # Remove inline // comments
    pattern = re.compile(r'^(.*?)//.*$', re.MULTILINE)
    text = re.sub(pattern, r'\1', text)
    return strip_trailing_commas(text)

def resumes_details(resume_text: str):
    prompt = f"""
You are a resume parsing assistant. Extract structured JSON from this resume:

{resume_text}

Return only JSON. No commentary. Include:
- Full Name, Contact Number, Email Address, Location
- Skills (Technical & Non-Technical)
- Education (Degree, Institution, Years)
- Work Experience (Job Title, Company Name, Years, Responsibilities)
- Certifications
- Languages spoken
- Suggested Resume Category
- Recommended Job Roles
"""
    response = client.generate_completion(prompt=prompt, temperature=0.5, max_tokens=1000)
    raw = response['choices'][0]['message']['content'] if 'choices' in response else ""
    return raw


@app.route("/")
def index():
    # Render template, initially empty (results filled after POST)
    return render_template("index.html")

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return render_template("index.html", error="No file part in upload.")
    file = request.files['resume']
    if file.filename == '':
        return render_template("index.html", error="No selected file.")
    if not file.filename.endswith('.pdf'):
        return render_template("index.html", error="Only PDF files allowed.")

    # Extract text from PDF
    text = ""
    reader = PdfReader(file)
    for page in reader.pages:
        text += page.extract_text()

    # Get response from Gemini LLM
    response = resumes_details(text)
    # Remove markdown code blocks if present
    response_clean = response.replace("```json", "").replace("```", "").strip()
    # Remove comments and trailing commas
    response_clean = remove_json_comments(response_clean)
    # Try to parse the cleaned response
    try:
        data = json.loads(response_clean)
    except Exception as e:
        # Show error on the frontend (for debugging)
        return render_template("index.html",
                               error="AI or JSON format error. Parsing failed.",
                               raw_response=response,
                               details=str(e))

    # Parse/format details for frontend (use .get to avoid KeyErrors)
    full_name = data.get("Full Name", "")
    contact_number = data.get("Contact Number", "")
    email_address = data.get("Email Address", "")
    location = data.get("Location", "")

    # Skills extraction
    skills = data.get("Skills", {})
    try:
        technical_skills = skills.get("Technical", []) or skills.get("Technical Skills", [])
    except AttributeError:
        pass
    if isinstance(technical_skills, list):
        technical_skills_str = ', '.join(technical_skills)
    else:
        technical_skills_str = str(technical_skills)
    non_technical_skills = skills.get("Non-Technical", []) or skills.get("Non-Technical Skills", [])
    if isinstance(non_technical_skills, list):
        non_technical_skills_str = ', '.join(non_technical_skills)
    else:
        non_technical_skills_str = str(non_technical_skills)

    # Education extraction
    education_list = data.get("Education", [])
    if isinstance(education_list, list):
        education_str = "\n".join([
            f"{edu.get('Degree', 'N/A')} from {edu.get('Institution', 'N/A')} (Graduated: {edu.get('Years', 'N/A')})"
            for edu in education_list
        ])
    else:
        # Sometimes LLM outputs as string
        education_str = str(education_list)

    # Work Experience extraction
    work_experience_list = data.get("Work Experience", [])
    if isinstance(work_experience_list, list):
        work_experience_str = "\n".join([
            f"{job.get('Job Title', 'N/A')} at {job.get('Company Name', 'N/A')} ({job.get('Years', 'N/A')})\nResponsibilities: {', '.join(job.get('Responsibilities', []))}"
            for job in work_experience_list
        ])
    else:
        work_experience_str = str(work_experience_list)

    # Certifications
    certifications = data.get("Certifications", [])
    if isinstance(certifications, list):
        certifications_str = ", ".join(certifications)
    else:
        certifications_str = str(certifications)

    # Languages spoken
    languages = data.get("Languages spoken", []) or data.get("Languages", [])
    if isinstance(languages, list):
        languages_str = ", ".join(languages)
    else:
        languages_str = str(languages)

    # Suggested Category and Recommended Job Roles extraction
    suggested_resume_category = data.get("Suggested Resume Category", "")
    recommended_job_roles = data.get("Recommended Job Roles", [])
    if isinstance(recommended_job_roles, list):
        recommended_job_roles_str = ", ".join(recommended_job_roles)
    else:
        recommended_job_roles_str = str(recommended_job_roles)

    # Render template with all fields
    return render_template('index.html',
                           full_name=full_name,
                           contact_number=contact_number,
                           email_address=email_address,
                           location=location,
                           technical_skills=technical_skills_str,
                           non_technical_skills=non_technical_skills_str,
                           education=education_str,
                           work_experience=work_experience_str,
                           certifications=certifications_str,
                           languages=languages_str,
                           suggested_resume_category=suggested_resume_category,
                           recommended_job_roles=recommended_job_roles_str,
                           error=None)

if __name__ == "__main__":
    app.run(debug=True)
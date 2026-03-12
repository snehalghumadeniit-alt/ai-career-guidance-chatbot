from flask import Flask, render_template, request, jsonify
import pandas as pd
import re

app = Flask(__name__)

# ==========================================
# LOAD DATASET
# ==========================================

data = pd.read_excel("career_dataset_extended.xlsx")

data.columns = data.columns.str.strip().str.lower()

for col in data.columns:
    data[col] = data[col].astype(str).str.lower()

# ==========================================
# CONTEXT MEMORY
# ==========================================

context = {
    "course": None,
    "last_course": None,
    "last_branch": None
}

# ==========================================
# TEXT CLEANING
# ==========================================

def clean(text):

    text = text.lower()
    text = text.replace(".", "")
    text = re.sub(r'[^a-z0-9 ]', '', text)

    return text


# ==========================================
# PERCENTAGE DETECTION
# ==========================================

def detect_percentage(text):

    match = re.search(r'(\d+)\s*(%|percent)', text)

    if match:
        return int(match.group(1))

    return None


# ==========================================
# FORMAT COURSE INFO
# ==========================================

def generate_info(row):

    context["last_course"] = row["course name"]
    context["last_branch"] = row["branch / specialization"]

    return f"""
🎓 <b>Course:</b> {row['course name']} - {row['branch / specialization']}<br>
📚 <b>Level:</b> {row['level']}<br>
📖 <b>Stream:</b> {row['stream']}<br>
⏳ <b>Duration:</b> {row['duration']}<br>
✅ <b>Eligibility:</b> {row['eligibility']}<br>
📝 <b>Entrance Exam:</b> {row['entrance exam']}<br>
📋 <b>Admission Process:</b> {row['admission process']}<br>
💼 <b>Job Roles:</b> {row['job roles']}<br>
🏫 <b>Colleges:</b> {row['colleges / institutes (nagpur)']}<br>
"""


# ==========================================
# GET COURSE BRANCHES
# ==========================================

def get_branches(course):

    rows = data[data["course name"] == course]

    return rows["branch / specialization"].unique()


# ==========================================
# FIND COURSE FROM DATASET
# ==========================================

def find_course(msg):

    words = msg.split()

    courses = data["course name"].unique()

    for course in courses:

        normalized = course.replace(".", "")

        if normalized in words:
            return course

    return None


# ==========================================
# FIND SPECIALIZATION
# ==========================================

def find_specialization(msg):

    if context["course"]:

        rows = data[
            (data["course name"] == context["course"]) &
            (data["branch / specialization"].str.contains(rf"\b{msg}\b", regex=True))
        ]

        if not rows.empty:
            return rows.iloc[0]

    return None


# ==========================================
# COURSE PROGRESSION
# ==========================================

def next_courses(course):

    mapping = {

        "bsc": ["msc","mca","mba"],
        "bcom": ["mcom","mba","ca","cs"],
        "bba": ["mba","pgdm"],
        "bca": ["mca","msc"],
        "ba": ["ma","journalism","civil services"],
        "btech": ["mtech","mba","ms abroad"],
        "mbbs": ["md","ms"],
        "msc": ["phd","research","lecturer"],
        "mtech": ["phd","research engineer"],
        "mba": ["phd","corporate leadership"],
        "mca": ["phd","software architect"]
    }

    key = course.replace(".", "")

    if key in mapping:

        result = f"After {course.upper()} you can pursue:<br><br>"

        for item in mapping[key]:
            result += f"• {item.upper()}<br>"

        return result

    return None


# ==========================================
# CHATBOT LOGIC
# ==========================================

def chatbot(message):

    msg = clean(message)

    if "details" in msg:
        msg = msg.replace("details","").strip()

    # --------------------------------------
    # GREETING
    # --------------------------------------

    if msg in ["hi","hello","hey"]:
        return "Hello 👋 I am your AI Career Guidance Assistant."

    # --------------------------------------
    # AFTER 10TH
    # --------------------------------------

    if "after 10th" in msg:

        return """
After 10th you can choose:

• Science 
• Commerce
• Arts
• Diploma Engineering
• ITI
"""

    # --------------------------------------
    # AFTER 12TH STREAM
    # --------------------------------------

    if "after 12th science" in msg:

        return """
After 12th Science you can choose:

• MBBS
• BDS
• BAMS
• BSc
• BTech
• BCA
"""

    if "after 12th commerce" in msg:

        return """
After 12th Commerce you can choose:

• BCom
• BBA
• CA
• CS
"""

    if "after 12th arts" in msg:

        return """
After 12th Arts you can choose:

• BA
• Journalism
• Psychology
• Law
"""

    if "after 12th" in msg:

        return """
After 12th you can choose:

• BSc
• BTech
• MBBS
• BBA
• BCom
• BA
• BCA
"""

    # --------------------------------------
    # PERCENTAGE
    # --------------------------------------

    percent = detect_percentage(msg)

    if percent:

        if percent >= 90:

            return """
Excellent score! You can aim for:

• Top Engineering Colleges
• MBBS
• BSc Honors Programs
"""

        elif percent >= 75:

            return """
With this percentage you can consider:

• BTech
• BSc
• BBA
• BCA
"""

        else:

            return """
You can explore:

• BCom
• BA
• Diploma Programs
"""

    # --------------------------------------
    # CONTEXT FOLLOW-UP
    # --------------------------------------

    if msg in ["what next","what after this","next step"]:

        if context["last_course"]:
            return next_courses(context["last_course"])

    # --------------------------------------
    # SPECIALIZATION
    # --------------------------------------

    spec_row = find_specialization(msg)

    if spec_row is not None:
        return generate_info(spec_row)



    # --------------------------------------
    # AFTER POST GRADUATION
    # --------------------------------------

    pg_courses = ["msc","mtech","mba","mca","mcom","ma"]

    words = msg.split()

    if "after" in words:

        for w in words:

            if w in pg_courses:

                return f"""
After {w.upper()} you can pursue:

• PhD (Doctoral Research)
• Lecturer / Professor
• Research Scientist
• Industry Specialist
"""

    

    # --------------------------------------
    # COURSE DETECTION
    # --------------------------------------

    course = find_course(msg)

    if course:

        # AFTER COURSE PROGRESSION
        if "after" in msg:

            progression = next_courses(course)

            if progression:
                return progression

        branches = get_branches(course)

        context["course"] = course
        context["last_course"] = course

        reply = f"<b>{course.upper()}</b> has these specializations:<br><br>"

        for b in branches:
            reply += f"<button onclick=\"sendQuick('{b}')\">{b}</button><br>"

        reply += "<br>Select specialization."

        return reply

    # --------------------------------------
    # DEFAULT
    # --------------------------------------

    return "Please ask about courses like BSc, BTech, MBA, MBBS, BBA, BCom."


# ==========================================
# ROUTES
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json["message"]

    response = chatbot(user_message)

    return jsonify({"reply": response})


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

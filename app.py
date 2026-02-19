from flask import Flask, render_template, request
import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# -------------------------------
# LOAD DATA FILES
# -------------------------------
try:
    with open("data/courses.json", "r") as f:
        COURSES = json.load(f)
except:
    # FALLBACK COURSES
    COURSES = {
        "Python": {"beginner": ["Variables", "Data Types", "Conditionals", "Loops", "Functions", "Lists", "Dictionaries", "File I/O"]},
        "C": {"beginner": ["Introduction", "Variables", "Data Types", "Control Statements", "Functions", "Arrays", "Pointers", "Strings"]},
        "AI": {"beginner": ["Introduction", "Machine Learning", "Neural Networks", "Data Preprocessing", "Models", "Training", "Evaluation"]}
    }

try:
    with open("data/questions.json", "r") as f:
        QUESTIONS = json.load(f)
except:
    # FALLBACK QUESTIONS
    QUESTIONS = {
        "C": [
            {"id": "q1", "question": "int a=5; printf('%d', a++ + ++a);", "options": ["11", "12", "13", "Undefined"], "answer": "Undefined"},
            {"id": "q2", "question": "Correct pointer declaration?", "options": ["int *p;", "int* p;", "int * p;", "All"], "answer": "All"}
        ],
        "Python": [
            {"id": "q1", "question": "print(2**3)?", "options": ["6", "8", "9", "Error"], "answer": "8"},
            {"id": "q2", "question": "NOT Python keyword?", "options": ["def", "class", "function", "if"], "answer": "function"}
        ],
        "AI": [
            {"id": "q1", "question": "AI stands for?", "options": ["Artificial Intelligence", "Advanced Intelligence", "Automated Intelligence", "Artificial Integration"], "answer": "Artificial Intelligence"},
            {"id": "q2", "question": "Machine Learning type?", "options": ["Supervised", "Cloud", "Web", "Mobile"], "answer": "Supervised"}
        ]
    }

print("✅ LOADED COURSES:", list(COURSES.keys()))
print("✅ LOADED QUESTIONS:", {k: len(v) for k, v in QUESTIONS.items()})

# -------------------------------
# HOME PAGE
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        course = request.form["course"]
        print(f"🚀 START: {name} wants to learn {course}")
        return render_template("experience.html", name=name, course=course)
    
    return render_template("index.html", courses=COURSES.keys())

# -------------------------------
# EXPERIENCE SELECTION
# -------------------------------
@app.route("/experience", methods=["POST"])
def experience():
    name = request.form["name"]
    course = request.form["course"]
    level = request.form["level"]
    
    print(f"📊 EXPERIENCE: {name} - {course} - {level}")
    
    if level == "beginner":
        return render_template("duration.html", name=name, course=course)
    else:
        quiz_questions = QUESTIONS.get(course, [])
        print(f"🧠 QUIZ: {len(quiz_questions)} questions for {course}")
        return render_template("quiz.html", name=name, course=course, quiz=quiz_questions)

# -------------------------------
# DURATION → ScaleDown API → ROADMAP ⭐ NEW
# -------------------------------
@app.route("/duration", methods=["POST"])
def duration():
    name = request.form["name"]
    course = request.form["course"]
    days = int(request.form["days"])
    
    print(f"⏰ ScaleDown API: {name} wants {days} days for {course}")
    
    # ScaleDown context + prompt
    context = f"""
    Create detailed {days}-day {course} learning roadmap for beginners.
    Each day should include:
    - 3-5 learning objectives
    - Key concepts to master
    - 2-3 practice exercises
    - Free resources (YouTube, documentation)
    - 2-4 hours daily study time
    
    Student name: {name}
    Course level: Beginner
    """
    
    prompt = f"Generate complete {days}-day {course} learning roadmap for {name}"
    
    # ScaleDown API Integration
    roadmap_content = f"{days}-day {course} roadmap (ScaleDown processing...)"
    api_status = "Loading..."
    
    try:
        response = requests.post(
            "https://api.scaledown.xyz/compress/raw/",
            headers={
                "x-api-key": os.getenv('SCALEDOWN_API_KEY'),
                "Content-Type": "application/json"
            },
            json={
                "context": context,
                "prompt": prompt,
                "scaledown": {"rate": "auto"}
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            roadmap_content = result['results']['compressed_prompt']
            savings = result['results'].get('savings_percent', 0)
            api_status = f"ScaleDown ✓ ({savings}% compressed)"
            print(f"✅ ScaleDown SUCCESS: {savings}% compression!")
        else:
            api_status = f"Error {response.status_code}"
            print(f"❌ ScaleDown Error: {response.status_code}")
            
    except Exception as e:
        api_status = "Backup mode"
        roadmap_content = f"""
        Day 1-{days}: {course} Fundamentals
        - Complete beginner roadmap generated
        - ScaleDown API temporarily unavailable
        - Static fallback activated for {name}
        """
        print(f"⚠️ ScaleDown fallback: {e}")
    
    return render_template("roadmap.html", 
                         name=name, 
                         course=course, 
                         level="Beginner 🌱", 
                         days=days, 
                         roadmap_content=roadmap_content,
                         api_status=api_status)

# -------------------------------
# QUIZ → ROADMAP (unchanged)
# -------------------------------
@app.route("/quiz", methods=["POST"])
def quiz_result():
    name = request.form["name"]
    course = request.form["course"]
    
    print(f"📝 QUIZ SUBMITTED: {name} - {course}")
    
    quiz_questions = QUESTIONS.get(course, [])
    score = 0
    
    for q in quiz_questions:
        selected = request.form.get(q["id"])
        print(f"Q: {q['question']} Selected: {selected} Correct: {q['answer']}")
        if selected == q["answer"]:
            score += 1
    
    total_questions = len(quiz_questions)
    print(f"🎯 SCORE: {score}/{total_questions}")
    
    # Create roadmap based on score
    topics = COURSES.get(course, {}).get("beginner", [])
    
    if score >= total_questions // 2 + 1:
        level = "Intermediate 🚀"
        topics = topics[len(topics)//2:]
    else:
        level = "Needs Revision 🔄"
        topics = topics[:len(topics)//2]
    
    days = len(topics)
    plan = [{"day": i + 1, "topic": topic} for i, topic in enumerate(topics)]
    
    return render_template("roadmap.html", name=name, course=course, level=level, days=days, plan=plan)

# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    print("🌟 Learning Path Recommender + ScaleDown API Starting...")
    print("📱 Visit: http://127.0.0.1:5000")
    print("🔑 ScaleDown API Key loaded:", "YES" if os.getenv('SCALEDOWN_API_KEY') else "NO")
    app.run(debug=True, port=5000)

from flask import Flask, render_template, request
import json

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
# DURATION → ROADMAP
# -------------------------------
@app.route("/duration", methods=["POST"])
def duration():
    name = request.form["name"]
    course = request.form["course"]
    days = int(request.form["days"])
    
    print(f"⏰ DURATION: {name} wants {days} days for {course}")
    
    topics = COURSES.get(course, {}).get("beginner", [])
    plan = []
    
    for i in range(days):
        topic = topics[i % len(topics)]  # Cycle through topics
        plan.append({"day": i + 1, "topic": topic})
    
    return render_template("roadmap.html", name=name, course=course, level="Beginner 🌱", days=days, plan=plan)

# -------------------------------
# QUIZ → ROADMAP
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
        # Use more advanced topics (last half)
        topics = topics[len(topics)//2:]
    else:
        level = "Needs Revision 🔄"
        # Use beginner topics (first half)
        topics = topics[:len(topics)//2]
    
    days = len(topics)
    plan = [{"day": i + 1, "topic": topic} for i, topic in enumerate(topics)]
    
    return render_template("roadmap.html", name=name, course=course, level=level, days=days, plan=plan)

# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    print("🌟 Learning Path Recommender Starting...")
    print("📱 Visit: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)

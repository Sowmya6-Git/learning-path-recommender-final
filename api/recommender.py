import json

with open("data/courses.json") as f:
    courses = json.load(f)

def generate_plan(course, days):
    topics = courses[course]["beginner"]
    plan = {}

    for day in range(days):
        plan[f"Day {day+1}"] = topics[day % len(topics)]

    return plan

def evaluate_quiz(form_data, quiz):
    score = 0
    for q in quiz:
        if form_data.get(q["id"]) == q["answer"]:
            score += 1
    return score

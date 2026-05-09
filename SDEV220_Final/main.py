#    Indiana Municipality Cybersecurity Self-Assessment Tool
#    main.py
#    SDEV 220 Final Project
from datetime import datetime
import json
import psycopg2
from psycopg2 import extras # Use to get data as dictionaries

# DATA MODELS
class Municipality:
    """Stores information about a municipality (city/town)"""
    def __init__(self, id, name, county, population, contact_email):
        self.id = id
        self.name = name
        self.county = county
        self.population = population
        self.contact_email = contact_email
 
    def __str__(self):
        return f"{self.name}, {self.county} County (Pop: {self.population})"
 
class Question:
    """Stores a single assessment question"""
    def __init__(self, id, category, text, weight, options, gap_description, recommendation):
        self.id = id
        self.category = category
        self.text = text
        self.weight = weight
        self.options = options  # list of answer options
        self.gap_description = gap_description  # used if score is low
        self.recommendation = recommendation # text recommendation for low scores
 
    def __str__(self):
        return f"[{self.category}] {self.text}"
 
class AssessmentSubmission:
    """Stores a completed assessment submission"""
    def __init__(self, id, municipality_id, answers):
        self.id = id
        self.municipality_id = municipality_id
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.answers = answers  # list of (question_id, value) tuples
 
    def __str__(self):
        return f"Submission #{self.id} for Municipality {self.municipality_id} on {self.timestamp}"
 
class ScoredReport:
    """Stores the scored results of an assessment"""
    def __init__(self, id, submission_id, total_score, category_scores, gaps, action_plan):
        self.id = id
        self.submission_id = submission_id
        self.total_score = total_score
        self.category_scores = category_scores  # dictionary of category -> score
        self.gaps = gaps                         # list of identified gaps
        self.action_plan = action_plan           # list of recommended actions
 
    def __str__(self):
        return f"Report #{self.id} | Total Score: {self.total_score:.1f}%"
 
# DATABASE FUNCTIONS

# CONNECT TO DB
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="cyber_assessment",
        user="postgres",
        password="post4word"
    )

# SAVE TO DB
def save_assessment_to_db(municipality_id, total_score, user_answers):
    conn = get_db_connection()
    cur = conn.cursor()
    
    answers_json = json.dumps(user_answers)
    
    query = """
    INSERT INTO assessments (municipality_id, total_score, answers)
    VALUES (%s, %s, %s);
    """
    
    cur.execute(query, (municipality_id, total_score, answers_json))
    
    conn.commit()
    cur.close()
    conn.close()

# ESTABLISHING DATA

# Database questions
def fetch_questions():
    conn = get_db_connection()
    # RealDictCursor allows column access by name (row['category'])
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    cur.execute("SELECT * FROM questions;")
    rows = cur.fetchall()
    
    db_questions = []
    for r in rows:
        # Create Question objects using data from table
        db_questions.append(Question(
            r['id'], 
            r['category'], 
            r['question_text'], 
            r['weight'], 
            ["Yes", "Partial", "No", "Unknown"],
            r['gap_description'],
            r['recommendation']
        ))
        
    cur.close()
    conn.close()
    return db_questions

# Get questions for the assessment
QUESTIONS = fetch_questions()
 
# Database municipalities
def fetch_municipalities():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    cur.execute("SELECT * FROM municipalities ORDER BY id;")
    rows = cur.fetchall()
    
    db_municipalities = []
    for r in rows:
        db_municipalities.append(Municipality(
            r['id'], 
            r['name'], 
            r['county'], 
            r['population'], 
            r['contact_email']
        ))
        
    cur.close()
    conn.close()
    return db_municipalities

# Get municipalities
MUNICIPALITIES = fetch_municipalities()

# Database submissions
def fetch_submissions():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    cur.execute("SELECT * FROM assessments ORDER BY id ASC;")
    rows = cur.fetchall()
    
    db_submissions = []
    for r in rows:
        db_submissions.append(AssessmentSubmission(
            r['id'], 
            r['municipality_id'], 
            r['answers']
        ))
        
    cur.close()
    conn.close()
    return db_submissions

# Get submissions
all_submissions = fetch_submissions()

# Fill reports with database submissions
def populate_reports_from_submissions():
    generated_reports = []
    for sub in all_submissions:
        # 1. Run the scoring math on the saved answers[cite: 1, 2]
        cat_scores, gaps = calculate_scores(sub.answers, QUESTIONS)
        
        # 2. Calculate the total[cite: 1, 2]
        total = sum(cat_scores.values()) / len(cat_scores) if cat_scores else 0
        
        # 3. Generate the plan[cite: 1, 2]
        plan = generate_action_plan(gaps)
        
        # 4. Create the report object and add to the list[cite: 1, 2]
        report_id = len(generated_reports) + 1
        generated_reports.append(ScoredReport(
            report_id, sub.id, total, cat_scores, gaps, plan
        ))
    return generated_reports

# Score mapping for answers
ANSWER_SCORES = {
    "Yes": 4,
    "Partial": 2,
    "No": 1,
    "Unknown": 1
}

# SCORE REPORTING FUNCTIONS
 
def calculate_scores(user_answers, questions):
    """Calculate category scores and identify gaps from user answers"""
    category_totals = {}      # stores total weighted score per category
    category_max = {}         # stores max possible score per category
    gaps_and_recs = []      # stores gaps of and recommendations for low-scoring areas
 
    # Build a quick lookup dictionary for questions by ID
    question_lookup = {q.id: q for q in questions}
 
    for (question_id, answer_value) in user_answers:
        question = question_lookup[question_id]
        weight = question.weight
        score = answer_value
        category = question.category
 
        # Add weighted score to category total
        if category not in category_totals:
            category_totals[category] = 0
            category_max[category] = 0
 
        category_totals[category] += score * weight
        category_max[category] += 4 * weight  # 4 is the max possible score
 
        # Flag as a gap if score is low, and add recommendation
        if score <= 2:
            gaps_and_recs.append((question.gap_description, question.recommendation))
 
    # Convert totals to percentages
    category_scores = {}
    for category in category_totals:
        if category_max[category] > 0:
            category_scores[category] = (category_totals[category] / category_max[category]) * 100
        else:
            category_scores[category] = 0
 
    return category_scores, gaps_and_recs
 
def generate_action_plan(gaps_and_recs):
    """Generate a list of recommended actions based on identified gaps"""
 
    action_plan = []
    for gap, rec in gaps_and_recs:
        if rec:
            action_plan.append(rec)
        else:
            action_plan.append(f"Review and address: {gap}")
 
    return action_plan
 
# TUI MENU FUNCTIONS
 
def print_header():
    print("============================================================")
    print("   Indiana Municipality Cybersecurity Self-Assessment Tool  ")
    print("============================================================")
 
def print_main_menu():
    print("\n-------- MAIN MENU --------")
    print("1. Start New Assessment")
    print("2. View Previous Reports")
    print("3. Update Existing Assessment")
    print("4. Manage Municipality Profile")
    print("5. Exit")
    print("---------------------------")
 
def print_report_menu():
    print("\n-------- REPORTS MENU --------")
    print("1. View Latest Report")
    print("2. View All Reports")
    print("3. Back to Main Menu")
    print("------------------------------")
 
def print_municipality_menu():
    print("\n-------- MUNICIPALITY MENU --------")
    print("1. View Municipality List")
    print("2. Back to Main Menu")
    print("-----------------------------------")
 
# PROGRAM FUNCTIONS
 
def select_municipality():
    """Let the user pick a municipality from the list"""
    print("\n-------- SELECT MUNICIPALITY --------")
    for m in MUNICIPALITIES:
        print(f"{m.id}. {m.name} ({m.county} County)")
    print("-------------------------------------")
 
    while True:
        choice = input("Enter municipality number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(MUNICIPALITIES):
            return MUNICIPALITIES[int(choice) - 1]
        else:
            print("[ERROR] Invalid choice. Please try again.")
 
 
def run_assessment(municipality):
    """Walk the user through all assessment questions and collect answers"""
    print(f"\n--- Starting Assessment for {municipality.name} ---")
    print("Answer each question: Yes / Partial / No / Unknown\n")
 
    user_answers = []
    total_questions = len(QUESTIONS)
 
    for i, question in enumerate(QUESTIONS):
        # Show progress
        print(f"Progress: [{i + 1}/{total_questions}]")
        print(f"Category: {question.category}")
        print(f"Question: {question.text}")
        print("Options: Yes / Partial / No / Unknown")
 
        while True:
            answer = input("Your answer: ").strip().capitalize()
            if answer in ANSWER_SCORES:
                user_answers.append((question.id, ANSWER_SCORES[answer]))
                break
            else:
                print("[ERROR] Please enter: Yes, Partial, No, or Unknown")
 
        print()  # blank line between questions
 
    return user_answers
 
def submit_assessment(municipality, user_answers):
    """Score the answers and generate a report"""
    # Create submission
    submission_id = len(all_submissions) + 1
    submission = AssessmentSubmission(submission_id, municipality.id, user_answers)
    all_submissions.append(submission)
 
    # Calculate scores
    category_scores, gaps = calculate_scores(user_answers, QUESTIONS)
 
    # Calculate overall total score
    if category_scores:
        total_score = sum(category_scores.values()) / len(category_scores)
    else:
        total_score = 0
 
    # Save assessment to database
    save_assessment_to_db(municipality.id, total_score, user_answers)

    # Generate action plan
    action_plan = generate_action_plan(gaps)
 
    # Create report
    report_id = len(all_reports) + 1
    report = ScoredReport(report_id, submission_id, total_score, category_scores, gaps, action_plan)
    all_reports.append(report)
 
    return report
 
def display_report(report):
    """Print a report to the screen"""
    print("\n============================================================")
    print("                   ASSESSMENT REPORT")
    print("============================================================")
    print(f"Report ID:    #{report.id}")
    print(f"Submission:   #{report.submission_id}")
    print(f"Total Score:  {report.total_score:.1f}%")
 
    # Score interpretation
    if report.total_score >= 75:
        print("Rating: GOOD - Your municipality has solid cybersecurity practices.")
    elif report.total_score >= 50:
        print("Rating: FAIR - Some improvements are needed.")
    else:
        print("Rating: POOR - Significant cybersecurity gaps were identified.")
 
    print("\n--- Category Scores ---")
    for category, score in report.category_scores.items():
        print(f"  {category}: {score:.1f}%")
 
    print("\n--- Identified Gaps ---")
    if report.gaps:
        for gap in report.gaps:
            print(f"  - {gap[0]}")
    else:
        print("  No significant gaps identified!")
 
    print("\n--- Action Plan ---")
    if report.action_plan:
        for i, action in enumerate(report.action_plan, 1):
            print(f"  {i}. {action}")
    else:
        print("  No actions required at this time.")
 
    print("============================================================")
 
def view_reports():
    """Let the user browse previous reports"""
    if not all_reports:
        print("\n[INFO] No reports found. Complete an assessment first.")
        return
 
    print_report_menu()
    choice = input("Enter your choice: ").strip()
 
    if choice == "1":
        # View latest report
        display_report(all_reports[-1])
    elif choice == "2":
        # View all reports
        for report in all_reports:
            display_report(report)
    elif choice == "3":
        return
    else:
        print("[ERROR] Invalid choice.")
 
def update_assessment():
    """Let the user redo an assessment to update their score"""
    if not all_submissions:
        print("\n[INFO] No previous assessments found.")
        return
 
    print("\n--- Previous Submissions ---")
    for submission in all_submissions:
        print(f"  Submission #{submission.id} | Municipality ID: {submission.municipality_id} | {submission.timestamp}")
 
    print("\nTo update, please start a new assessment from the main menu.")
    print("Your new results will be saved alongside previous submissions.")
 
def manage_municipality():
    """Show municipality management options"""
    print_municipality_menu()
    choice = input("Enter your choice: ").strip()
 
    if choice == "1":
        print("\n--- Municipality List ---")
        for m in MUNICIPALITIES:
            print(f"  {m.id}. {m}")
    elif choice == "2":
        return
    else:
        print("[ERROR] Invalid choice.")
 
# Get reports
all_reports = populate_reports_from_submissions()

# MAIN PROGRAM
 
def main():
    
    print_header()
 
    while True:
        print_main_menu()
        choice = input("Enter your choice (1-5): ").strip()
 
        if choice == "1":
            # Start new assessment
            municipality = select_municipality()
            user_answers = run_assessment(municipality)
            report = submit_assessment(municipality, user_answers)
            display_report(report)
 
        elif choice == "2":
            # View previous reports
            view_reports()
 
        elif choice == "3":
            # Update existing assessment
            update_assessment()
 
        elif choice == "4":
            # Manage municipality profile
            manage_municipality()
 
        elif choice == "5":
            print("\n[INFO] Thank you for using the Cybersecurity Self-Assessment Tool.")
            print("Stay secure!\n")
            break
 
        else:
            print("\n[ERROR] Invalid choice. Please enter a number between 1 and 5.")
 
 
if __name__ == "__main__":
    main()

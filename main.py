#    Indiana Municipality Cybersecurity Self-Assessment Tool
#    main.py
#    SDEV 220 Final Project
from datetime import datetime
 
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
    def __init__(self, id, category, text, weight, options, gap_description):
        self.id = id
        self.category = category
        self.text = text
        self.weight = weight
        self.options = options  # list of answer options
        self.gap_description = gap_description  # used if score is low
 
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
 
# SAMPLE DATA
 
# Sample questions for the assessment
QUESTIONS = [
    Question(1, "Identity Protection",     "Does your municipality use multi-factor authentication?",          2, ["Yes", "Partial", "No", "Unknown"], "No multi-factor authentication in place"),
    Question(2, "Incident Response",       "Do you have a documented incident response plan?",                2, ["Yes", "Partial", "No", "Unknown"], "No incident response plan"),
    Question(3, "Patch Management",        "Are software patches applied within 30 days of release?",         2, ["Yes", "Partial", "No", "Unknown"], "Patch management process is lacking"),
    Question(4, "Third-Party Vendor Risk", "Are third-party vendors required to meet security standards?",    1, ["Yes", "Partial", "No", "Unknown"], "Third-party vendor risk not managed"),
    Question(5, "Data Protection",         "Is sensitive data encrypted both in storage and in transit?",     2, ["Yes", "Partial", "No", "Unknown"], "Data encryption not fully implemented"),
    Question(6, "Compliance",              "Does your municipality follow any cybersecurity compliance framework?", 1, ["Yes", "Partial", "No", "Unknown"], "No compliance framework followed"),
    Question(7, "Security Testing",        "Has your municipality conducted a security audit in the past year?", 1, ["Yes", "Partial", "No", "Unknown"], "No recent security testing performed"),
]
 
# Score mapping for answers
ANSWER_SCORES = {
    "Yes": 4,
    "Partial": 2,
    "No": 1,
    "Unknown": 1
}
 
# Sample municipalities to choose from
MUNICIPALITIES = [
    Municipality(1, "Warsaw",       "Kosciusko", 15000, "contact@warsaw.in.gov"),
    Municipality(2, "Plymouth",     "Marshall",   10000, "contact@plymouth.in.gov"),
    Municipality(3, "Wabash",       "Wabash",     10000, "contact@wabash.in.gov"),
    Municipality(4, "Logansport",   "Cass",       18000, "contact@logansport.in.gov"),
    Municipality(5, "Other",        "Unknown",    0,     "N/A"),
]
 
# Store all submissions and reports in memory
all_submissions = []
all_reports = []
 
# SCORE REPORTING FUNCTIONS
 
def calculate_scores(user_answers, questions):
    """Calculate category scores and identify gaps from user answers"""
    category_totals = {}      # stores total weighted score per category
    category_max = {}         # stores max possible score per category
    identified_gaps = []      # stores descriptions of low-scoring areas
 
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
 
        # Flag as a gap if score is low
        if score <= 2:
            identified_gaps.append(question.gap_description)
 
    # Convert totals to percentages
    category_scores = {}
    for category in category_totals:
        if category_max[category] > 0:
            category_scores[category] = (category_totals[category] / category_max[category]) * 100
        else:
            category_scores[category] = 0
 
    return category_scores, identified_gaps
 
def generate_action_plan(gaps):
    """Generate a list of recommended actions based on identified gaps"""
 
    # Recommendations mapped to gap descriptions
    recommendations = {
        "No multi-factor authentication in place":       "Implement multi-factor authentication for all staff accounts immediately.",
        "No incident response plan":                     "Develop and document a formal incident response plan with assigned roles.",
        "Patch management process is lacking":           "Establish a patch management policy to apply updates within 30 days.",
        "Third-party vendor risk not managed":           "Create a vendor risk management policy and require security attestations.",
        "Data encryption not fully implemented":         "Encrypt all sensitive data at rest and in transit using current standards.",
        "No compliance framework followed":              "Adopt a cybersecurity framework such as NIST CSF or CIS Controls.",
        "No recent security testing performed":          "Schedule an annual security audit or penetration test.",
    }
 
    action_plan = []
    for gap in gaps:
        if gap in recommendations:
            action_plan.append(recommendations[gap])
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
            print(f"  - {gap}")
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

#    Indiana Municipality Cybersecurity Self-Assessment Tool
#    main.py
#    SDEV 220 Final Project
#    Falls back to local data if database is unavailable.

import os
import json
from datetime import datetime

# database is optional — the app runs offline if it is not installed
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


# ============================================================
# CONFIGURATION
# ============================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


# ============================================================
# DATA MODELS
# ============================================================

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
    """Stores a single assessment question (aligned to NIST CSF)"""
    def __init__(self, id, domain, subdomain, text, weight, guidance, indiana_reference):
        self.id = id                              # e.g. "PR-AC-2"
        self.domain = domain                      # NIST CSF function
        self.subdomain = subdomain                # NIST CSF category
        self.text = text
        self.weight = weight                      # 2 = medium, 3 = high
        self.guidance = guidance                  # plain-language hint
        self.indiana_reference = indiana_reference

    def __str__(self):
        return f"[{self.domain} / {self.subdomain}] {self.text}"


class Recommendation:
    """Stores a recommendation triggered by a No or Partial answer"""
    def __init__(self, question_id, trigger_answer, priority, effort, title, action):
        self.question_id = question_id
        self.trigger_answer = trigger_answer      # "No" or "Partial"
        self.priority = priority                  # critical | high | medium
        self.effort = effort                      # low | medium | high
        self.title = title
        self.action = action


class AssessmentSubmission:
    """Stores a completed assessment submission"""
    def __init__(self, id, municipality_id, answers):
        self.id = id
        self.municipality_id = municipality_id
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.answers = answers                    # list of (question_id, answer_text) tuples

    def __str__(self):
        return f"Submission #{self.id} for Municipality {self.municipality_id} on {self.timestamp}"


class ScoredReport:
    """Stores the scored results of an assessment"""
    def __init__(self, id, submission_id, total_score, maturity_level,
                 domain_scores, gaps, action_plan):
        self.id = id
        self.submission_id = submission_id
        self.total_score = total_score
        self.maturity_level = maturity_level      # 1=Partial, 2=Risk Informed, 3=Repeatable, 4=Adaptive
        self.domain_scores = domain_scores        # dict: domain -> score
        self.gaps = gaps                          # list of question IDs answered No/Partial
        self.action_plan = action_plan            # list of Recommendation objects

    def __str__(self):
        return f"Report #{self.id} | Score: {self.total_score:.1f}% | Level {self.maturity_level}"


# ============================================================
# ANSWER SCORING
# ============================================================

# Maps user answers to numeric scores (out of 4)
ANSWER_SCORES = {
    "Yes":     4,
    "Partial": 2,
    "No":      0,
    "N/A":     None,  # excluded from scoring
}

# NIST CSF maturity tiers
MATURITY_LEVELS = {
    1: ("Partial",        0,  39, "Significant cybersecurity gaps require immediate attention."),
    2: ("Risk Informed", 40,  59, "Some foundational controls in place but important gaps remain."),
    3: ("Repeatable",    60,  79, "Solid cybersecurity foundations and documented practices."),
    4: ("Adaptive",      80, 100, "Strong, continuously improving cybersecurity practices."),
}

# Relative weight of each NIST CSF domain (must sum to 100)
DOMAIN_WEIGHTS = {
    "Identify": 15,
    "Protect":  35,
    "Detect":   15,
    "Respond":  20,
    "Recover":  15,
}


# ============================================================
# SAMPLE MUNICIPALITIES
# ============================================================

MUNICIPALITIES = [
    Municipality(1, "Warsaw",     "Kosciusko", 15000, "contact@warsaw.in.gov"),
    Municipality(2, "Plymouth",   "Marshall",  10000, "contact@plymouth.in.gov"),
    Municipality(3, "Wabash",     "Wabash",    10000, "contact@wabash.in.gov"),
    Municipality(4, "Logansport", "Cass",      18000, "contact@logansport.in.gov"),
    Municipality(5, "Other",      "Unknown",       0, "N/A"),
]


# ============================================================
# FALLBACK QUESTION BANK (used if Supabase unavailable)
# 31 questions aligned to NIST CSF, adapted for small Indiana municipalities
# ============================================================

FALLBACK_QUESTIONS = [
    # IDENTIFY — Asset Management
    Question("ID-AM-1", "Identify", "Asset Management", "Does your municipality maintain an up-to-date inventory of all hardware devices connected to your network?", 2, "Includes desktops, laptops, printers, routers, and any device that connects to city systems.", "IN-ISAC Asset Inventory Baseline"),
    Question("ID-AM-2", "Identify", "Asset Management", "Does your municipality maintain an inventory of all software applications installed on city-owned devices?", 2, "Includes operating systems, productivity software, and cloud services paid for by the city.", "IN-ISAC Asset Inventory Baseline"),
    Question("ID-AM-3", "Identify", "Asset Management", "Has your municipality identified and documented which systems handle sensitive data (resident PII, financial records, law enforcement data)?", 3, "Sensitive data includes names, addresses, SSNs, payment card data, and criminal records.", "Indiana Data Protection Act"),
    # IDENTIFY — Governance
    Question("ID-GV-1", "Identify", "Governance", "Does your municipality have a written cybersecurity policy reviewed or updated in the last two years?", 3, "Should cover acceptable use, password requirements, and incident reporting at minimum.", "Indiana IC 5-22-17"),
    Question("ID-GV-2", "Identify", "Governance", "Is there a designated person (staff or vendor) responsible for cybersecurity decisions in your municipality?", 2, "Could be the IT coordinator, city administrator, or a contracted IT service provider.", None),
    Question("ID-GV-3", "Identify", "Governance", "Has the city council formally approved a cybersecurity budget or allocated resources for cybersecurity improvements?", 2, "Even a small dedicated budget line counts as a Yes.", None),
    # IDENTIFY — Risk Assessment
    Question("ID-RA-1", "Identify", "Risk Assessment", "Has your municipality conducted a formal cybersecurity risk assessment in the last three years?", 3, "Includes assessments through Indiana Cybertrack, a third party, or an internal NIST/CIS review.", "Indiana Cybertrack Program"),
    Question("ID-RA-2", "Identify", "Risk Assessment", "Does your municipality have a process to evaluate cybersecurity risks from third-party vendors and service providers?", 2, "For example, reviewing contracts of cloud vendors and IT managed service providers for security obligations.", None),

    # PROTECT — Access Control
    Question("PR-AC-1", "Protect", "Access Control", "Are unique user accounts required for every employee who accesses city systems? (No shared accounts?)", 3, "Each person should log in with their own credentials. Shared accounts are a high-risk practice.", None),
    Question("PR-AC-2", "Protect", "Access Control", "Is Multi-Factor Authentication (MFA) enabled for email and remote access to city systems?", 3, "MFA is the single most effective control against account takeover.", "CISA MFA Guidance"),
    Question("PR-AC-3", "Protect", "Access Control", "Are employee accounts disabled or removed promptly when staff leave the municipality?", 2, "Accounts of former employees should be deactivated within 24 hours of departure.", None),
    Question("PR-AC-4", "Protect", "Access Control", "Do employees only have access to the systems and data they need to perform their job? (Principle of least privilege)", 2, "A parks employee should not have access to financial or law enforcement systems.", None),
    # PROTECT — Awareness & Training
    Question("PR-AT-1", "Protect", "Awareness & Training", "Do all city employees receive cybersecurity awareness training at least once per year?", 3, "Training can be online (CISA free modules), in-person, or through your IT vendor.", "CISA Free Cybersecurity Training"),
    Question("PR-AT-2", "Protect", "Awareness & Training", "Are employees trained to recognize and report phishing emails?", 2, "Phishing is the #1 attack vector for ransomware in local government.", None),
    # PROTECT — Data Security
    Question("PR-DS-1", "Protect", "Data Security", "Are backups of critical city data performed regularly (at least weekly) and stored separately from primary systems?", 3, "Follow the 3-2-1 rule: 3 copies, 2 different media, 1 offsite. Backups on the same network are vulnerable to ransomware.", None),
    Question("PR-DS-2", "Protect", "Data Security", "Are backup restorations tested at least once per year to confirm data can be recovered?", 3, "An untested backup is not a backup. A successful restore test is the only way to verify your recovery capability.", None),
    Question("PR-DS-3", "Protect", "Data Security", "Is sensitive data encrypted when stored on laptops, USB drives, or portable devices?", 2, "BitLocker (Windows) and FileVault (Mac) are built-in, free encryption tools.", "Indiana Data Breach Notification Law (IC 24-4.9)"),
    # PROTECT — Information Protection
    Question("PR-IP-1", "Protect", "Information Protection", "Are operating systems and software on city devices kept up to date with security patches?", 3, "Patching should occur within 30 days of a critical update release. Unpatched systems are the most common ransomware entry point.", "CISA Known Exploited Vulnerabilities Catalog"),
    Question("PR-IP-2", "Protect", "Information Protection", "Does your municipality use antivirus or endpoint protection software on all city-owned devices?", 2, "Modern endpoint protection (EDR) is preferred over traditional antivirus.", None),
    Question("PR-IP-3", "Protect", "Information Protection", "Is there a firewall protecting the boundary between your city network and the internet?", 2, "A managed firewall from an IT vendor provides significantly stronger protection than a basic ISP router.", None),
    Question("PR-IP-4", "Protect", "Information Protection", "Is guest Wi-Fi (for public or visitor use) separated from the internal city network?", 2, "Public Wi-Fi on the same network as city systems is a critical vulnerability.", None),

    # DETECT — Continuous Monitoring
    Question("DE-CM-1", "Detect", "Continuous Monitoring", "Does your municipality have a way to detect unauthorized access or unusual activity on city systems?", 3, "At minimum, Windows Event Logs and firewall logs should be reviewed regularly.", "CISA Free Vulnerability Scanning (CyHy)"),
    Question("DE-CM-2", "Detect", "Continuous Monitoring", "Are security logs reviewed on a regular basis (at least monthly)?", 2, "Logs that are never reviewed provide no detection value.", None),
    Question("DE-CM-3", "Detect", "Continuous Monitoring", "Has your municipality enrolled in CISA's free Cyber Hygiene (CyHy) vulnerability scanning service?", 2, "CyHy is a free automated external vulnerability scan offered by CISA to all SLTT governments.", "CISA CyHy Program — free for all Indiana municipalities"),

    # RESPOND — Response Planning
    Question("RS-RP-1", "Respond", "Response Planning", "Does your municipality have a written Incident Response Plan (IRP) describing what to do in the event of a cyberattack?", 3, "An IRP should identify who to call, what systems to isolate, and how to engage law enforcement. CISA provides free templates.", "Indiana IDHS Incident Response Resources"),
    Question("RS-RP-2", "Respond", "Response Planning", "Has your municipality conducted a tabletop exercise to practice responding to a cyber incident in the last two years?", 2, "A tabletop is a facilitated discussion walking through a simulated attack scenario.", "IN-ISAC Tabletop Exercise Program"),
    # RESPOND — Communications
    Question("RS-CO-1", "Respond", "Communications", "Does your municipality know who to contact at the state and federal level in the event of a cyberattack?", 2, "Key contacts: Indiana IDHS (800-800-3578), MS-ISAC (866-787-4722), CISA Region 5. Print and store offline.", "Indiana IDHS Cyber Division"),
    Question("RS-CO-2", "Respond", "Communications", "Does your municipality have cyber liability insurance coverage?", 2, "Cyber insurance can cover ransom payments, recovery costs, legal fees, and resident notification.", None),

    # RECOVER — Recovery Planning
    Question("RC-RP-1", "Recover", "Recovery Planning", "Does your municipality have a Continuity of Operations Plan (COOP) or Disaster Recovery Plan addressing cyber incidents?", 3, "A COOP defines how the municipality continues essential services while IT systems are down.", "Indiana IDHS COOP Planning Guide"),
    Question("RC-RP-2", "Recover", "Recovery Planning", "Have Recovery Time Objectives (RTOs) been defined for critical city systems?", 2, "Examples: 911 dispatch = 0 hours, financial system = 24 hours, parks scheduling = 1 week.", None),
    # RECOVER — Improvements
    Question("RC-IM-1", "Recover", "Improvements", "After a security incident or near-miss, does your municipality conduct a post-incident review to identify lessons learned?", 2, "Even minor incidents (a phishing click, a lost laptop) are opportunities to improve.", None),
]


# ============================================================
# FALLBACK RECOMMENDATIONS (used if Supabase unavailable)
# One per question, triggered by No or Partial answers
# ============================================================

FALLBACK_RECOMMENDATIONS = [
    Recommendation("ID-AM-1", "No", "high", "low", "Create a hardware asset inventory", "Use a free spreadsheet to list every device connected to city systems: computers, servers, printers, routers. Include make, model, serial number, and location. Review quarterly."),
    Recommendation("ID-AM-2", "No", "high", "low", "Create a software asset inventory", "Document all software installed on city devices, including version numbers and license expiration dates. Note any end-of-life software for high-priority replacement."),
    Recommendation("ID-AM-3", "No", "critical", "medium", "Identify and document where sensitive data lives", "Walk through each department and list every system that stores resident PII, financial records, or law enforcement information. Required for Indiana data breach notification compliance."),
    Recommendation("ID-GV-1", "No", "high", "medium", "Adopt a written cybersecurity policy", "Draft a one- to two-page policy covering acceptable use, password requirements, remote access rules, and incident reporting. Have the city council formally adopt it. CISA offers free templates."),
    Recommendation("ID-GV-2", "No", "high", "low", "Designate a cybersecurity point of contact", "Assign one person — even part-time — as the go-to for cybersecurity decisions. Document their name and contact info and share with all staff."),
    Recommendation("ID-GV-3", "No", "medium", "medium", "Establish a cybersecurity budget line", "Present council with a minimal cybersecurity budget proposal. Even $2,000–$5,000/year covers critical tools. Frame as risk management, not IT spending."),
    Recommendation("ID-RA-1", "No", "high", "medium", "Request a free assessment through Indiana Cybertrack", "Apply to Indiana's Cybertrack program for a free seven-week cybersecurity assessment by Purdue University. Best investment of time for a municipality starting from scratch."),
    Recommendation("ID-RA-2", "No", "medium", "medium", "Add cybersecurity requirements to vendor contracts", "Review IT vendor contracts. Add a clause requiring 72-hour breach notification and reasonable security practices. IN-ISAC offers sample contract language."),
    Recommendation("PR-AC-1", "No", "critical", "low", "Eliminate shared accounts immediately", "Create individual accounts for every staff member. Remove or disable shared accounts like 'admin' or 'office'. Foundational prerequisite for all other access controls."),
    Recommendation("PR-AC-2", "No", "critical", "low", "Enable MFA on email and remote access immediately", "MFA is the single most effective control against ransomware entry. Enable for Microsoft 365 or Google Workspace (free at the account level), VPN, and remote desktop. Target: 30 days."),
    Recommendation("PR-AC-3", "No", "high", "low", "Create an offboarding checklist for account deactivation", "Add account deactivation to your HR offboarding process. Accounts should be disabled within 24 hours and deleted within 30 days."),
    Recommendation("PR-AC-4", "No", "high", "medium", "Implement least privilege access", "Review what systems each employee can access. Remove access unrelated to their role. Ensure no standard employee has local administrator rights."),
    Recommendation("PR-AT-1", "No", "critical", "low", "Enroll all employees in free cybersecurity awareness training", "CISA offers a free training catalog requiring no registration. Assign phishing awareness and password hygiene modules. Document completion as an annual requirement."),
    Recommendation("PR-AT-2", "No", "critical", "low", "Train employees to recognize and report phishing emails", "Deploy CISA's free phishing awareness training. Establish a simple reporting mechanism (dedicated email or button in the email client)."),
    Recommendation("PR-DS-1", "No", "critical", "medium", "Implement the 3-2-1 backup rule", "Set up automated backups: 3 copies, 2 different media types, 1 copy offsite. Cloud backup costs $5–$50/month for most small municipalities. Primary defense against ransomware."),
    Recommendation("PR-DS-2", "No", "critical", "low", "Test backup restoration at least once per year", "Pick a non-critical system and verify it can be fully restored from backup. Document the result and time required. An untested backup provides no guarantee of recovery."),
    Recommendation("PR-DS-3", "No", "high", "low", "Enable encryption on all laptops and portable devices", "Enable BitLocker (Windows) or FileVault (Mac) — both built in and free. Protects resident data if a device is lost or stolen and ensures Indiana breach notification compliance."),
    Recommendation("PR-IP-1", "No", "critical", "medium", "Establish a monthly patching process", "Enable automatic updates on all devices. Designate the second Tuesday of each month for patching servers and manual systems. Cross-reference CISA's KEV catalog for urgent patches."),
    Recommendation("PR-IP-2", "No", "critical", "low", "Deploy free or low-cost endpoint protection on all devices", "MS-ISAC provides free CrowdStrike Falcon EDR to SLTT governments. At minimum, ensure Windows Defender is active and updated on all Windows devices."),
    Recommendation("PR-IP-3", "No", "critical", "medium", "Install a firewall between city systems and the internet", "At minimum, enable your ISP router's built-in firewall. For better protection, deploy a managed firewall (pfSense, SonicWall, or Fortinet) through an IT vendor."),
    Recommendation("PR-IP-4", "No", "critical", "low", "Separate public Wi-Fi from city internal network immediately", "Configure a separate SSID for guest Wi-Fi, isolated from the internal network via VLAN. Typically a configuration change costing nothing."),
    Recommendation("DE-CM-1", "No", "high", "medium", "Enable security logging and free CISA scanning", "Enable Windows Security Event logging. Enroll in CISA CyHy for free external vulnerability scanning. Use MS-ISAC's free MDBR to block malicious DNS. Three steps, no cost."),
    Recommendation("DE-CM-2", "No", "high", "low", "Assign someone to review security logs monthly", "Designate IT contact (staff or vendor) to review Windows Event Logs and firewall logs monthly. Focus on failed logins, account lockouts, and unusual outbound connections."),
    Recommendation("DE-CM-3", "No", "high", "low", "Enroll in CISA's free CyHy vulnerability scanning service", "CyHy scans your public-facing systems weekly and emails a vulnerability report. Enrollment takes 15 minutes. One of the highest-value security actions available at no cost."),
    Recommendation("RS-RP-1", "No", "critical", "medium", "Create a written Incident Response Plan using the free CISA template", "Create a one- to two-page plan covering who to call, what systems to isolate, and how to communicate with residents. Print and store offline — ransomware blocks digital access."),
    Recommendation("RS-RP-2", "No", "high", "medium", "Schedule a free tabletop exercise with CISA or IN-ISAC", "Contact CISA Region 5 or IN-ISAC for a free facilitated tabletop. Or run CISA's ready-made exercise packages in two hours. Dramatically improves real-incident response."),
    Recommendation("RS-CO-1", "No", "critical", "low", "Print and post emergency cybersecurity contacts", "Create a one-page contact card: Indiana IDHS (800-800-3578), MS-ISAC (866-787-4722), CISA Region 5 (312-353-7272), FBI IC3, and your IT vendor. Post physically."),
    Recommendation("RS-CO-2", "No", "medium", "medium", "Obtain cyber liability insurance coverage", "Contact your municipal insurance carrier about adding a cyber liability rider. Premiums for small municipalities range $1,500–$5,000/year and cover ransomware, recovery, and legal fees."),
    Recommendation("RC-RP-1", "No", "high", "high", "Create a Continuity of Operations Plan for cyber incidents", "Use the FEMA COOP template to document how essential services continue when IT is unavailable. Identify manual fallback procedures for water, utilities, 911 dispatch, and payroll."),
    Recommendation("RC-RP-2", "No", "medium", "low", "Define Recovery Time Objectives for critical systems", "Document maximum acceptable downtime for each critical system. Examples: 911 dispatch = 0 hours, financial system = 24 hours. RTOs drive recovery prioritization."),
    Recommendation("RC-IM-1", "No", "medium", "low", "Establish a post-incident review process", "After any incident — even minor ones like a clicked phishing link — hold a brief review meeting and document what happened, how it was detected, and what should change."),
]


# ============================================================
# DATABASE LAYER (Supabase)
# ============================================================

def get_supabase_client():
    """Return a Supabase client, or None if unavailable."""
    if not SUPABASE_AVAILABLE or not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"[WARN] Could not connect to Supabase: {e}")
        return None


def load_questions(supabase):
    """Load questions from Supabase, falling back to local data on failure."""
    if supabase is None:
        return FALLBACK_QUESTIONS
    try:
        response = supabase.table("questions").select("*").execute()
        if not response.data:
            return FALLBACK_QUESTIONS
        questions = []
        for row in response.data:
            questions.append(Question(
                row["id"], row["domain"], row["subdomain"], row["text"],
                row["weight"], row.get("guidance"), row.get("indiana_reference")
            ))
        return questions
    except Exception as e:
        print(f"[WARN] Could not load questions from Supabase: {e}. Using fallback.")
        return FALLBACK_QUESTIONS


def load_recommendations(supabase):
    """Load recommendations from Supabase, falling back to local data on failure."""
    if supabase is None:
        return FALLBACK_RECOMMENDATIONS
    try:
        response = supabase.table("recommendations").select("*").execute()
        if not response.data:
            return FALLBACK_RECOMMENDATIONS
        recs = []
        for row in response.data:
            recs.append(Recommendation(
                row["question_id"], row["trigger_answer"], row["priority"],
                row["effort"], row["title"], row["action"]
            ))
        return recs
    except Exception as e:
        print(f"[WARN] Could not load recommendations from Supabase: {e}. Using fallback.")
        return FALLBACK_RECOMMENDATIONS


def save_submission_and_report(supabase, municipality, submission, report):
    """Persist submission and report to Supabase. Silently no-op if unavailable."""
    if supabase is None:
        return
    try:
        # Convert answers list of tuples to dict for JSONB storage
        answers_dict = {qid: ans for qid, ans in submission.answers}
        sub_response = supabase.table("assessments").insert({
            "municipality": municipality.name,
            "population": str(municipality.population),
            "answers": answers_dict,
        }).execute()
        sub_id = sub_response.data[0]["id"] if sub_response.data else None

        supabase.table("reports").insert({
            "assessment_id": sub_id,
            "total_score": round(report.total_score, 2),
            "maturity_level": report.maturity_level,
            "domain_scores": report.domain_scores,
            "gaps": report.gaps,
            "recommendations": [
                {"question_id": r.question_id, "title": r.title,
                 "priority": r.priority, "action": r.action}
                for r in report.action_plan
            ],
        }).execute()
        print("[INFO] Report saved to Supabase.")
    except Exception as e:
        print(f"[WARN] Could not save to Supabase: {e}. Report exists in memory only.")


# ============================================================
# SCORING FUNCTIONS
# ============================================================

def calculate_scores(user_answers, questions):
    """Calculate weighted domain scores and identify gaps."""
    domain_totals = {}
    domain_max = {}
    gaps = []

    question_lookup = {q.id: q for q in questions}

    for question_id, answer_text in user_answers:
        if answer_text == "N/A":
            continue  # excluded from scoring
        question = question_lookup[question_id]
        score = ANSWER_SCORES[answer_text]
        domain = question.domain
        weight = question.weight

        domain_totals.setdefault(domain, 0)
        domain_max.setdefault(domain, 0)
        domain_totals[domain] += score * weight
        domain_max[domain] += 4 * weight  # 4 = max score

        if answer_text in ("No", "Partial"):
            gaps.append((question_id, answer_text))

    # Convert each domain to a percentage
    domain_scores = {}
    for domain in domain_totals:
        if domain_max[domain] > 0:
            domain_scores[domain] = (domain_totals[domain] / domain_max[domain]) * 100
        else:
            domain_scores[domain] = 0

    return domain_scores, gaps


def calculate_total_score(domain_scores):
    """Combine domain scores using NIST CSF domain weights."""
    total = 0
    used_weight = 0
    for domain, weight in DOMAIN_WEIGHTS.items():
        if domain in domain_scores:
            total += domain_scores[domain] * (weight / 100)
            used_weight += weight
    if used_weight == 0:
        return 0
    # Normalize in case some domains had no scored answers
    return total * (100 / used_weight)


def determine_maturity_level(total_score):
    """Map total score to NIST CSF maturity tier 1–4."""
    for level, (name, lo, hi, _desc) in MATURITY_LEVELS.items():
        if lo <= total_score <= hi:
            return level
    return 1


def generate_action_plan(gaps, recommendations):
    """Match gaps to their recommendations and sort by priority."""
    rec_lookup = {(r.question_id, r.trigger_answer): r for r in recommendations}
    priority_order = {"critical": 0, "high": 1, "medium": 2}

    action_plan = []
    for question_id, trigger_answer in gaps:
        # Try exact match first; fall back to "No" recommendation for "Partial"
        rec = rec_lookup.get((question_id, trigger_answer))
        if rec is None and trigger_answer == "Partial":
            rec = rec_lookup.get((question_id, "No"))
        if rec is not None:
            action_plan.append(rec)

    action_plan.sort(key=lambda r: priority_order.get(r.priority, 99))
    return action_plan


# ============================================================
# TUI MENU FUNCTIONS
# ============================================================

def print_header():
    print("=" * 64)
    print("    Indiana Municipality Cybersecurity Self-Assessment Tool    ")
    print("    Aligned to NIST Cybersecurity Framework 2.0                ")
    print("=" * 64)


def print_main_menu():
    print("\n-------- MAIN MENU --------")
    print("1. Start New Assessment")
    print("2. View Previous Reports")
    print("3. View Submission History")
    print("4. View Municipality List")
    print("5. Exit")
    print("---------------------------")


# ============================================================
# PROGRAM FUNCTIONS
# ============================================================

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
        print("[ERROR] Invalid choice. Please try again.")


def run_assessment(municipality, questions):
    """Walk the user through all assessment questions and collect answers"""
    print(f"\n--- Starting Assessment for {municipality.name} ---")
    print(f"You will answer {len(questions)} questions across 5 NIST CSF domains.")
    print("Answer each question: Yes / Partial / No / N/A\n")

    user_answers = []
    current_domain = None

    for i, question in enumerate(questions):
        # Print a domain header when the domain changes
        if question.domain != current_domain:
            current_domain = question.domain
            print(f"\n========== {current_domain.upper()} ==========")

        print(f"\nProgress: [{i + 1}/{len(questions)}] | {question.subdomain}")
        print(f"Q: {question.text}")
        if question.guidance:
            print(f"   Hint: {question.guidance}")
        print("Options: Yes / Partial / No / N/A")

        while True:
            answer = input("Your answer: ").strip()
            # Normalize input
            normalized = answer.upper() if answer.upper() == "N/A" else answer.capitalize()
            if normalized in ANSWER_SCORES:
                user_answers.append((question.id, normalized))
                break
            print("[ERROR] Please enter: Yes, Partial, No, or N/A")

    return user_answers


def submit_assessment(municipality, user_answers, questions, recommendations,
                      supabase, all_submissions, all_reports):
    """Score the answers, generate a report, and persist it."""
    submission_id = len(all_submissions) + 1
    submission = AssessmentSubmission(submission_id, municipality.id, user_answers)
    all_submissions.append(submission)

    domain_scores, gaps = calculate_scores(user_answers, questions)
    total_score = calculate_total_score(domain_scores)
    maturity_level = determine_maturity_level(total_score)
    action_plan = generate_action_plan(gaps, recommendations)

    report_id = len(all_reports) + 1
    report = ScoredReport(report_id, submission_id, total_score, maturity_level,
                          domain_scores, [g[0] for g in gaps], action_plan)
    all_reports.append(report)

    save_submission_and_report(supabase, municipality, submission, report)
    return report


def display_report(report, questions):
    """Print a formatted report to the screen."""
    question_lookup = {q.id: q for q in questions}
    level_name, _, _, level_desc = MATURITY_LEVELS[report.maturity_level]

    print("\n" + "=" * 64)
    print("                     ASSESSMENT REPORT")
    print("=" * 64)
    print(f"Report ID:         #{report.id}")
    print(f"Submission ID:     #{report.submission_id}")
    print(f"Total Score:       {report.total_score:.1f}%")
    print(f"Maturity Tier:     Level {report.maturity_level} — {level_name}")
    print(f"What this means:   {level_desc}")

    print("\n--- Domain Scores ---")
    for domain in ["Identify", "Protect", "Detect", "Respond", "Recover"]:
        if domain in report.domain_scores:
            score = report.domain_scores[domain]
            weight = DOMAIN_WEIGHTS[domain]
            bar = "#" * int(score / 5) + "-" * (20 - int(score / 5))
            print(f"  {domain:10s} [{bar}] {score:5.1f}%  (weight: {weight}%)")

    print(f"\n--- Identified Gaps ({len(report.gaps)}) ---")
    if report.gaps:
        for gap_id in report.gaps[:10]:
            q = question_lookup.get(gap_id)
            if q:
                print(f"  [{gap_id}] {q.text[:70]}{'...' if len(q.text) > 70 else ''}")
        if len(report.gaps) > 10:
            print(f"  ... and {len(report.gaps) - 10} more")
    else:
        print("  No significant gaps identified!")

    print(f"\n--- Prioritized Action Plan ({len(report.action_plan)} items) ---")
    if report.action_plan:
        for i, rec in enumerate(report.action_plan[:8], 1):
            print(f"\n  {i}. [{rec.priority.upper()}] {rec.title}")
            print(f"     Effort: {rec.effort} | Question: {rec.question_id}")
            print(f"     {rec.action}")
        if len(report.action_plan) > 8:
            print(f"\n  ... and {len(report.action_plan) - 8} more recommendations")
    else:
        print("  No actions required at this time.")

    print("\n--- Indiana Resources ---")
    print("  Indiana IDHS Cyber Division: 800-800-3578")
    print("  IN-ISAC:  https://www.in.gov/cybersecurity/in-isac/")
    print("  CISA Region 5 (Chicago): 312-353-7272")
    print("=" * 64)


def view_reports(all_reports, questions):
    """Let the user browse previous reports."""
    if not all_reports:
        print("\n[INFO] No reports found. Complete an assessment first.")
        return
    print("\n--- Previous Reports ---")
    for r in all_reports:
        print(f"  Report #{r.id} | Score: {r.total_score:.1f}% | Level {r.maturity_level}")
    choice = input("\nEnter report ID to view (or press Enter to skip): ").strip()
    if choice.isdigit():
        report_id = int(choice)
        for r in all_reports:
            if r.id == report_id:
                display_report(r, questions)
                return
        print("[ERROR] Report not found.")


def view_submissions(all_submissions):
    """Show submission history."""
    if not all_submissions:
        print("\n[INFO] No submissions found.")
        return
    print("\n--- Submission History ---")
    for s in all_submissions:
        print(f"  Submission #{s.id} | Municipality ID: {s.municipality_id} | {s.timestamp}")


def view_municipalities():
    """Show the municipality list."""
    print("\n--- Municipality List ---")
    for m in MUNICIPALITIES:
        print(f"  {m.id}. {m}")


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():
    print_header()

    # Connect to Supabase (fall back to local data if unavailable)
    supabase = get_supabase_client()
    if supabase is not None:
        print("[INFO] Connected to Supabase.")
    else:
        print("[INFO] Running offline with local question bank.")

    questions = load_questions(supabase)
    recommendations = load_recommendations(supabase)
    print(f"[INFO] Loaded {len(questions)} questions and {len(recommendations)} recommendations.")

    all_submissions = []
    all_reports = []

    while True:
        print_main_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            municipality = select_municipality()
            user_answers = run_assessment(municipality, questions)
            report = submit_assessment(municipality, user_answers, questions,
                                       recommendations, supabase,
                                       all_submissions, all_reports)
            display_report(report, questions)

        elif choice == "2":
            view_reports(all_reports, questions)

        elif choice == "3":
            view_submissions(all_submissions)

        elif choice == "4":
            view_municipalities()

        elif choice == "5":
            print("\n[INFO] Thank you for using the Cybersecurity Self-Assessment Tool.")
            print("Stay secure!\n")
            break

        else:
            print("\n[ERROR] Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import sqlite3, hashlib, re, smtplib, threading, random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "campus_hiring_secret_2026"
DB = "hiring.db"

EMAIL_SENDER   = "techvistara3.0@gmail.com"
EMAIL_PASSWORD = "sxlh mjpq rxcs occv"

otp_store = {}  # email -> {otp, data, expires}

BRANCHES = ["Computer Science", "Information Technology", "Electronics", "Mechanical", "Civil", "MBA", "BCA", "MCA"]

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def hp(p): return hashlib.md5(p.encode()).hexdigest()
def today(): return datetime.now().strftime("%d/%m/%Y")
def now():   return datetime.now().strftime("%d/%m/%Y %H:%M")

def valid_email(e):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', e.strip()) is not None

def send_email(to, subject, html):
    def _send():
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"]    = f"CampusHire — SMD College <{EMAIL_SENDER}>"
            msg["To"]      = to
            msg.attach(MIMEText(html, "html"))
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
                s.login(EMAIL_SENDER, EMAIL_PASSWORD)
                s.sendmail(EMAIL_SENDER, to, msg.as_string())
            print(f"[EMAIL OK] {to}")
        except Exception as e:
            print(f"[EMAIL ERR] {e}")
    threading.Thread(target=_send).start()

def base_email(icon, header_color, title, subtitle, body_html):
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
  body{{margin:0;padding:0;background:#f0f4ff;font-family:'Segoe UI',sans-serif}}
  .wrap{{max-width:600px;margin:0 auto;background:#f0f4ff;padding:20px 0}}
  .card{{background:#fff;border-radius:20px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08)}}
  .hero{{background:{header_color};padding:44px 40px;text-align:center}}
  .hero-icon{{font-size:56px;margin-bottom:16px}}
  .hero h1{{color:#fff;font-size:28px;font-weight:900;margin:0 0 6px;letter-spacing:-0.5px}}
  .hero p{{color:rgba(255,255,255,0.8);font-size:14px;margin:0}}
  .body{{padding:36px 40px}}
  .greeting{{font-size:20px;font-weight:800;color:#1a1a2e;margin-bottom:12px}}
  .text{{color:#555;font-size:15px;line-height:1.8;margin-bottom:16px}}
  .info-box{{background:#f8faff;border:1px solid #e0e8ff;border-radius:14px;padding:20px;margin:20px 0}}
  .info-row{{display:flex;padding:8px 0;border-bottom:1px solid #eef2ff}}
  .info-row:last-child{{border-bottom:none}}
  .info-label{{color:#888;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;width:140px;flex-shrink:0}}
  .info-val{{color:#1a1a2e;font-size:14px;font-weight:600}}
  .cta{{background:{header_color};border-radius:14px;padding:24px;text-align:center;margin-top:20px}}
  .cta h3{{color:#fff;font-size:18px;font-weight:800;margin:0 0 6px}}
  .cta p{{color:rgba(255,255,255,0.85);font-size:13px;margin:0}}
  .footer{{text-align:center;padding:24px;color:#aaa;font-size:12px}}
</style></head><body>
<div class="wrap"><div class="card">
  <div class="hero"><div class="hero-icon">{icon}</div><h1>{title}</h1><p>{subtitle}</p></div>
  <div class="body">{body_html}</div>
</div>
<div class="footer"><p>© 2026 CampusHire — SMD College, Hospet</p><p>This is an automated email. Do not reply.</p></div>
</div></body></html>"""

def email_otp(name, email, otp):
    body = f"""<div class="greeting">Hello, {name}! 👋</div>
<p class="text">Your OTP for CampusHire registration is:</p>
<div style="text-align:center;margin:28px 0">
  <div style="display:inline-block;background:linear-gradient(135deg,#1a1a6e,#4444cc);color:#fff;font-size:44px;font-weight:900;padding:22px 44px;border-radius:18px;letter-spacing:10px">{otp}</div>
</div>
<p class="text">This OTP is valid for <b>10 minutes</b>. Do not share it with anyone.</p>
<div class="cta"><h3>🔐 Verify &amp; Join CampusHire!</h3><p>Enter this OTP to complete your registration.</p></div>"""
    send_email(email, "🔐 Your OTP — CampusHire Registration", base_email("🔐", "linear-gradient(135deg,#1a1a6e,#2d2d9e,#4444cc)", "OTP Verification", "Complete your CampusHire registration", body))

def email_welcome_student(name, email, branch, cgpa):
    body = f"""<div class="greeting">Welcome, {name}! 🎓</div>
<p class="text">Your student account has been successfully registered on <b>CampusHire</b> — the official placement portal of SMD College, Hospet.</p>
<div class="info-box">
  <div class="info-row"><div class="info-label">Name</div><div class="info-val">{name}</div></div>
  <div class="info-row"><div class="info-label">Branch</div><div class="info-val">{branch}</div></div>
  <div class="info-row"><div class="info-label">CGPA</div><div class="info-val">{cgpa}</div></div>
  <div class="info-row"><div class="info-label">Portal</div><div class="info-val">CampusHire — SMD College</div></div>
</div>
<p class="text">You can now browse open placement drives, apply to companies, and track your application status in real time.</p>
<div class="cta"><h3>🚀 Start Your Career Journey!</h3><p>Login to explore companies and apply for your dream job.</p></div>"""
    send_email(email, "🎓 Welcome to CampusHire — Registration Confirmed!", base_email("🎓", "linear-gradient(135deg,#1a1a6e,#2d2d9e,#4444cc)", "Registration Confirmed!", "CampusHire — SMD College, Hospet", body))

def email_welcome_company(name, email, company):
    body = f"""<div class="greeting">Welcome, {name}! 🏢</div>
<p class="text">Your company <b>{company}</b> has been registered on <b>CampusHire</b>. Our TPO team will review and approve your profile shortly.</p>
<div class="info-box">
  <div class="info-row"><div class="info-label">Contact</div><div class="info-val">{name}</div></div>
  <div class="info-row"><div class="info-label">Company</div><div class="info-val">{company}</div></div>
  <div class="info-row"><div class="info-label">Status</div><div class="info-val">⏳ Pending Approval</div></div>
</div>
<p class="text">Once approved by the Placement Cell, you can post job drives and start reviewing student applications.</p>
<div class="cta"><h3>🏢 Start Hiring Top Talent!</h3><p>Access the best students from SMD College, Hospet.</p></div>"""
    send_email(email, "🏢 Company Registered — CampusHire", base_email("🏢", "linear-gradient(135deg,#0f4c75,#1b6ca8,#3a9bd5)", "Company Registration Received!", "Pending approval by Placement Cell", body))

def email_company_approved(name, email, company):
    body = f"""<div class="greeting">Great News, {name}! ✅</div>
<p class="text">Your company <b>{company}</b> has been <b style="color:#16a34a">approved</b> by the SMD College Placement Cell. You can now post placement drives and start hiring!</p>
<div class="cta"><h3>✅ You're All Set!</h3><p>Login to CampusHire and post your first job drive today.</p></div>"""
    send_email(email, "✅ Company Approved — Start Hiring Now!", base_email("✅", "linear-gradient(135deg,#065f46,#059669,#34d399)", "Company Approved!", "You can now post drives on CampusHire", body))

def email_drive_announcement(student_name, student_email, company, role, ctc, cgpa_req, last_date):
    body = f"""<div class="greeting">New Drive Alert, {student_name}! 🚀</div>
<p class="text">A new placement drive has been posted on CampusHire. Check if you're eligible and apply before the deadline!</p>
<div class="info-box">
  <div class="info-row"><div class="info-label">Company</div><div class="info-val">{company}</div></div>
  <div class="info-row"><div class="info-label">Role</div><div class="info-val">{role}</div></div>
  <div class="info-row"><div class="info-label">CTC</div><div class="info-val" style="color:#16a34a;font-weight:900">{ctc}</div></div>
  <div class="info-row"><div class="info-label">Min. CGPA</div><div class="info-val">{cgpa_req}</div></div>
  <div class="info-row"><div class="info-label">Last Date</div><div class="info-val" style="color:#dc2626">{last_date}</div></div>
</div>
<div class="cta"><h3>⚡ Apply Now!</h3><p>Login to CampusHire and submit your application before the deadline.</p></div>"""
    send_email(student_email, f"🚀 New Drive: {company} is Hiring! — CampusHire", base_email("🚀", "linear-gradient(135deg,#7c3aed,#9333ea,#c084fc)", f"New Drive: {company}", f"Role: {role} | CTC: {ctc}", body))

def email_application_status(student_name, student_email, company, role, status, round_name="", message=""):
    color = {"Shortlisted":"#16a34a","Rejected":"#dc2626","Selected":"#059669","Interview":"#d97706","Applied":"#4444cc"}.get(status,"#4444cc")
    icon  = {"Shortlisted":"🎯","Rejected":"😔","Selected":"🏆","Interview":"📅","Applied":"📋"}.get(status,"📋")
    body  = f"""<div class="greeting">Application Update, {student_name}! {icon}</div>
<p class="text">Your application for <b>{role}</b> at <b>{company}</b> has been updated.</p>
<div class="info-box">
  <div class="info-row"><div class="info-label">Company</div><div class="info-val">{company}</div></div>
  <div class="info-row"><div class="info-label">Role</div><div class="info-val">{role}</div></div>
  <div class="info-row"><div class="info-label">Status</div><div class="info-val"><span style="color:{color};font-weight:900;font-size:16px">{status}</span></div></div>
  {f'<div class="info-row"><div class="info-label">Round</div><div class="info-val">{round_name}</div></div>' if round_name else ''}
  {f'<div class="info-row"><div class="info-label">Message</div><div class="info-val">{message}</div></div>' if message else ''}
</div>
{"<div class='cta'><h3>🏆 Congratulations!</h3><p>You have been selected! Offer letter will be shared soon.</p></div>" if status=="Selected" else ""}
{"<div class='cta' style='background:linear-gradient(135deg,#d97706,#f59e0b)'><h3>📅 Interview Scheduled!</h3><p>Check your dashboard for round details and prepare well!</p></div>" if status=="Interview" else ""}
{"<div class='cta'><h3>📋 Application Submitted!</h3><p>We have received your application. The company will review it soon.</p></div>" if status=="Applied" else ""}"""
    send_email(student_email, f"{icon} Application {status} — {company} | CampusHire", base_email(icon, f"linear-gradient(135deg,{color},{color}cc)", f"Application {status}", f"{company} — {role}", body))

def email_new_application(company_name, hr_email, student_name, role, branch, cgpa, skills):
    body = f"""<div class="greeting">New Application Received! 📋</div>
<p class="text">A student has applied for your placement drive on <b>CampusHire</b>. Review the candidate details below.</p>
<div class="info-box">
  <div class="info-row"><div class="info-label">Student</div><div class="info-val">{student_name}</div></div>
  <div class="info-row"><div class="info-label">Applied For</div><div class="info-val">{role}</div></div>
  <div class="info-row"><div class="info-label">Branch</div><div class="info-val">{branch}</div></div>
  <div class="info-row"><div class="info-label">CGPA</div><div class="info-val" style="color:#16a34a;font-weight:900">{cgpa}</div></div>
  <div class="info-row"><div class="info-label">Skills</div><div class="info-val">{skills or 'Not mentioned'}</div></div>
</div>
<div class="cta"><h3>👀 Review Application!</h3><p>Login to CampusHire to shortlist or reject this candidate.</p></div>"""
    send_email(hr_email, f"📋 New Application: {student_name} applied for {role} — CampusHire", base_email("📋", "linear-gradient(135deg,#0f4c75,#1b6ca8,#3a9bd5)", f"New Application — {company_name}", f"{student_name} applied for {role}", body))

def email_offer_letter(student_name, student_email, company, role, ctc, joining_date):
    body = f"""<div class="greeting">Congratulations, {student_name}! 🏆</div>
<p class="text">We are thrilled to inform you that you have been <b style="color:#16a34a">selected</b> for the position of <b>{role}</b> at <b>{company}</b>. This is a proud moment for you and SMD College!</p>
<div class="info-box">
  <div class="info-row"><div class="info-label">Student</div><div class="info-val">{student_name}</div></div>
  <div class="info-row"><div class="info-label">Company</div><div class="info-val">{company}</div></div>
  <div class="info-row"><div class="info-label">Role</div><div class="info-val">{role}</div></div>
  <div class="info-row"><div class="info-label">CTC Package</div><div class="info-val" style="color:#16a34a;font-weight:900;font-size:16px">{ctc}</div></div>
  <div class="info-row"><div class="info-label">Joining Date</div><div class="info-val">{joining_date}</div></div>
  <div class="info-row"><div class="info-label">Issued By</div><div class="info-val">CampusHire — SMD College, Hospet</div></div>
</div>
<p class="text">Please report to the Placement Cell to collect your official offer letter. Congratulations once again! 🎉</p>
<div class="cta"><h3>🎉 Your Future Starts Now!</h3><p>Best wishes from the entire Placement Team, SMD College, Hospet.</p></div>"""
    send_email(student_email, f"🏆 Offer Letter — {company} | {role} | CampusHire", base_email("🏆", "linear-gradient(135deg,#065f46,#059669,#34d399)", "Offer Letter Issued!", f"{company} — {role} | {ctc}", body))

def email_interview_call(student_name, student_email, company, role, round_name, date_time, venue, instructions):
    body = f"""<div class="greeting">Interview Call Letter 📋</div>
<p class="text">You have been called for the next round of the selection process at <b>{company}</b>.</p>
<div class="info-box">
  <div class="info-row"><div class="info-label">Company</div><div class="info-val">{company}</div></div>
  <div class="info-row"><div class="info-label">Position</div><div class="info-val">{role}</div></div>
  <div class="info-row"><div class="info-label">Round</div><div class="info-val" style="color:#7c3aed;font-weight:700">{round_name}</div></div>
  <div class="info-row"><div class="info-label">Date &amp; Time</div><div class="info-val" style="color:#dc2626;font-weight:700">{date_time}</div></div>
  <div class="info-row"><div class="info-label">Venue</div><div class="info-val">{venue}</div></div>
  {f'<div class="info-row"><div class="info-label">Instructions</div><div class="info-val">{instructions}</div></div>' if instructions else ''}
</div>
<div class="cta"><h3>📋 Be Prepared!</h3><p>Carry your resume, ID proof, and all required documents. Best of luck, {student_name}!</p></div>"""
    send_email(student_email, f"📋 Interview Call — {company} | {round_name} | CampusHire", base_email("📋", "linear-gradient(135deg,#7c3aed,#9333ea,#c084fc)", "Interview Call Letter", f"{company} — {round_name}", body))

# ── DATABASE ──────────────────────────────────────────────────
def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY, name TEXT, email TEXT UNIQUE,
        password TEXT, role TEXT, phone TEXT,
        created_on TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS students (
        user_id TEXT PRIMARY KEY, roll_no TEXT UNIQUE,
        branch TEXT, cgpa REAL, skills TEXT,
        projects TEXT, internships TEXT, achievements TEXT,
        resume_link TEXT, placed INTEGER DEFAULT 0,
        placed_company TEXT, placed_role TEXT, placed_ctc TEXT,
        linkedin TEXT, github TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS companies (
        id TEXT PRIMARY KEY, user_id TEXT, company_name TEXT,
        industry TEXT, website TEXT, about TEXT,
        hr_name TEXT, hr_email TEXT, hr_phone TEXT,
        status TEXT DEFAULT 'Pending', approved_on TEXT,
        created_on TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS drives (
        id TEXT PRIMARY KEY, company_id TEXT, company_name TEXT,
        role TEXT, job_type TEXT, ctc TEXT,
        location TEXT, branches TEXT, min_cgpa REAL,
        description TEXT, rounds TEXT, last_date TEXT,
        drive_date TEXT, status TEXT DEFAULT 'Open',
        created_on TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS applications (
        id TEXT PRIMARY KEY, drive_id TEXT, student_id TEXT,
        student_name TEXT, company_name TEXT, role TEXT,
        status TEXT DEFAULT 'Applied', current_round TEXT,
        hr_message TEXT, applied_on TEXT, updated_on TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS notices (
        id TEXT PRIMARY KEY, title TEXT, content TEXT,
        posted_by TEXT, priority TEXT DEFAULT 'Normal',
        created_on TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS offer_letters (
        id TEXT PRIMARY KEY, student_id TEXT, student_name TEXT,
        company_name TEXT, role TEXT, ctc TEXT,
        joining_date TEXT, issued_on TEXT, issued_by TEXT)''')

    if not c.execute("SELECT 1 FROM users WHERE email='tpo@smd.edu.in'").fetchone():
        c.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?)",
            ("ADM001","Dr. Priya Sharma","tpo@smd.edu.in",hp("admin123"),"admin","9845001122",today()))
    comp_users = [
        ("CHR001","Vikram Mehta","kalalindu951@gmail.com",hp("hr123"),"company","9876500001",today()),
        ("CHR002","Sneha Gupta","tarakalal052@gmail.com",hp("hr123"),"company","9876500002",today()),
        ("CHR003","Arjun Nair","kalalindu951@gmail.com",hp("hr123"),"company","9876500003",today()),
    ]
    for u in comp_users:
        c.execute("INSERT OR IGNORE INTO users VALUES(?,?,?,?,?,?,?)", u)

    companies = [
        ("CMP001","CHR001","JSW Limited","IT Services","https://jsw.com","Leading global IT company","Vikram Mehta","kalalindu951@gmail.com","9876500001","Approved",today(),today()),
        ("CMP002","CHR002","Kirloskar Technologies","IT Services","https://kirloskar.com","Global IT consulting company","Sneha Gupta","tarakalal052@gmail.com","9876500002","Approved",today(),today()),
        ("CMP003","CHR003","BMM","IT Services","https://bmm.com","Top IT firm","Arjun Nair","kalalindu951@gmail.com","9876500003","Approved",today(),today()),
    ]
    for comp in companies:
        c.execute("INSERT OR IGNORE INTO companies VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", comp)

    stu_users = [
        ("STU001","Kavya Reddy","kavya@gmail.com",hp("stu123"),"student","9900001111",today()),
        ("STU002","Arjun Patil","arjunp@gmail.com",hp("stu123"),"student","9900002222",today()),
        ("STU003","Meera Kulkarni","meera@gmail.com",hp("stu123"),"student","9900003333",today()),
        ("STU004","Sameer Khan","sameer@gmail.com",hp("stu123"),"student","9900004444",today()),
        ("STU005","Pooja Desai","pooja@gmail.com",hp("stu123"),"student","9900005555",today()),
        ("STU006","Rohit Verma","rohit@gmail.com",hp("stu123"),"student","9900006666",today()),
    ]
    for u in stu_users:
        c.execute("INSERT OR IGNORE INTO users VALUES(?,?,?,?,?,?,?)", u)

    students = [
        ("STU001","BCA2026001","BCA",8.7,"Python,Flask,React,SQL","E-commerce Website,Chat App","ABC Corp — Web Dev","Hackathon Winner 2025","",0,"","","","linkedin.com/kavya","github.com/kavya"),
        ("STU002","BCA2026002","BCA",7.9,"Java,Spring,MySQL","Library System,Bank App","XYZ Pvt — Java Dev","Best Project Award","",0,"","","","linkedin.com/arjunp","github.com/arjunp"),
        ("STU003","BCA2026003","Computer Science",8.4,"C++,Python,ML","ML Model,Blog Website","None","State Level Quiz Winner","",0,"","","","linkedin.com/meera","github.com/meera"),
        ("STU004","BCA2026004","BCA",7.2,"JavaScript,Node,MongoDB","Todo App,Portfolio","Freelance — Web","None","",0,"","","","linkedin.com/sameer","github.com/sameer"),
        ("STU005","BCA2026005","Information Technology",8.9,"Python,Django,PostgreSQL","HR Portal,Inventory App","TechStart — Django","Gold Medal Academics","",0,"","","","linkedin.com/pooja","github.com/pooja"),
        ("STU006","BCA2026006","BCA",6.8,"HTML,CSS,JS,PHP","College Website,Quiz App","None","Sports Captain","",0,"","","","linkedin.com/rohit","github.com/rohit"),
    ]
    for s in students:
        c.execute("INSERT OR IGNORE INTO students VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", s)

    if not c.execute("SELECT 1 FROM drives").fetchone():
        drives = [
            ("DRV001","CMP001","JSW Limited","Systems Engineer","Full-time","4.5 LPA","Bangalore","BCA,Computer Science,Information Technology",7.0,"Exciting opportunity for fresh graduates","Aptitude Test,Technical Interview,HR Interview","30/04/2026","10/05/2026","Open",now()),
            ("DRV002","CMP002","Kirloskar Technologies","Project Engineer","Full-time","3.8 LPA","Pune,Hyderabad","BCA,Information Technology,Electronics",6.5,"Join Kirloskar global talent network","Written Test,GD,Technical,HR","25/04/2026","05/05/2026","Open",now()),
            ("DRV003","CMP003","BMM","Assistant System Engineer","Full-time","3.6 LPA","Mumbai,Chennai,Bangalore","BCA,Computer Science,MCA",6.0,"BMM National Qualifier Test based hiring","BMM NQT,Technical Interview,HR","20/04/2026","02/05/2026","Open",now()),
        ]
        c.executemany("INSERT INTO drives VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", drives)

    if not c.execute("SELECT 1 FROM applications").fetchone():
        apps = [
            ("APP001","DRV001","STU001","Kavya Reddy","JSW Limited","Systems Engineer","Shortlisted","Aptitude Test","Great profile!",now(),now()),
            ("APP002","DRV001","STU002","Arjun Patil","JSW Limited","Systems Engineer","Applied","","",now(),now()),
            ("APP003","DRV002","STU003","Meera Kulkarni","Kirloskar Technologies","Project Engineer","Applied","","",now(),now()),
            ("APP004","DRV003","STU005","Pooja Desai","BMM","Assistant System Engineer","Shortlisted","BMM NQT","Excellent scores!",now(),now()),
        ]
        c.executemany("INSERT INTO applications VALUES(?,?,?,?,?,?,?,?,?,?,?)", apps)

    if not c.execute("SELECT 1 FROM notices").fetchone():
        c.execute("INSERT INTO notices VALUES(?,?,?,?,?,?)",
            ("NOT001","Pre-Placement Orientation","All final year students must attend the pre-placement orientation on 15th April 2026 in the Main Auditorium.","Dr. Priya Sharma","High",now()))
        c.execute("INSERT INTO notices VALUES(?,?,?,?,?,?)",
            ("NOT002","Resume Submission Deadline","All students must upload their updated resume by 20th April 2026.","Dr. Priya Sharma","Normal",now()))

    conn.commit()
    conn.close()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def d(*a, **kw):
        if "user_id" not in session: return jsonify({"error":"Unauthorized"}),401
        return f(*a, **kw)
    return d

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def d(*a, **kw):
        if session.get("role") != "admin": return jsonify({"error":"Forbidden"}),403
        return f(*a, **kw)
    return d

# ── AUTH ──────────────────────────────────────────────────────
@app.route("/")
def index(): return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        d = request.get_json()
        email = d.get("email","").strip()
        if not valid_email(email):
            return jsonify({"ok":False,"msg":"Please enter a valid email! (e.g. name@gmail.com)"})
        conn = get_db()
        u = conn.execute("SELECT * FROM users WHERE email=? AND password=?",
            (email, hp(d.get("password","")))).fetchone()
        conn.close()
        if u:
            session.update({"user_id":u["id"],"user_name":u["name"],
                            "role":u["role"],"user_email":u["email"]})
            return jsonify({"ok":True,"role":u["role"]})
        return jsonify({"ok":False,"msg":"Invalid email or password!"})
    return render_template("index.html")

@app.route("/signup/send-otp", methods=["POST"])
def send_otp():
    d = request.get_json()
    email = d.get("email","").strip()
    if not valid_email(email):
        return jsonify({"ok":False,"msg":"Please enter a valid email!"})
    if not d.get("name","").strip():
        return jsonify({"ok":False,"msg":"Please enter your name!"})
    if len(d.get("password","")) < 6:
        return jsonify({"ok":False,"msg":"Password must be at least 6 characters!"})
    conn = get_db()
    if conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
        conn.close()
        return jsonify({"ok":False,"msg":"Email already registered!"})
    conn.close()
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {
        "otp": otp,
        "data": d,
        "expires": datetime.now().timestamp() + 600
    }
    email_otp(d.get("name","User"), email, otp)
    return jsonify({"ok":True,"msg":"OTP sent to your email! Check inbox."})

@app.route("/signup", methods=["POST"])
def signup():
    d = request.get_json()
    email = d.get("email","").strip()
    entered_otp = d.get("otp","").strip()
    if email not in otp_store:
        return jsonify({"ok":False,"msg":"OTP not sent! Please request OTP first."})
    record = otp_store[email]
    if datetime.now().timestamp() > record["expires"]:
        del otp_store[email]
        return jsonify({"ok":False,"msg":"OTP expired! Please request again."})
    if record["otp"] != entered_otp:
        return jsonify({"ok":False,"msg":"Wrong OTP! Please try again."})
    del otp_store[email]
    data = record["data"]
    conn = get_db()
    uid = ("STU" if data["role"]=="student" else "CHR") + str(int(datetime.now().timestamp()))
    conn.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?)",
        (uid, data["name"], data["email"], hp(data["password"]),
         data["role"], data.get("phone",""), today()))
    if data["role"] == "student":
        conn.execute("INSERT INTO students VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (uid,"",data.get("branch",""),float(data.get("cgpa",0)),
             "","","","","",0,"","","","",""))
        conn.commit(); conn.close()
        email_welcome_student(data["name"],data["email"],data.get("branch",""),data.get("cgpa",0))
    elif data["role"] == "company":
        cid = "CMP"+str(int(datetime.now().timestamp()))
        conn.execute("INSERT INTO companies VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (cid,uid,data.get("company_name",""),data.get("industry",""),
             data.get("website",""),data.get("about",""),data["name"],
             data["email"],data.get("phone",""),"Pending","",today()))
        conn.commit(); conn.close()
        email_welcome_company(data["name"],data["email"],data.get("company_name",""))
    return jsonify({"ok":True})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/api/session")
def get_session():
    if "user_id" not in session: return jsonify({"logged_in":False})
    conn = get_db()
    extra = {}
    if session["role"] == "student":
        s = conn.execute("SELECT * FROM students WHERE user_id=?", (session["user_id"],)).fetchone()
        if s: extra = dict(s)
    elif session["role"] == "company":
        c = conn.execute("SELECT * FROM companies WHERE user_id=?", (session["user_id"],)).fetchone()
        if c: extra = dict(c)
    conn.close()
    return jsonify({"logged_in":True,"id":session["user_id"],"name":session["user_name"],
                    "role":session["role"],"email":session["user_email"],**extra})

# ── DASHBOARD ─────────────────────────────────────────────────
@app.route("/api/dashboard")
@login_required
def dashboard():
    conn = get_db()
    role = session["role"]
    data = {}
    if role == "admin":
        data["total_students"]    = conn.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0]
        data["total_companies"]   = conn.execute("SELECT COUNT(*) FROM companies WHERE status='Approved'").fetchone()[0]
        data["total_drives"]      = conn.execute("SELECT COUNT(*) FROM drives WHERE status='Open'").fetchone()[0]
        data["total_placed"]      = conn.execute("SELECT COUNT(*) FROM students WHERE placed=1").fetchone()[0]
        data["pending_approvals"] = conn.execute("SELECT COUNT(*) FROM companies WHERE status='Pending'").fetchone()[0]
        data["total_apps"]        = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        data["recent_apps"]       = [dict(r) for r in conn.execute("SELECT * FROM applications ORDER BY rowid DESC LIMIT 6").fetchall()]
        data["top_companies"]     = [dict(r) for r in conn.execute("SELECT company_name, COUNT(*) as cnt FROM applications GROUP BY company_name ORDER BY cnt DESC LIMIT 5").fetchall()]
        data["branch_stats"]      = [dict(r) for r in conn.execute("SELECT branch, COUNT(*) as total, SUM(placed) as placed FROM students GROUP BY branch").fetchall()]
    elif role == "student":
        sid = session["user_id"]
        data["my_apps"]      = conn.execute("SELECT COUNT(*) FROM applications WHERE student_id=?", (sid,)).fetchone()[0]
        data["shortlisted"]  = conn.execute("SELECT COUNT(*) FROM applications WHERE student_id=? AND status='Shortlisted'", (sid,)).fetchone()[0]
        data["selected"]     = conn.execute("SELECT COUNT(*) FROM applications WHERE student_id=? AND status='Selected'", (sid,)).fetchone()[0]
        data["open_drives"]  = conn.execute("SELECT COUNT(*) FROM drives WHERE status='Open'").fetchone()[0]
        data["recent_apps"]  = [dict(r) for r in conn.execute("SELECT * FROM applications WHERE student_id=? ORDER BY rowid DESC LIMIT 5", (sid,)).fetchall()]
        data["notices"]      = [dict(r) for r in conn.execute("SELECT * FROM notices ORDER BY rowid DESC LIMIT 3").fetchall()]
    elif role == "company":
        cid_row = conn.execute("SELECT id FROM companies WHERE user_id=?", (session["user_id"],)).fetchone()
        if cid_row:
            cid = cid_row["id"]
            data["total_drives"] = conn.execute("SELECT COUNT(*) FROM drives WHERE company_id=?", (cid,)).fetchone()[0]
            data["total_apps"]   = conn.execute("SELECT COUNT(*) FROM applications a JOIN drives d ON a.drive_id=d.id WHERE d.company_id=?", (cid,)).fetchone()[0]
            data["shortlisted"]  = conn.execute("SELECT COUNT(*) FROM applications a JOIN drives d ON a.drive_id=d.id WHERE d.company_id=? AND a.status='Shortlisted'", (cid,)).fetchone()[0]
            data["selected"]     = conn.execute("SELECT COUNT(*) FROM applications a JOIN drives d ON a.drive_id=d.id WHERE d.company_id=? AND a.status='Selected'", (cid,)).fetchone()[0]
            data["recent_apps"]  = [dict(r) for r in conn.execute("SELECT a.* FROM applications a JOIN drives d ON a.drive_id=d.id WHERE d.company_id=? ORDER BY a.rowid DESC LIMIT 5", (cid,)).fetchall()]
    conn.close()
    return jsonify(data)

# ── DRIVES ────────────────────────────────────────────────────
@app.route("/api/drives")
@login_required
def get_drives():
    conn = get_db()
    role = session["role"]
    if role == "company":
        cid = conn.execute("SELECT id FROM companies WHERE user_id=?", (session["user_id"],)).fetchone()
        drives = [dict(r) for r in conn.execute("SELECT * FROM drives WHERE company_id=? ORDER BY rowid DESC", (cid["id"],)).fetchall()] if cid else []
    elif role == "student":
        s = conn.execute("SELECT * FROM students WHERE user_id=?", (session["user_id"],)).fetchone()
        drives = [dict(r) for r in conn.execute("SELECT * FROM drives WHERE status='Open' ORDER BY rowid DESC").fetchall()]
        applied = {r["drive_id"] for r in conn.execute("SELECT drive_id FROM applications WHERE student_id=?", (session["user_id"],)).fetchall()}
        for d in drives:
            d["applied"]  = d["id"] in applied
            d["eligible"] = (s["cgpa"] >= d["min_cgpa"]) and (s["branch"] in d["branches"]) if s else False
    else:
        drives = [dict(r) for r in conn.execute("SELECT * FROM drives ORDER BY rowid DESC").fetchall()]
    conn.close()
    return jsonify(drives)

@app.route("/api/drives", methods=["POST"])
@login_required
def add_drive():
    d = request.get_json()
    conn = get_db()
    cmp = conn.execute("SELECT * FROM companies WHERE user_id=?", (session["user_id"],)).fetchone()
    if not cmp or cmp["status"] != "Approved":
        conn.close()
        return jsonify({"ok":False,"msg":"Company not approved yet!"})
    did = "DRV"+str(int(datetime.now().timestamp()))
    branches = ",".join(d.get("branches",[]))
    conn.execute("INSERT INTO drives VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (did,cmp["id"],cmp["company_name"],d["role"],d.get("job_type","Full-time"),
         d["ctc"],d.get("location",""),branches,float(d.get("min_cgpa",6.0)),
         d.get("description",""),d.get("rounds",""),d["last_date"],
         d.get("drive_date",""),d.get("status","Open"),now()))
    conn.commit()
    students = conn.execute(
        "SELECT u.email, u.name, s.cgpa, s.branch FROM students s JOIN users u ON s.user_id=u.id WHERE s.cgpa>=? AND s.placed=0",
        (float(d.get("min_cgpa",6.0)),)).fetchall()
    conn.close()
    for stu in students:
        if stu["branch"] in branches:
            email_drive_announcement(stu["name"],stu["email"],cmp["company_name"],d["role"],d["ctc"],d.get("min_cgpa",6.0),d["last_date"])
    return jsonify({"ok":True})

@app.route("/api/drives/<did>", methods=["PUT"])
@login_required
def update_drive(did):
    d = request.get_json()
    conn = get_db()
    conn.execute("UPDATE drives SET role=?,ctc=?,location=?,min_cgpa=?,description=?,last_date=?,drive_date=?,status=?,rounds=? WHERE id=?",
        (d["role"],d["ctc"],d["location"],float(d["min_cgpa"]),d["description"],d["last_date"],d.get("drive_date",""),d.get("status","Open"),d.get("rounds",""),did))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

@app.route("/api/drives/<did>", methods=["DELETE"])
@login_required
def delete_drive(did):
    conn = get_db()
    conn.execute("DELETE FROM drives WHERE id=?", (did,))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

# ── APPLICATIONS ──────────────────────────────────────────────
@app.route("/api/apply/<did>", methods=["POST"])
@login_required
def apply(did):
    conn = get_db()
    if conn.execute("SELECT 1 FROM applications WHERE drive_id=? AND student_id=?",
        (did, session["user_id"])).fetchone():
        conn.close()
        return jsonify({"ok":False,"msg":"Already applied!"})
    drv = conn.execute("SELECT * FROM drives WHERE id=?", (did,)).fetchone()
    stu = conn.execute("SELECT * FROM students WHERE user_id=?", (session["user_id"],)).fetchone()
    if not drv or not stu:
        conn.close()
        return jsonify({"ok":False,"msg":"Invalid request!"})
    if stu["cgpa"] < drv["min_cgpa"]:
        conn.close()
        return jsonify({"ok":False,"msg":f"Min CGPA required: {drv['min_cgpa']}"})
    aid = "APP"+str(int(datetime.now().timestamp()))
    conn.execute("INSERT INTO applications VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (aid,did,session["user_id"],session["user_name"],
         drv["company_name"],drv["role"],"Applied","","",now(),now()))
    conn.commit()
    # Email to student — application submitted confirmation
    email_application_status(
        session["user_name"], session["user_email"],
        drv["company_name"], drv["role"], "Applied", "",
        "Your application has been submitted successfully!"
    )
    # Email to company HR — new application alert
    hr = conn.execute("SELECT hr_email FROM companies WHERE id=?", (drv["company_id"],)).fetchone()
    if hr:
        email_new_application(
            drv["company_name"], hr["hr_email"],
            session["user_name"], drv["role"],
            stu["branch"], stu["cgpa"], stu["skills"]
        )
    conn.close()
    return jsonify({"ok":True})

@app.route("/api/applications")
@login_required
def get_applications():
    conn = get_db()
    role = session["role"]
    if role == "student":
        apps = [dict(r) for r in conn.execute("SELECT * FROM applications WHERE student_id=? ORDER BY rowid DESC", (session["user_id"],)).fetchall()]
    elif role == "company":
        cid = conn.execute("SELECT id FROM companies WHERE user_id=?", (session["user_id"],)).fetchone()
        apps = [dict(r) for r in conn.execute(
            "SELECT a.*, s.cgpa, s.branch, s.skills, u.phone FROM applications a JOIN students s ON a.student_id=s.user_id JOIN users u ON a.student_id=u.id JOIN drives d ON a.drive_id=d.id WHERE d.company_id=? ORDER BY a.rowid DESC",
            (cid["id"],)).fetchall()] if cid else []
    else:
        apps = [dict(r) for r in conn.execute(
            "SELECT a.*, s.cgpa, s.branch FROM applications a JOIN students s ON a.student_id=s.user_id ORDER BY a.rowid DESC").fetchall()]
    conn.close()
    return jsonify(apps)

@app.route("/api/applications/<aid>/update", methods=["PUT"])
@login_required
def update_application(aid):
    d = request.get_json()
    status  = d.get("status","")
    round_n = d.get("round","")
    message = d.get("message","")
    conn = get_db()
    conn.execute("UPDATE applications SET status=?,current_round=?,hr_message=?,updated_on=? WHERE id=?",
        (status, round_n, message, now(), aid))
    conn.commit()
    app_row = conn.execute("SELECT * FROM applications WHERE id=?", (aid,)).fetchone()
    student = conn.execute("SELECT u.email,u.name FROM users u WHERE u.id=?", (app_row["student_id"],)).fetchone()
    conn.close()
    if student:
        if status == "Interview":
            email_interview_call(student["name"],student["email"],app_row["company_name"],
                app_row["role"],round_n,d.get("datetime",now()),
                d.get("venue","Placement Cell, SMD College"),d.get("instructions",""))
        else:
            email_application_status(student["name"],student["email"],
                app_row["company_name"],app_row["role"],status,round_n,message)
    return jsonify({"ok":True})

# ── OFFER LETTERS ─────────────────────────────────────────────
@app.route("/api/offer", methods=["POST"])
@login_required
def issue_offer():
    d = request.get_json()
    conn = get_db()
    oid = "OFR"+str(int(datetime.now().timestamp()))
    conn.execute("INSERT INTO offer_letters VALUES(?,?,?,?,?,?,?,?,?)",
        (oid,d["student_id"],d["student_name"],d["company_name"],d["role"],
         d["ctc"],d["joining_date"],today(),session["user_name"]))
    conn.execute("UPDATE students SET placed=1,placed_company=?,placed_role=?,placed_ctc=? WHERE user_id=?",
        (d["company_name"],d["role"],d["ctc"],d["student_id"]))
    conn.execute("UPDATE applications SET status='Selected' WHERE student_id=? AND company_name=?",
        (d["student_id"],d["company_name"]))
    conn.commit()
    stu = conn.execute("SELECT email FROM users WHERE id=?", (d["student_id"],)).fetchone()
    conn.close()
    if stu:
        email_offer_letter(d["student_name"],stu["email"],d["company_name"],d["role"],d["ctc"],d["joining_date"])
    return jsonify({"ok":True,"offer_id":oid})

@app.route("/api/offers")
@login_required
def get_offers():
    conn = get_db()
    if session["role"] == "student":
        offers = [dict(r) for r in conn.execute("SELECT * FROM offer_letters WHERE student_id=?", (session["user_id"],)).fetchall()]
    else:
        offers = [dict(r) for r in conn.execute("SELECT * FROM offer_letters ORDER BY rowid DESC").fetchall()]
    conn.close()
    return jsonify(offers)

# ── COMPANIES ─────────────────────────────────────────────────
@app.route("/api/companies")
@login_required
def get_companies():
    conn = get_db()
    comps = [dict(r) for r in conn.execute("SELECT * FROM companies ORDER BY rowid DESC").fetchall()]
    conn.close()
    return jsonify(comps)

@app.route("/api/companies/<cid>/approve", methods=["PUT"])
@admin_required
def approve_company(cid):
    conn = get_db()
    conn.execute("UPDATE companies SET status='Approved',approved_on=? WHERE id=?", (today(),cid))
    comp = conn.execute("SELECT * FROM companies WHERE id=?", (cid,)).fetchone()
    conn.commit(); conn.close()
    if comp:
        email_company_approved(comp["hr_name"],comp["hr_email"],comp["company_name"])
    return jsonify({"ok":True})

@app.route("/api/companies/<cid>/reject", methods=["PUT"])
@admin_required
def reject_company(cid):
    conn = get_db()
    conn.execute("UPDATE companies SET status='Rejected' WHERE id=?", (cid,))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

# ── STUDENTS ──────────────────────────────────────────────────
@app.route("/api/students")
@login_required
def get_students():
    conn = get_db()
    students = [dict(r) for r in conn.execute(
        "SELECT u.id,u.name,u.email,u.phone,s.* FROM users u JOIN students s ON u.id=s.user_id ORDER BY u.rowid DESC").fetchall()]
    conn.close()
    return jsonify(students)

@app.route("/api/students/profile", methods=["PUT"])
@login_required
def update_profile():
    d = request.get_json()
    conn = get_db()
    conn.execute("UPDATE students SET branch=?,cgpa=?,skills=?,projects=?,internships=?,achievements=?,linkedin=?,github=? WHERE user_id=?",
        (d.get("branch",""),float(d.get("cgpa",0)),d.get("skills",""),d.get("projects",""),
         d.get("internships",""),d.get("achievements",""),d.get("linkedin",""),d.get("github",""),session["user_id"]))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

# ── NOTICES ───────────────────────────────────────────────────
@app.route("/api/notices")
@login_required
def get_notices():
    conn = get_db()
    notices = [dict(r) for r in conn.execute("SELECT * FROM notices ORDER BY rowid DESC").fetchall()]
    conn.close()
    return jsonify(notices)

@app.route("/api/notices", methods=["POST"])
@admin_required
def add_notice():
    d = request.get_json()
    nid = "NOT"+str(int(datetime.now().timestamp()))
    conn = get_db()
    conn.execute("INSERT INTO notices VALUES(?,?,?,?,?,?)",
        (nid,d["title"],d["content"],session["user_name"],d.get("priority","Normal"),now()))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

@app.route("/api/notices/<nid>", methods=["DELETE"])
@admin_required
def delete_notice(nid):
    conn = get_db()
    conn.execute("DELETE FROM notices WHERE id=?", (nid,))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

# ── STATS ─────────────────────────────────────────────────────
@app.route("/api/stats")
@admin_required
def get_stats():
    conn = get_db()
    placed     = conn.execute("SELECT COUNT(*) FROM students WHERE placed=1").fetchone()[0]
    not_placed = conn.execute("SELECT COUNT(*) FROM students WHERE placed=0").fetchone()[0]
    avg_cgpa   = conn.execute("SELECT ROUND(AVG(cgpa),2) FROM students").fetchone()[0]
    branch_stat= [dict(r) for r in conn.execute("SELECT branch,COUNT(*) as total,SUM(placed) as placed_count FROM students GROUP BY branch").fetchall()]
    comp_stat  = [dict(r) for r in conn.execute("SELECT company_name,COUNT(*) as hired FROM students WHERE placed=1 GROUP BY placed_company").fetchall()]
    conn.close()
    return jsonify({"placed":placed,"not_placed":not_placed,"avg_cgpa":avg_cgpa,"branch_stat":branch_stat,"comp_stat":comp_stat})

if __name__ == "__main__":
    init_db()
    print("="*55)
    print("  🎓 CampusHire — Campus Hiring System")
    print("="*55)
    print("  Open   : http://localhost:5000")
    print("  Admin  : tarakalal052@gmail.com / admin123")
    print("  Company: kalalindu951@gmail.com / hr123")
    print("  Student: kavya@gmail.com / stu123")
    print("="*55)
    app.run(debug=True)
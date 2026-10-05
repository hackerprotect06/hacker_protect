from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import re
import urllib.parse
from functools import wraps

app = Flask(__name__)
app.secret_key = "cyber_sec_ai_secret_key"

DB_NAME = "database.db"

# 1. تهيئة قاعدة البيانات (جدول المستخدمين وجدول الفحوصات)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # جدول المستخدمين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # جدول الفحوصات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            scan_type TEXT NOT NULL,
            input_data TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# مزخرف (Decorator) لحماية الصفحات ومنع غير المسجلين من دخولها
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("يرجى تسجيل الدخول أولاً للوصول إلى هذه الصفحة.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- منطق الأدوات الأمنية ---
def analyze_code_with_ai(code):
    lowered = code.lower()
    issues = []
    if "select *" in lowered and "where" in lowered and "+" in lowered:
        issues.append("⚠️ ثغرة SQL Injection: عدم استخدام الاستعلامات المجهزة.")
    if "eval(" in lowered:
        issues.append("🚨 ثغرة خطيرة (Arbitrary Code Execution): استخدام eval().")
    if "system(" in lowered or "exec(" in lowered:
        issues.append("⚠️ ثغرة Command Injection: تنفيذ أوامر النظام دون تنقية.")
    if "password" in lowered and "=" in lowered and ("123" in lowered or "admin" in lowered):
        issues.append("🔑 كلمات مرور مكشوفة داخل الكود (Hardcoded Credentials).")

    return "✅ الكود يبدو آمناً مبدئياً." if not issues else "🛡️️ التقرير الأمني:\n" + "\n".join(issues)

def analyze_url_with_ai(url):
    reasons = []
    score = 100
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc

    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain):
        reasons.append("🚨 استخدام عنوان IP مباشر بدلاً من اسم النطاق.")
        score -= 40
    for word in ["login", "verify", "secure", "bank", "update", "account", "paypal"]:
        if word in domain.lower() and not domain.endswith(word + ".com"):
            reasons.append(f"⚠️ وجود كلمة مشبوهة ('{word}') لتضليل المستخدم.")
            score -= 25

    return f"✅ الرابط آمن بنسبة {score}%" if score >= 80 else f"🚨 تحذير: الرابط مشبوه! درجة الأمان {score}%\nالأسباب:\n" + "\n".join(reasons)

# --- المسارات (Routes) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        if action == 'register':
            full_name = request.form.get('full_name', '').strip()
            try:
                cursor.execute("INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
                               (full_name, email, password))
                conn.commit()
                flash("تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.", "success")
            except sqlite3.IntegrityError:
                flash("البريد الإلكتروني مسجل بالفعل!", "danger")
            conn.close()
            return redirect(url_for('login'))

        elif action == 'login':
            cursor.execute("SELECT id, full_name FROM users WHERE email=? AND password=?", (email, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                return redirect(url_for('index'))
            else:
                flash("البريد الإلكتروني أو كلمة المرور غير صحيحة.", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE user_id=? ORDER BY created_at DESC", (session['user_id'],))
    scans = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', scans=scans)

@app.route('/services/code-auditor', methods=['GET', 'POST'])
@login_required
def code_auditor():
    result = None
    if request.method == 'POST':
        user_code = request.form.get('code', '')
        if user_code.strip():
            result = analyze_code_with_ai(user_code)
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO scans (user_id, scan_type, input_data, result) VALUES (?, ?, ?, ?)",
                           (session['user_id'], "فحص كود برمجي", user_code[:80] + "...", result))
            conn.commit()
            conn.close()
    return render_template('code_checker.html', result=result)

@app.route('/services/url-checker', methods=['GET', 'POST'])
@login_required
def url_checker():
    result = None
    if request.method == 'POST':
        user_url = request.form.get('url', '')
        if user_url.strip():
            result = analyze_url_with_ai(user_url)
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO scans (user_id, scan_type, input_data, result) VALUES (?, ?, ?, ?)",
                           (session['user_id'], "فحص رابط مشبوه", user_url, result))
            conn.commit()
            conn.close()
    return render_template('url_checker.html', result=result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
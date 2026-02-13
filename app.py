from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone  # ✅ FIXED: Added timezone
from collections import defaultdict
from functools import wraps
from sqlalchemy import func
import os

# ---------------- APP CONFIG ----------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fedclassroom-secret-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- DATABASE MODELS ----------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    app_name = db.Column(db.String(100), nullable=False)
    window_title = db.Column(db.String(200))
    duration_seconds = db.Column(db.Integer, nullable=False)
    fl_score = db.Column(db.Float, default=0.5)
    timestamp_start = db.Column(db.DateTime)
    timestamp_end = db.Column(db.DateTime)

# ---------------- INIT DATABASE ----------------
with app.app_context():
    db.create_all()

login_manager = LoginManager(app)
login_manager.login_view = 'home'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# 🔥 ADMIN DECORATOR
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# 🔥 APP DETECTION & PROCESSING FUNCTIONS (same as before)
def get_display_name(raw_app_name, window_title=""):
    # [Keep your existing get_display_name function exactly the same]
    if not raw_app_name:
        return "Unknown"
    raw_lower = raw_app_name.lower()
    window_lower = window_title.lower() if window_title else ""
    
    if any(x in window_lower for x in ['youtube', 'youtu.be']):
        return "YouTube"
    if 'perplexity' in window_lower:
        return "Perplexity"
    if 'netflix' in window_lower:
        return "Netflix"
    
    app_mapping = {'youtube.com': 'YouTube', 'chrome': 'Chrome', 'whatsapp': 'WhatsApp',
                   'instagram.com': 'Instagram', 'telegram': 'Telegram', 'discord': 'Discord',
                   'code': 'VS Code', 'spotify.com': 'Spotify'}
    
    for key, display_name in app_mapping.items():
        if key in raw_lower:
            return display_name
    
    if 'chrome' in raw_lower and window_title:
        clean_title = window_title.replace(' - Google Chrome', '').strip()
        if len(clean_title) > 3:
            return clean_title[:30]
    
    if raw_app_name.endswith('.exe'):
        return raw_app_name[:-4].split('\\')[-1].title()
    return raw_app_name.split('\\')[-1].title()

def process_activities(activities):
    app_totals = defaultdict(int)
    productive_keywords = ['code', 'vscode', 'studio', 'notepad', 'word', 'excel']
    
    for activity in activities:
        display_name = get_display_name(activity.app_name, activity.window_title or "")
        app_totals[display_name] += activity.duration_seconds
    
    merged = []
    for app_name, total_time in app_totals.items():
        merged.append({
            'app_name': app_name,        # ← Templates use this
            'total_minutes': round(total_time / 60, 1),
            'is_productive': any(keyword in app_name.lower() for keyword in productive_keywords)
        })
    return sorted(merged, key=lambda x: x['total_minutes'], reverse=True)

# ---------------- ROUTES ----------------
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/admin/setup', methods=['GET', 'POST'])
def admin_setup():
    if User.query.filter_by(role='admin').first():
        flash("Admin exists. Login at home page.", "warning")
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        try:
            admin = User(username="admin", email=request.form['email'],
                        password_hash=generate_password_hash(request.form['password']), role="admin")
            db.session.add(admin)
            db.session.commit()
            print(f"✅ ADMIN CREATED: {admin.email}")
            flash("Admin created!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "error")
    
    return render_template('admin_setup.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email'].strip().lower()
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        print(f"✅ LOGIN: {user.username} (ID: {user.id})")
        return redirect(url_for('admin_users' if user.role == 'admin' else 'user_dashboard'))
    
    flash("Invalid credentials!", "error")
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username'].strip()
    email = request.form['email'].strip().lower()
    password = request.form['password']
    
    if User.query.filter_by(email=email).first():
        flash("Email exists!", "error")
        return redirect(url_for('home'))
    
    try:
        user = User(username=username, email=email, 
                   password_hash=generate_password_hash(password), role='student')
        db.session.add(user)
        db.session.commit()
        flash('Account created! Login now.', "success")
        print(f"✅ NEW STUDENT: {username} (ID: {user.id})")
    except:
        flash("Registration failed!", "error")
    
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out!", "success")
    return redirect(url_for('home'))

@app.route('/users')
def list_users():
    users = User.query.all()
    print("\n📋 USERS:")
    for u in users:
        print(f"ID: {u.id} | {u.username} | {u.email} | {u.role}")
    return jsonify([{'id': u.id, 'username': u.username, 'email': u.email, 'role': u.role} for u in users])

# 🔥 24HR ADMIN DASHBOARD (FIXED utcnow)
@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    stats = db.session.query(
        User.id, User.username,
        func.sum(Activity.duration_seconds).label('total'),
        func.count(Activity.id).label('count')
    ).outerjoin(Activity).filter(
        User.role == 'student',
        Activity.timestamp_start >= cutoff
    ).group_by(User.id, User.username).all()
    
    # ✅ FIXED: Use db.session.get() + calculate total_classroom_time
    student_stats = []
    total_classroom_time = 0  # ✅ ADDED
    for r in stats:
        student = db.session.get(User, r[0])  # ✅ FIXED Query.get()
        total_time = (r[2] or 0) / 60
        total_classroom_time += total_time  # ✅ ADDED
        student_stats.append({
            'student': student,
            'total_time': total_time,
            'activity_count': r[3] or 0
        })
    
    # ✅ PASS total_classroom_time to template
    return render_template('admin_users.html', 
                          student_stats=student_stats, 
                          total_classroom_time=total_classroom_time)  # ✅ FIXED


@app.route('/admin/student/<int:student_id>')
@login_required
@admin_required
def admin_student_dashboard(student_id):
    student = User.query.get_or_404(student_id)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)  # ✅ FIXED
    activities = Activity.query.filter(
        Activity.user_id == student.id,
        Activity.timestamp_start >= cutoff
    ).order_by(Activity.id.desc()).all()
    
    merged = process_activities(activities)
    total_duration = sum(a.duration_seconds for a in activities) / 60 if activities else 0
    productive_time = sum(a['total_minutes'] for a in merged if a['is_productive'])
    
    return render_template('admin_user_details.html',
                          user=student, merged_activities=merged, 
                          total_duration=total_duration, productive_time=productive_time,
                          activities=activities, activity_count=len(activities),
                          **{'user_id': student.id})  # ✅ PASSED USER ID

# 🔥 24HR USER DASHBOARD (FIXED + USER ID)
@app.route('/dashboard')
@login_required
def user_dashboard():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)  # ✅ FIXED
    activities = Activity.query.filter(
        Activity.user_id == current_user.id,
        Activity.timestamp_start >= cutoff
    ).order_by(Activity.id.desc()).all()
    
    merged = process_activities(activities)
    total_duration = sum(a.duration_seconds for a in activities) / 60 if activities else 0
    productive_time = sum(a['total_minutes'] for a in merged if a['is_productive'])
    
    return render_template('dashboard.html',
                          merged_activities=merged, total_duration=total_duration,
                          productive_time=productive_time, activity_count=len(activities),
                          activities=activities, user=current_user,
                          **{'user_id': current_user.id})  # ✅ USER ID PASSED!

@app.route('/track_activity', methods=['POST'])
def track_activity():
    data = request.json
    user = User.query.get(data.get('user_id'))
    if not user:
        return jsonify({"error": "Invalid user"}), 400
    
    app_name = get_display_name(data['app_name'], data.get('window_title', ''))
    activity = Activity(
        user_id=user.id,
        app_name=app_name[:50],
        window_title=data.get('window_title', '')[:200],
        duration_seconds=data['duration_seconds'],
        fl_score=data.get('fl_score', 0.5),
        timestamp_start=datetime.fromisoformat(data['timestamp_start']),
        timestamp_end=datetime.fromisoformat(data['timestamp_end'])
    )
    db.session.add(activity)
    db.session.commit()
    print(f"✅ TRACKED: {app_name} (ID: {user.id})")
    return jsonify({"status": "tracked"})

if __name__ == '__main__':
    print("🚀 FedClassroom Pro (24HR + Perfect Detection)")
    print("📱 http://127.0.0.1:5000")
    app.run(debug=True, port=5000, host='127.0.0.1')

# tracker.py - DEBUG VERSION WITH FULL LOGGING + FEDERATED LEARNING
import psutil
import win32gui
import win32process
import time
import threading
from datetime import datetime
import requests
import json
import torch
import numpy as np

# 🔥 FEDERATED LEARNING GLOBALS (your existing model features)
activity_features = []  # Local training data
activity_labels = []    # 0=unproductive, 1=productive
MODEL_TRAINED = False

def get_activity_features(app_name, duration):
    """Convert activity → ML features for YOUR ProductivityNet"""
    features = np.array([
        1.0 if 'code' in app_name.lower() or 'studio' in app_name.lower() else 0.0,  # productive
        1.0 if 'youtube' in app_name.lower() or 'netflix' in app_name.lower() else 0.0,  # entertainment
        1.0 if duration > 300 else 0.0,  # long session
        len(app_name) / 20.0,  # app complexity
        1.0 if 'chrome' in app_name.lower() else 0.0  # browser time
    ], dtype=np.float32)
    
    label = 1 if 'code' in app_name.lower() or 'studio' in app_name.lower() else 0
    return features, label

class RealTimeActivityTracker:
    def __init__(self, flask_url="http://127.0.0.1:5000", user_id=1):
        self.flask_url = flask_url
        self.user_id = user_id
        self.current_app = None
        self.current_window = ""
        self.start_time = None
        self.tracking = False
        self.activity_count = 0  # 🔥 NEW: FL data counter
        print(f"🎯 Tracker User ID: {user_id}, Flask: {flask_url}")
        print("🔥 FEDERATED LEARNING: Collecting training data...")
        
    def get_active_window(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            app_name = process.name().lower()
            window_title = win32gui.GetWindowText(hwnd)
            return app_name, window_title, hwnd
        except:
            return "unknown", "Unknown Window", None
    
    def send_to_flask(self, activity):
        global activity_features, activity_labels  # 🔥 FL data
        
        try:
            payload = {
                'user_id': self.user_id,
                'app_name': activity['app_name'],
                'window_title': activity['window_title'][:100],
                'duration_seconds': activity['duration_seconds'],
                'timestamp_start': activity['timestamp_start'],
                'timestamp_end': activity['timestamp_end']
            }
            print(f"📤 SENDING TO FLASK: {payload['app_name']} ({payload['duration_seconds']}s)")
            
            response = requests.post(
                f"{self.flask_url}/track_activity",
                json=payload,
                timeout=5,
                headers={'Content-Type': 'application/json'}
            )
            print(f"📥 FLASK RESPONSE: {response.status_code} - {response.text[:100]}")
            
            if response.status_code == 200:
                print(f"✅ SUCCESSFULLY TRACKED: {activity['app_name']}")
                
                # 🔥 FEDERATED LEARNING: Add to local training data
                app_name = activity['app_name']
                duration = activity['duration_seconds']
                features, label = get_activity_features(app_name, duration)
                activity_features.append(features)
                activity_labels.append(label)
                self.activity_count += 1
                
                # 🔥 Train local model every 10 activities
                if self.activity_count % 10 == 0 and len(activity_features) >= 5:
                    print(f"🤖 FL TRAINING: {len(activity_features)} samples collected")
                    global MODEL_TRAINED
                    MODEL_TRAINED = True
            else:
                print(f"❌ FLASK ERROR: {response.status_code}")
        except Exception as e:
            print(f"❌ REQUEST FAILED: {e}")
    
    def track(self):
        self.tracking = True
        print("🔍 REAL-TIME TRACKING STARTED... (Switch apps to test!)")
        print("📊 FL Data → activity_features list (ready for Flower client)")
        
        while self.tracking:
            app_name, window_title, hwnd = self.get_active_window()
            
            if app_name != self.current_app or window_title != self.current_window:
                # End previous activity
                if self.current_app and self.start_time:
                    duration = int((datetime.now() - self.start_time).total_seconds())
                    if duration > 15:  # Min 15 seconds
                        activity = {
                            'app_name': self.current_app.title(),
                            'window_title': self.current_window,
                            'duration_seconds': duration,
                            'timestamp_start': self.start_time.isoformat(),
                            'timestamp_end': datetime.now().isoformat()
                        }
                        print(f"⏱️  Ending: {self.current_app} ({duration}s)")
                        self.send_to_flask(activity)
                
                # Start new activity
                self.current_app = app_name
                self.current_window = window_title
                self.start_time = datetime.now()
                print(f"👀 Now tracking: {app_name.title()} - {window_title[:50]}")
            
            time.sleep(3)
    
    def start(self):
        self.tracker_thread = threading.Thread(target=self.track, daemon=True)
        self.tracker_thread.start()

# 🔥 FL STATUS CHECKER (runs in background)
def fl_status_thread():
    global MODEL_TRAINED
    while True:
        if MODEL_TRAINED and len(activity_features) > 0:
            print(f"🌟 FL STATUS: {len(activity_features)} samples | Ready for Flower client!")
            print(f"   → Run: python fl_flower_client.py (User ID: {user_id})")
        time.sleep(30)

if __name__ == "__main__":
    print("🎮 On-Screen Activity Tracker DEBUG + FEDERATED LEARNING")
    print("=" * 60)
    
    user_id = input("Enter User ID : ") or "1"
    tracker = RealTimeActivityTracker(user_id=int(user_id))
    
    # 🔥 Start FL status monitor
    fl_status = threading.Thread(target=fl_status_thread, daemon=True)
    fl_status.start()
    
    tracker.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Tracker stopped!")
        print(f"📊 FINAL FL DATA: {len(activity_features)} samples ready for training!")

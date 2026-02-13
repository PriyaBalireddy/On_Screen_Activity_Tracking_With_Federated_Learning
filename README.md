# 🖥️ ON SCREEN ACTIVITY TRACKING WITH FEDERATED LEARNING

---

## 📌 Project Overview

ON SCREEN ACTIVITY TRACKING WITH FEDERATED LEARNING is a privacy-preserving productivity monitoring system that analyzes user screen activity and application usage patterns without compromising personal data security.

The system tracks screen time, classifies application usage into productive and non-productive categories, and generates productivity insights — all while ensuring that raw user data never leaves the local device.

This project leverages Federated Learning to train machine learning models collaboratively across multiple devices while maintaining strict privacy protection.

---

## 🎯 Objectives

- Monitor real-time screen activity  
- Track application usage patterns  
- Classify apps as productive / non-productive  
- Generate productivity scores  
- Preserve user privacy using Federated Learning  
- Provide visual productivity insights  

---

## 🚀 Key Features

- 🔐 Privacy-First Architecture  
- 🧠 Federated Machine Learning Models  
- 📊 Productivity Score Calculation  
- 📈 Pie Chart Visualizations  
- 🖥️ Real-Time Activity Tracking  
- 📂 Application Usage Reports  
- 👤 Role-Based Dashboard (Admin/User)  

---

## 🧠 Technologies Used

### Programming & Frameworks
- Python  
- Flask  
- HTML  
- CSS  
- JavaScript  

### Machine Learning
- Decision Tree Classifier  
- Linear Discriminant Analysis (LDA)  

### Federated Learning
- Distributed Model Training  
- Secure Model Aggregation  

### Visualization
- Matplotlib / Chart.js  

---

## 🏗️ System Architecture

The system works in four major stages:

1. **Data Collection**
   - Tracks app usage  
   - Records screen time  
   - Runs locally on device  

2. **Feature Extraction**
   - Session duration  
   - App frequency  
   - Usage patterns  

3. **Local Model Training**
   - Decision Tree  
   - LDA Classification  

4. **Federated Learning Aggregation**
   - Shares model updates only  
   - No raw data transfer  
   - Builds global productivity model  

---

## 📊 Productivity Score Formula

```
Productivity Score (%) =
(Productive Time / Total Screen Time) × 100
```

---

## 📸 Output Visualizations

- Productivity vs Non-Productivity Pie Chart  
- Daily Screen Time Reports  
- App Usage Dashboard  
- Real-Time Activity Monitor  

---

## 🔒 Privacy & Security

- No screenshots captured  
- No keystroke logging  
- No raw data sharing  
- Encrypted model updates  
- Differential privacy support  

---

## 📂 Project Structure

```
ACTIVITYWEBAPP/
│
├── app.py
├── server.py
├── tracker.py
├── client.py
├── create_admin.py
├── save_model.py
├── global_model.pth
│
├── templates/
│   ├── admin_user_details.html
│   ├── admin_users.html
│   ├── base.html
│   ├── dashboard.html
│   └── home.html
│
├── static/
│   └── tracker.js
│
├── instance/
│   └── users.db
│
└── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```
git clone https://github.com/your-username/on-screen-activity-tracking-with-federated-learning.git
cd on-screen-activity-tracking-with-federated-learning
```

### 2️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

## ▶️ How to Run the Project

This system runs using three parallel services.

Open **3 terminals** in the project folder and execute:

### Terminal 1 — Main Flask Application
```
python app.py
```

### Terminal 2 — Federated Learning Server
```
python server.py
```

### Terminal 3 — Activity Tracker
```
python tracker.py
```

Make sure all three services are running simultaneously for full system functionality.

---

## 📊 Performance Highlights

| Metric | Traditional System | Proposed System |
|-------|-------------------|----------------|
| Accuracy | 72% | 86% |
| Privacy | Low | High |
| Data Storage | Centralized | Local |
| Server Load | High | Reduced |
| Processing | Delayed | Real-Time |

---

## 🔮 Future Enhancements

- AI Productivity Recommendations  
- Focus Mode App Blocking  
- Multi-Device Synchronization  
- Wearable Device Integration  
- Cognitive Load Detection  

---

## 👩‍💻 Authors
- Sane Sasikala
- Balireddy Raghava Priya    
- Sribhashyam Mohana Sri  
- Shaik Ashfaq Hussain  

**Department of CSE (AI & ML)**

---

## 📜 Publication

IEEE Conference Paper:  
**ON SCREEN ACTIVITY TRACKING WITH FEDERATED LEARNING**

---

## 📬 Contact

📧 balireddypriya957@gmail.com  

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!


# On_Screen_Activity_Tracking_With_Federated_Learning

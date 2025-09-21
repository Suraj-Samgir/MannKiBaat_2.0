# 🌸 Mann Ki Baat 2.0 – AI-Powered Student Mental Wellness Platform

> **Confidential | Empathetic | AI-Driven | Student-First**  

Mann Ki Baat 2.0 is a confidential, AI-powered mental wellness platform designed specifically for students.  
It provides a safe space to express emotions, get actionable lifestyle tips, receive motivational nudges, and build healthy mental habits — all while staying anonymous.

---

## 🚀 Problem Statement

Mental health remains a taboo topic in India, and students often hesitate to seek help due to fear of judgment, social stigma, or high costs of therapy.  
As a result, stress, burnout, anxiety, and depression among youth are rising.

---

## 🎯 Vision

> **"To make mental wellness accessible, stigma-free, and a part of every student's daily routine by blending Generative AI, personalization, and cultural sensitivity."**

---

## 🛠 Features

- 💬 **AI Chatbot** – A Hinglish-friendly conversational buddy to talk, vent, and seek advice.  
- 🚨 **Crisis Detection** – Detects emotionally critical situations and nudges toward safe actions.  
- ✨ **Daily Affirmations** – Motivational nudges that refresh every day.  
- 🛌 **Lifestyle Suggestions** – Practical, personalized tips to improve sleep, focus, and stress.  
- 🎮 **Activities & Challenges** – Fun tasks and streak-based engagement for habit building.  
- 📊 **Progress Tracking** – Streak counters, saved affirmations, and completed challenges.

---

## 🖼 Process Flow

1. **Landing Page** → Welcome & CTA  
2. **Personalized Onboarding** → Capture student info & lifestyle data  
3. **Category Selection** → Choose problem areas like career, health, relationships  
4. **AI Dashboard** → Chatbot, daily affirmation, lifestyle tips  
5. **Gamified Experience** → Track streaks, earn badges, stay engaged  

---


---

## 💻 Tech Stack

- **Frontend:** HTML5, CSS3, Bootstrap 5, Jinja2  
- **Backend:** Flask (Python)  
- **Database:** SQLite (prototype), scalable to Firestore/Cloud SQL  
- **AI/ML:** Google Gemini API (Generative AI), Perspective API (moderation)  
- **Security:** bcrypt password hashing, Flask-Session  
- **Deployment:** Google Cloud (Cloud Run / App Engine)

---

## 📦 Installation & Setup

```bash
# 1️⃣ Clone the Repository
git clone https://github.com/<your-username>/mann-ki-baat-2.0.git
cd mann-ki-baat-2.0

# 2️⃣ Create & Activate Virtual Environment
python -m venv venv
# Activate the environment:
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 3️⃣ Install Dependencies
pip install -r requirements.txt

# 4️⃣ Setup Environment Variables
# Create a .env file in the project root and add:
# GEMINI_API_KEY=your_google_gemini_api_key

# 5️⃣ Run the Application
python ./app.py

# The app will now be available at:
# http://127.0.0.1:5000/

# 🛡️ Aegis — AI Safety Middleware

**Aegis** is a real-time **AI safety layer** that protects students and everyday users from accidentally leaking sensitive information while interacting with AI tools.

Instead of replacing AI assistants, Aegis works as a **protective middleware** that intercepts prompts, analyzes risk, and ensures safe AI usage.

---

## 🚨 Problem Statement

AI adoption is growing rapidly, but users unknowingly share:

- 🔑 Passwords and credentials  
- 📧 Personal information (emails, phone numbers, IDs)  
- 📄 Sensitive documents  
- ⚠️ Risky or unsafe requests  

Currently, **no safety layer exists between users and AI systems**.

---

## ✅ Our Solution

Aegis secures human-AI interaction by:

- Intercepting prompts **before they leave the device**
- Detecting sensitive data and risky intent
- Automatically sanitizing unsafe prompts
- Screening AI responses for harmful output
- Educating users about safe AI practices

👉 Users continue using AI normally — **but safely**.

---

## ⚙️ How It Works

1. User types a prompt on any AI platform.
2. Aegis browser extension intercepts the prompt locally.
3. Safety Engine performs:
   - NLP intent analysis  
   - Sensitive data detection  
   - Risk scoring
4. Unsafe prompts are automatically rewritten.
5. Only the **safe prompt** is sent to the AI.
6. AI responses are scanned for phishing or unsafe content.
7. User receives secure output + safety explanation.

---

## 🧠 Key Features

- 🔒 **Local Prompt Protection**
- 🤖 **Context-Aware AI Reasoning**
- ✏️ **Automatic Prompt Rewriting**
- 🌐 **Works with Any AI Chatbot**
- 🛡️ **AI Response Safety Filtering**
- 🎓 **Real-Time User Education**

---


---

## 🧩 Tech Stack

### 🖥 Frontend (Demo Interface)
- Streamlit (Model Output Visualization)
- HTML / CSS / JavaScript (Browser Extension UI)

### ⚙️ Backend
- Python
- spaCy (NLP Processing)
- LLaMA / Local LLM
- FastAPI (Production API - Planned)

### 🔐 Detection & Security
- Regex-based PII Detection
- Entropy-based Secret Detection
- Risk Scoring Engine

### 📚 RAG System
- FAISS / ChromaDB
- Policy Knowledge Retrieval

---

## 💻 Usage of AMD Products / Solutions

- Optimized for **AMD Ryzen CPUs**
- Cloud-hosted inference for low-end laptops
- Ready for **AMD Radeon GPU acceleration (ROCm)**
- Future deployment on **AMD Ryzen AI NPUs** for on-device AI

---

## 🖥 Demo Notice

The current **Streamlit interface** is used only for demonstrating model outputs and safety reasoning.

In the production version:

- Aegis runs silently in the background
- Unsafe prompts are automatically replaced
- Users interact with AI normally without seeing internal processing

---

## 🚀 Installation

```bash
git clone https://github.com/your-username/aegis.git
cd aegis
pip install -r requirements.txt
streamlit run app.py

# ◈ PhishBERT-XAI

PhishBERT-XAI is an advanced, hybrid phishing URL detection and automated threat analysis system. It is designed to identify zero-day phishing attacks, typosquatting, homoglyph domain spoofing, and malicious infrastructure with high accuracy.

The system combines a fine-tuned **CANINE Transformer** (a character-level deep learning model) with a robust **Heuristic Engine** to provide transparent, explainable AI (XAI) security threat assessments.

## 🚀 Features

- **Deep Learning Core**: Utilizes Google's CANINE architecture trained on real-world benign and phishing datasets, augmented with synthetic homoglyph samples for advanced typo-squatting detection.
- **Heuristic Engine**: Performs 12 critical security checks, including SSL/HTTPS validation, TLD reputation, raw IP usage, brand impersonation, and phishing keyword detection.
- **XAI Reporting**: Breaks down exactly *why* a URL is considered dangerous, giving security analysts clear visibility into the threat indicators.
- **Modern UI**: A premium, responsive React dashboard featuring real-time scanning and threat scoring.

## 🏗️ Architecture

- **Frontend**: React + Vite + Vanilla CSS
- **Backend**: FastAPI + Python
- **Model**: PyTorch + HuggingFace Transformers (CANINE-c)

## 🛠️ Installation & Setup

### 1. Backend Setup (FastAPI & AI Model)
Navigate to the backend directory, set up your Python environment, and start the server:
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # On Windows
pip install -r requirements.txt
python api.py
```
*Note: The backend API runs on `http://localhost:8000`.*

### 2. Frontend Setup (React UI)
Open a new terminal window, navigate to the frontend directory, and start the development server:
```bash
cd frontend
npm install
npm run dev
```
*Note: The UI runs on `http://localhost:5173`.*

## 🔒 Usage
1. Ensure both the backend and frontend servers are running.
2. Open the UI in your browser.
3. Paste a suspicious URL, domain, or IP address into the centralized search bar.
4. Click **Scan** to receive an instant, explainable threat report.

## 📂 Project Structure
- `/frontend`: Contains all React components, styling (`index.css`), and UI logic.
- `/backend`: Contains the FastAPI application (`api.py`), heuristic logic (`url_analyzer.py`), data loading, and model inference scripts.

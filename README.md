# OpenPath — AI-Powered Personalized Learning

OpenPath is an AI-driven platform that transforms any skill or topic into a structured, manageable learning journey. It leverages Gemini 2.5 Flash to generate custom syllabi and curates high-quality educational content from YouTube.

![OpenPath Landing Page Mockup](https://images.unsplash.com/photo-1516321318423-f06f85e504b3?ixlib=rb-1.2.1&auto=format&fit=crop&w=1200&q=80)
*(Replace with actual screenshot after deployment)*

## 🚀 Key Features

- **AI Syllabus Generation**: Tailored module plans based on your skill level and time commitment.
- **Context-Aware Video Ranking**: Smart selection of high-quality tutorials from trusted channels (Fireship, 3Blue1Brown, etc.).
- **Quiz-to-Skip**: Accelerate your learning by testing out of modules you already master.
- **AI Flashcards**: Automatically distilled knowledge snippets from video transcripts for better retention.
- **Community Marketplace**: Share your learning paths or clone paths built by others.
- **Tokyo Night Aesthetic**: A premium, developer-focused UI with smooth animations.

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [SQLAlchemy](https://www.sqlalchemy.org/) + SQLite / PostgreSQL
- **AI**: [Google Gemini 2.5 Flash](https://ai.google.dev/)
- **Search**: YouTube Data / Search APIs

### Frontend
- **React**: Vite-powered SPA
- **Styling**: Vanilla CSS / Custom Design Tokens
- **Animations**: [Framer Motion](https://www.framer.com/motion/)

## 📦 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Gemini API Key ([Get it here](https://aistudio.google.com/app/apikey))

### Backend Setup
1.  Navigate to the root directory.
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set up your environment variables:
    ```bash
    cp .env.example .env
    # Edit .env and add your GEMINI_API_KEY
    ```
5.  Run the server:
    ```bash
    cd backend
    uvicorn main:app --reload
    ```

### Frontend Setup (React)
1.  Navigate to the `react-frontend` directory.
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```

## 🏗️ Project Structure
```text
OpenPath/
├── backend/               # FastAPI logic & Database models
├── react-frontend/        # Premium React UI
├── frontend/              # Streamlit prototyping interface
├── docker/                # Containerization setup
└── requirements.txt       # Python dependencies
```

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).

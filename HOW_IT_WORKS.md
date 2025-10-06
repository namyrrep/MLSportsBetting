# 🏈 NFL Prediction Bot - Complete Workflow Explanation

## 📚 Table of Contents
1. [Big Picture Overview](#big-picture-overview)
2. [Components Breakdown](#components-breakdown)
3. [Step-by-Step Workflows](#step-by-step-workflows)
4. [Data Flow Diagram](#data-flow-diagram)
5. [File Structure & Responsibilities](#file-structure--responsibilities)

---

## 🎯 Big Picture Overview

**What does this application do?**
- Predicts which NFL team will win upcoming games
- Uses 6 machine learning models trained on real historical data
- Shows predictions in a nice web dashboard
- Automatically updates results when games finish

**Think of it like a robot sports analyst:**
1. 📖 **Learns** from past games (training)
2. 🧠 **Thinks** about upcoming games (prediction)
3. 📊 **Shows** you its predictions (dashboard)
4. ✅ **Checks** if it was right after games finish (evaluation)

---

## 🧩 Components Breakdown

### Backend (Python) - The "Brain"
```
src/
├── data_collector.py      → Fetches game data from ESPN
├── database.py            → Stores everything in SQLite
├── feature_engineering.py → Creates smart stats from raw data
├── ml_models.py          → 6 AI models that make predictions
├── agent.py              → Coordinates everything
└── api_server.py         → Web API that frontend talks to
```

### Frontend (React) - The "Face"
```
frontend/
├── src/
│   ├── App.jsx           → Main dashboard UI
│   └── App.css           → Makes it look pretty
└── package.json          → Lists what libraries it needs
```

### Database (SQLite) - The "Memory"
```
data/
└── nfl_games.db          → Stores all games, predictions, stats
```

### Scripts - The "Helpers"
```
scripts/
├── collect_data.py       → Fetch historical game data
├── train.py              → Train ML models
├── predict.py            → Generate predictions
└── update_results.py     → Update finished games
```

---

## 🔄 Step-by-Step Workflows

### Workflow 1: Initial Setup (One-Time)
```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Install Dependencies                                │
│ ────────────────────────────────────────────────────────── │
│ Command: pip install -r requirements.txt                    │
│ What it does: Installs Python libraries (pandas, sklearn)   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Initialize Database                                 │
│ ────────────────────────────────────────────────────────── │
│ Command: python scripts/init_database.py                    │
│ What it does: Creates empty database with tables           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Collect Historical Data                            │
│ ────────────────────────────────────────────────────────── │
│ Command: python scripts/collect_data.py                     │
│ What it does: Fetches 2023-2024 games from ESPN            │
│ Result: ~544 games stored in database                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Train ML Models                                     │
│ ────────────────────────────────────────────────────────── │
│ Command: python scripts/train.py                            │
│ What it does: Teaches 6 models to predict winners          │
│ Result: Trained models saved to models/ folder             │
└─────────────────────────────────────────────────────────────┘
```

### Workflow 2: Making Predictions (Weekly)
```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Fetch This Week's Games                            │
│ ────────────────────────────────────────────────────────── │
│ File: src/data_collector.py                                │
│ Function: get_games_for_week(2025, 6)                      │
│                                                             │
│ ESPN API → data_collector.py → database                     │
│                                                             │
│ Example Data:                                               │
│   Game: CHI @ WSH                                           │
│   Date: 2025-10-13                                          │
│   Teams: Bears vs Commanders                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Engineer Features                                   │
│ ────────────────────────────────────────────────────────── │
│ File: src/feature_engineering.py                           │
│ Function: create_features_for_game()                       │
│                                                             │
│ Creates 44+ statistics:                                     │
│   • Team's win/loss record                                  │
│   • Points scored in last 5 games                           │
│   • Home field advantage                                    │
│   • Head-to-head history                                    │
│   • Rest days between games                                 │
│   • Season trends                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Get Predictions from Each Model                    │
│ ────────────────────────────────────────────────────────── │
│ File: src/ml_models.py                                     │
│ Function: predict_all()                                     │
│                                                             │
│ Each model votes:                                           │
│   • LightGBM: CHI wins (65%)                               │
│   • Neural Net: CHI wins (62%)                             │
│   • Logistic: WSH wins (51%)                               │
│   • Gradient Boost: CHI wins (68%)                         │
│   • Random Forest: CHI wins (60%)                          │
│   • XGBoost: CHI wins (66%)                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Combine into Ensemble Prediction                   │
│ ────────────────────────────────────────────────────────── │
│ File: src/agent.py                                         │
│ Function: _ensemble_predict()                              │
│                                                             │
│ Majority vote + average confidence:                         │
│   5 out of 6 models say CHI → CHI wins                     │
│   Average confidence: 63.7%                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Save Prediction to Database                        │
│ ────────────────────────────────────────────────────────── │
│ File: src/database.py                                      │
│ Function: insert_prediction()                              │
│                                                             │
│ Stored in predictions table:                                │
│   game_id: "401671797"                                      │
│   predicted_winner: "CHI"                                   │
│   win_probability: 0.637                                    │
│   model_name: "ensemble"                                    │
└─────────────────────────────────────────────────────────────┘
```

### Workflow 3: Viewing Dashboard (User Action)
```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Start API Server                                    │
│ ────────────────────────────────────────────────────────── │
│ Command: python -m uvicorn src.api_server:app --reload     │
│ What it does: Starts FastAPI on http://localhost:8000      │
│                                                             │
│ Available endpoints:                                         │
│   GET /health                  → Check if alive             │
│   GET /predictions/current     → Get this week              │
│   GET /predictions/past        → Get last week              │
│   POST /predictions/refresh    → Update results             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Start Frontend                                      │
│ ────────────────────────────────────────────────────────── │
│ Command: cd frontend && npm run dev                         │
│ What it does: Starts React on http://localhost:5175        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: User Opens Browser                                  │
│ ────────────────────────────────────────────────────────── │
│ Browser → http://localhost:5175                             │
│                                                             │
│ React App (App.jsx) runs useEffect():                       │
│   1. Calls API: GET /predictions/current                    │
│   2. Calls API: GET /predictions/past                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: API Fetches from Database                          │
│ ────────────────────────────────────────────────────────── │
│ File: src/api_server.py                                    │
│ Function: get_current_predictions()                         │
│                                                             │
│ API calls database.py:                                      │
│   db.get_current_predictions(season=2025, week=6)          │
│                                                             │
│ Database returns JSON:                                      │
│   {                                                         │
│     "predictions": [15 games with predictions],             │
│     "season": 2025,                                         │
│     "week": 6                                               │
│   }                                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: React Displays Data                                │
│ ────────────────────────────────────────────────────────── │
│ File: frontend/src/App.jsx                                 │
│ Component: GameCard                                         │
│                                                             │
│ For each prediction:                                        │
│   • Shows teams with green glow (winner)                    │
│   • Shows red glow (loser)                                  │
│   • Displays confidence percentage                          │
│   • Links to ESPN game page                                 │
└─────────────────────────────────────────────────────────────┘
```

### Workflow 4: Auto-Updating Results (Background)
```
┌─────────────────────────────────────────────────────────────┐
│ Trigger 1: Server Startup                                   │
│ ────────────────────────────────────────────────────────── │
│ When API starts → @app.on_event("startup")                 │
│ Automatically checks for completed games                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Trigger 2: User Views "Last Week Results" Tab              │
│ ────────────────────────────────────────────────────────── │
│ API endpoint /predictions/past → BackgroundTasks           │
│ Runs update_completed_games() in background                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Trigger 3: Manual Update                                    │
│ ────────────────────────────────────────────────────────── │
│ Command: python scripts/update_results.py                   │
│ Or: curl -X POST http://localhost:8000/predictions/refresh │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Update Process                                              │
│ ────────────────────────────────────────────────────────── │
│ 1. Get games without results from database                  │
│ 2. For each game, fetch fresh data from ESPN                │
│ 3. If game is complete, update winner & scores              │
│ 4. Mark prediction as correct/incorrect                     │
│ 5. Save to database                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           DATA SOURCES                              │
│                                                                     │
│    ┌──────────────┐                    ┌──────────────┐            │
│    │  ESPN API    │                    │  User Input  │            │
│    │  (Real NFL   │                    │  (Season/    │            │
│    │   Games)     │                    │   Week)      │            │
│    └──────┬───────┘                    └──────┬───────┘            │
└───────────┼────────────────────────────────────┼───────────────────┘
            │                                    │
            ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA COLLECTION LAYER                        │
│                                                                     │
│    ┌────────────────────────────────────────────────────┐          │
│    │  src/data_collector.py                             │          │
│    │  • get_games_for_week()                            │          │
│    │  • Fetches game schedule, scores, dates            │          │
│    │  • Formats data for database                       │          │
│    └─────────────────────┬──────────────────────────────┘          │
└──────────────────────────┼─────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER (SQLite)                      │
│                                                                     │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│    │   games      │  │ predictions  │  │  team_stats  │           │
│    │──────────────│  │──────────────│  │──────────────│           │
│    │ game_id      │  │ prediction_id│  │ team         │           │
│    │ season       │  │ game_id      │  │ season       │           │
│    │ week         │  │ model_name   │  │ wins         │           │
│    │ home_team    │  │ predicted_   │  │ losses       │           │
│    │ away_team    │  │   winner     │  │ points_for   │           │
│    │ winner       │  │ win_prob     │  │ points_against│          │
│    │ home_score   │  │ confidence   │  │ ...          │           │
│    │ away_score   │  │ correct_pred │  │              │           │
│    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
└───────────┼─────────────────┼─────────────────┼───────────────────┘
            │                 │                 │
            └────────┬────────┴────────┬────────┘
                     │                 │
                     ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FEATURE ENGINEERING LAYER                        │
│                                                                     │
│    ┌────────────────────────────────────────────────────┐          │
│    │  src/feature_engineering.py                        │          │
│    │  • create_features_for_game()                      │          │
│    │                                                     │          │
│    │  Raw Data → 44+ Smart Features:                    │          │
│    │    ✓ win_rate_home                                 │          │
│    │    ✓ avg_points_scored_last_5                      │          │
│    │    ✓ home_field_advantage                          │          │
│    │    ✓ head_to_head_history                          │          │
│    │    ✓ rest_days                                     │          │
│    │    ✓ season_momentum                               │          │
│    │    ... (44 total)                                  │          │
│    └─────────────────────┬──────────────────────────────┘          │
└──────────────────────────┼─────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    MACHINE LEARNING LAYER                           │
│                                                                     │
│    ┌────────────────────────────────────────────────────┐          │
│    │  src/ml_models.py                                  │          │
│    │                                                     │          │
│    │  ┌─────────────────┐  ┌─────────────────┐         │          │
│    │  │ RandomForest    │  │  XGBoost        │         │          │
│    │  │ Vote: CHI 60%   │  │  Vote: CHI 66%  │         │          │
│    │  └─────────────────┘  └─────────────────┘         │          │
│    │                                                     │          │
│    │  ┌─────────────────┐  ┌─────────────────┐         │          │
│    │  │ LightGBM        │  │  Logistic Reg   │         │          │
│    │  │ Vote: CHI 65%   │  │  Vote: WSH 51%  │         │          │
│    │  └─────────────────┘  └─────────────────┘         │          │
│    │                                                     │          │
│    │  ┌─────────────────┐  ┌─────────────────┐         │          │
│    │  │ Gradient Boost  │  │  Neural Network │         │          │
│    │  │ Vote: CHI 68%   │  │  Vote: CHI 62%  │         │          │
│    │  └─────────────────┘  └─────────────────┘         │          │
│    └─────────────────────┬──────────────────────────────┘          │
└──────────────────────────┼─────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PREDICTION ORCHESTRATION                         │
│                                                                     │
│    ┌────────────────────────────────────────────────────┐          │
│    │  src/agent.py                                      │          │
│    │  • predict_week()                                  │          │
│    │  • _ensemble_predict()                             │          │
│    │                                                     │          │
│    │  Combines 6 model votes:                           │          │
│    │    5/6 say CHI → Final: CHI wins (63.7%)           │          │
│    └─────────────────────┬──────────────────────────────┘          │
└──────────────────────────┼─────────────────────────────────────────┘
                           │
                           ▼ (saves to database)
┌─────────────────────────────────────────────────────────────────────┐
│                          API LAYER (FastAPI)                        │
│                                                                     │
│    ┌────────────────────────────────────────────────────┐          │
│    │  src/api_server.py                                 │          │
│    │                                                     │          │
│    │  GET /predictions/current?season=2025&week=6       │          │
│    │      ↓                                              │          │
│    │      db.get_current_predictions()                  │          │
│    │      ↓                                              │          │
│    │      JSON response with predictions                │          │
│    └─────────────────────┬──────────────────────────────┘          │
└──────────────────────────┼─────────────────────────────────────────┘
                           │
                           ▼ (HTTP request)
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER (React)                       │
│                                                                     │
│    ┌────────────────────────────────────────────────────┐          │
│    │  frontend/src/App.jsx                              │          │
│    │                                                     │          │
│    │  useEffect() → fetch API → display:                │          │
│    │                                                     │          │
│    │  ┌──────────────────────────────────┐              │          │
│    │  │  GameCard Component              │              │          │
│    │  │  ┌────────────┐  ┌────────────┐  │              │          │
│    │  │  │ CHI (Home) │  │ WSH (Away) │  │              │          │
│    │  │  │ ✓ Green    │  │ ✗ Red      │  │              │          │
│    │  │  │   Glow     │  │   Glow     │  │              │          │
│    │  │  └────────────┘  └────────────┘  │              │          │
│    │  │  Prediction: CHI (63.7%)         │              │          │
│    │  └──────────────────────────────────┘              │          │
│    └─────────────────────┬──────────────────────────────┘          │
└──────────────────────────┼─────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          USER'S BROWSER                             │
│                    http://localhost:5175                            │
│                                                                     │
│    Shows beautiful dashboard with:                                 │
│      • Week slider (select any week)                               │
│      • Green glowing winners                                       │
│      • Red glowing losers                                          │
│      • Confidence percentages                                      │
│      • ESPN links                                                  │
│      • Disclaimer at bottom                                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure & Responsibilities

### Python Backend Files
```
MLSportsBetting/
│
├── src/
│   ├── data_collector.py
│   │   └─ Role: ESPN API Client
│   │      • Fetches game schedules
│   │      • Gets scores and dates
│   │      • Formats data
│   │
│   ├── database.py
│   │   └─ Role: Database Manager
│   │      • Creates tables
│   │      • Saves/retrieves games
│   │      • Saves/retrieves predictions
│   │      • Queries for dashboard
│   │
│   ├── feature_engineering.py
│   │   └─ Role: Feature Creator
│   │      • Calculates team stats
│   │      • Creates 44+ features
│   │      • Prepares data for ML
│   │
│   ├── ml_models.py
│   │   └─ Role: Model Manager
│   │      • Trains 6 ML models
│   │      • Makes predictions
│   │      • Saves/loads models
│   │
│   ├── agent.py
│   │   └─ Role: Orchestrator
│   │      • Coordinates all components
│   │      • Runs training workflow
│   │      • Runs prediction workflow
│   │      • Combines model votes
│   │
│   └── api_server.py
│       └─ Role: Web API
│          • Exposes endpoints
│          • Handles HTTP requests
│          • Returns JSON data
│
├── scripts/
│   ├── collect_data.py    → Fetch historical data
│   ├── train.py           → Train ML models
│   ├── predict.py         → Generate predictions
│   └── update_results.py  → Update game results
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx        → React dashboard UI
│   │   └── App.css        → Styling
│   └── package.json       → Dependencies
│
├── data/
│   └── nfl_games.db       → SQLite database
│
└── models/
    └── *.pkl              → Trained ML models
```

---

## 🔧 Recommended Visualization Tools

### For Code Organization:
1. **VS Code Extensions**:
   - **Code Tour**: Creates guided tours through your codebase
   - **Draw.io Integration**: Create diagrams in VS Code
   - **Bookmarks**: Mark important code sections

2. **Diagramming Tools**:
   - **[Excalidraw](https://excalidraw.com/)**: Free, simple drawing tool (hand-drawn style)
   - **[Draw.io](https://app.diagrams.net/)**: Free professional diagrams
   - **[Mermaid](https://mermaid.js.org/)**: Code-based diagrams (works in GitHub README)
   - **[Lucidchart](https://www.lucidchart.com/)**: Professional flowcharts

3. **Architecture Visualization**:
   - **[PlantUML](https://plantuml.com/)**: Text-to-diagram tool
   - **[C4 Model](https://c4model.com/)**: Software architecture diagrams

### For Understanding Data Flow:
1. **Postman**: Test your API endpoints visually
2. **DB Browser for SQLite**: View your database visually
3. **React DevTools**: Inspect React component tree

---

## 🎓 Quick Reference Card

### Starting the Application:
```bash
# Terminal 1: Start API
python -m uvicorn src.api_server:app --reload

# Terminal 2: Start Frontend
cd frontend
npm run dev

# Open browser: http://localhost:5175
```

### Making New Predictions:
```bash
# Option 1: Use the slider in dashboard (auto-generates)
# Just select season/week and it auto-fetches

# Option 2: Manual script
python populate_week5.py   # or populate_current_week.py
```

### Updating Results After Games:
```bash
# Option 1: Automatic (happens when viewing dashboard)
# Option 2: Manual
python scripts/update_results.py
```

### Key Endpoints:
- `http://localhost:8000/predictions/current?season=2025&week=6` - Get predictions
- `http://localhost:8000/predictions/past` - Get results
- `http://localhost:8000/health` - Check if API is alive

---

## 🧠 Mental Model

Think of it as a **3-Layer Cake**:

```
┌─────────────────────────────────────┐
│     LAYER 3: Presentation           │  ← What user sees
│     (React Dashboard)                │     (Pretty UI)
├─────────────────────────────────────┤
│     LAYER 2: Business Logic         │  ← The "brain"
│     (Python ML + API)                │     (Smart stuff)
├─────────────────────────────────────┤
│     LAYER 1: Data Storage           │  ← Memory
│     (SQLite Database)                │     (Facts storage)
└─────────────────────────────────────┘
```

**Data flows**: Layer 1 → Layer 2 → Layer 3 → User's eyes 👀

---

## 📝 Summary in Plain English

1. **Collect** real NFL game data from ESPN
2. **Store** it in a database
3. **Calculate** smart statistics from the data
4. **Train** 6 robot "experts" to predict winners
5. **Combine** their opinions into one prediction
6. **Show** predictions on a nice website
7. **Update** results when games finish
8. **Learn** from mistakes to get better

It's like having 6 sports analysts that learned from watching hundreds of games, now they vote on who will win each week! 🏈🤖


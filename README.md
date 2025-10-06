# NFL Game Prediction ML Agent

This project implements a machine-learning driven agent that collects NFL data, trains an ensemble of models, and surfaces weekly win predictions. It now ships with a modern React dashboard for exploring upcoming picks and reviewing past results.

## Key Features

- **Automated Data Collection**: Fetches NFL schedules, results, and team statistics with smart caching to avoid duplicate API calls.
- **SQLite Persistence**: Stores every game, prediction, and model evaluation for quick recall and analysis.
- **Feature Engineering Pipeline**: Builds 40+ engineered features including ELO trends, momentum metrics, weather, and betting lines.
- **Model Ensemble**: Random Forest, XGBoost, LightGBM, Logistic Regression, Gradient Boosting, and a Neural Network blended together.
- **Performance Tracking**: Logs model accuracy over time and marks each historical prediction as a hit or miss.
- **React Dashboard**: Stylish two-tab dashboard that highlights the current week's predictions and grades last week's outcomes with clear visual feedback and ESPN deep links.

## Project Structure

```
MLSportsBetting/
├── data/                     # SQLite database, trained models, intermediate artifacts
├── frontend/                 # React + Vite user interface
│   ├── package.json
│   └── src/
├── scripts/                  # Helper scripts (collect, train, predict, etc.)
├── src/                      # Python source code
│   ├── agent.py
│   ├── api_server.py         # FastAPI service powering the dashboard
│   ├── database.py
│   ├── data_collector.py
│   ├── feature_engineering.py
│   └── ml_models.py
├── requirements.txt
└── README.md
```

## Quick Start (CLI Agent)

1. **Install Python Dependencies**

   ```powershell
   pip install -r requirements.txt
   ```

2. **Initialize the Database (creates tables if missing)**

   ```powershell
   python scripts/init_database.py
   ```

3. **Collect Historical Data**

   ```powershell
   python scripts/collect_data.py --start-year 2018 --end-year 2024
   ```

4. **Train the Ensemble Models**

   ```powershell
   python scripts/train_models.py
   ```

5. **Generate Predictions from the CLI**

   ```powershell
   python scripts/predict.py --current
   ```

## Web Dashboard

The dashboard calls the FastAPI service and presents a card-based view of the predictions.

### 1. Start the API

```powershell
uvicorn src.api_server:app --host 0.0.0.0 --port 8000 --reload
```

The service exposes:

- `GET /health` – quick heartbeat check.
- `GET /predictions/current` – ensemble picks for the upcoming week.
- `GET /predictions/past` – most recent completed week along with outcome grading.

### 2. Start the React UI

```powershell
cd frontend
npm install
npm run dev
```

By default the UI runs at [http://localhost:5173](http://localhost:5173) and calls the API at [http://localhost:8000](http://localhost:8000). Set `VITE_API_BASE_URL` in a `.env` file if you deploy the API somewhere else.

## Prediction Workflow

1. **Auto-populate on startup**: When you open the dashboard, the API automatically fetches the current week's schedule and generates predictions if none exist.

2. **Update completed games**: Run this script after games finish to update results:
   ```powershell
   python scripts/update_results.py
   ```
   This updates the database with final scores and marks predictions as correct/incorrect.

3. **View results**: The "Last Week Results" tab automatically shows completed games with green (correct) or red (incorrect) highlighting.

4. **Background updates**: The API checks for new results every time the "Last Week Results" tab is opened.

5. **Manual refresh**: Call the refresh endpoint to force an update:
   ```powershell
   curl -X POST http://localhost:8000/predictions/refresh
   ```

### Automated Updates (Optional)

Set up a daily task to automatically update results:

**Windows Task Scheduler:**
```powershell
# Run daily at 2 AM
schtasks /create /tn "NFL Results Update" /tr "python C:\path\to\MLSportsBetting\scripts\update_results.py" /sc daily /st 02:00
```

**Linux/Mac Cron:**
```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/MLSportsBetting && python scripts/update_results.py
```

## Disclaimer

This project is designed for research and educational exploration. **Not** intended for real-money wagering. Always gamble responsibly.

# 🏗️ NFL Prediction Bot - Visual Architecture

This document contains visual diagrams using Mermaid (view in GitHub or Markdown preview).

## System Architecture Diagram

```mermaid
graph TB
    subgraph External["🌐 External Data Sources"]
        ESPN[ESPN API<br/>Real NFL Games]
        User[👤 User Input<br/>Season/Week Selection]
    end

    subgraph Backend["🐍 Python Backend"]
        DC[Data Collector<br/>src/data_collector.py]
        FE[Feature Engineer<br/>src/feature_engineering.py]
        ML[ML Models Manager<br/>src/ml_models.py]
        Agent[Prediction Agent<br/>src/agent.py]
        API[FastAPI Server<br/>src/api_server.py]
        
        DC -->|Raw Games| DB
        DB -->|Historical Data| FE
        FE -->|44+ Features| ML
        ML -->|6 Model Votes| Agent
        Agent -->|Ensemble Prediction| DB
        DB -->|Query Results| API
    end

    subgraph Storage["💾 Data Storage"]
        DB[(SQLite Database<br/>games, predictions,<br/>team_stats)]
    end

    subgraph Frontend["⚛️ React Frontend"]
        React[App.jsx<br/>Dashboard UI]
        Cards[GameCard Components<br/>Green/Red Glows]
        Slider[Week Selector<br/>Season + Week]
    end

    ESPN -->|Fetch Games| DC
    User -->|Select Week| Slider
    Slider -->|HTTP Request| API
    API -->|JSON Response| React
    React -->|Render| Cards

    style ESPN fill:#f96,stroke:#333,stroke-width:2px
    style DB fill:#85C1E9,stroke:#333,stroke-width:2px
    style ML fill:#82E0AA,stroke:#333,stroke-width:2px
    style React fill:#FAD7A0,stroke:#333,stroke-width:2px
```

## Data Flow: Making a Prediction

```mermaid
sequenceDiagram
    participant E as ESPN API
    participant DC as Data Collector
    participant DB as Database
    participant FE as Feature Engineer
    participant ML as ML Models (6x)
    participant A as Agent
    participant API as FastAPI
    participant R as React UI
    participant U as User

    U->>R: Opens Dashboard
    R->>API: GET /predictions/current?week=6
    API->>DB: Query: Get predictions for week 6
    
    alt No predictions exist
        DB-->>API: Empty result
        API->>E: Fetch week 6 games
        E-->>DC: Game schedule data
        DC->>DB: Insert games
        
        DB->>FE: Get historical data
        FE->>FE: Calculate 44+ features
        FE->>ML: Feed features
        
        ML->>ML: RandomForest predicts
        ML->>ML: XGBoost predicts
        ML->>ML: LightGBM predicts
        ML->>ML: Logistic predicts
        ML->>ML: GradientBoost predicts
        ML->>ML: NeuralNet predicts
        
        ML->>A: Return 6 predictions
        A->>A: Ensemble vote (majority)
        A->>DB: Save ensemble prediction
        DB->>API: Return predictions
    else Predictions exist
        DB-->>API: Return cached predictions
    end
    
    API-->>R: JSON: 15 games with predictions
    R->>R: Render GameCards
    R->>U: Display dashboard with glows
```

## Component Relationships

```mermaid
graph LR
    subgraph Scripts["📜 Scripts (One-time Setup)"]
        S1[collect_data.py]
        S2[train.py]
        S3[predict.py]
        S4[update_results.py]
    end

    subgraph Core["🧠 Core Components"]
        DB[(Database)]
        DC[Data Collector]
        FE[Feature Engineer]
        ML[ML Models]
        AG[Agent]
    end

    subgraph API["🌐 API Layer"]
        FastAPI[FastAPI Server]
    end

    subgraph UI["🎨 User Interface"]
        React[React App]
        Cards[Game Cards]
        Slider[Week Slider]
    end

    S1 -->|Uses| DC
    S2 -->|Uses| ML
    S3 -->|Uses| AG
    S4 -->|Uses| DC
    
    DC <-->|R/W| DB
    FE <-->|R| DB
    ML <-->|R/W| DB
    AG -->|Orchestrates| DC
    AG -->|Orchestrates| FE
    AG -->|Orchestrates| ML
    
    FastAPI <-->|Query| DB
    React <-->|HTTP| FastAPI
    React -->|Renders| Cards
    React -->|Contains| Slider

    style DB fill:#85C1E9,stroke:#333,stroke-width:3px
    style AG fill:#82E0AA,stroke:#333,stroke-width:3px
    style React fill:#FAD7A0,stroke:#333,stroke-width:3px
```

## ML Ensemble Process

```mermaid
flowchart TD
    Start([Game: CHI @ WSH]) --> Features[Create Features<br/>44+ statistics]
    
    Features --> M1[RandomForest<br/>CHI: 60%]
    Features --> M2[XGBoost<br/>CHI: 66%]
    Features --> M3[LightGBM<br/>CHI: 65%]
    Features --> M4[Logistic Reg<br/>WSH: 51%]
    Features --> M5[Gradient Boost<br/>CHI: 68%]
    Features --> M6[Neural Network<br/>CHI: 62%]
    
    M1 --> Vote{Ensemble Vote}
    M2 --> Vote
    M3 --> Vote
    M4 --> Vote
    M5 --> Vote
    M6 --> Vote
    
    Vote -->|5 of 6 say CHI| Winner[Predicted Winner: CHI]
    Vote -->|Average confidence| Conf[Win Probability: 63.7%]
    
    Winner --> Save[(Save to Database)]
    Conf --> Save
    
    Save --> Display[Display in Dashboard<br/>CHI with Green Glow]

    style Start fill:#f96,stroke:#333,stroke-width:2px
    style Vote fill:#FAD7A0,stroke:#333,stroke-width:3px
    style Display fill:#82E0AA,stroke:#333,stroke-width:2px
```

## Database Schema

```mermaid
erDiagram
    GAMES ||--o{ PREDICTIONS : has
    GAMES {
        string game_id PK
        int season
        int week
        string home_team
        string away_team
        datetime game_date
        int home_score
        int away_score
        string winner
        float home_spread
        string espn_url
    }
    
    PREDICTIONS {
        int prediction_id PK
        string game_id FK
        string model_name
        string predicted_winner
        float win_probability
        float confidence_score
        string actual_winner
        boolean correct_prediction
        datetime prediction_date
    }
    
    TEAM_STATS {
        string team PK
        int season PK
        int wins
        int losses
        float points_for
        float points_against
        float win_rate
    }
    
    MODEL_PERFORMANCE {
        int performance_id PK
        string model_name
        int season
        float accuracy
        int total_predictions
        datetime evaluation_date
    }
```

## User Journey Flow

```mermaid
journey
    title User Experience Flow
    section Setup (One Time)
      Install dependencies: 3: Developer
      Collect historical data: 4: Developer
      Train ML models: 5: Developer
    section Weekly Usage
      Start API server: 5: Developer
      Start React frontend: 5: Developer
      Open dashboard: 5: User
      Select week with slider: 5: User
      View predictions: 5: User
      See green glow on winner: 5: User
      See red glow on loser: 5: User
      Click ESPN link: 4: User
    section After Games
      Games complete: 3: Automatic
      Results auto-update: 5: Automatic
      View accuracy: 5: User
      Check last week tab: 5: User
```

## State Machine: Prediction Lifecycle

```mermaid
stateDiagram-v2
    [*] --> NoGames: System initialized
    NoGames --> GamesScheduled: ESPN data collected
    GamesScheduled --> PredictionsMade: ML models run
    PredictionsMade --> AwaitingResults: Games not played yet
    AwaitingResults --> ResultsAvailable: Games completed
    ResultsAvailable --> Evaluated: Accuracy calculated
    Evaluated --> Displayed: Shows on dashboard
    Displayed --> [*]
    
    AwaitingResults --> AwaitingResults: Games in progress
    ResultsAvailable --> ResultsAvailable: Checking for updates
    
    note right of PredictionsMade
        6 models vote
        Ensemble decides
        Saved to DB
    end note
    
    note right of Evaluated
        Prediction marked
        correct/incorrect
    end note
```

## Request Flow Diagram

```mermaid
flowchart LR
    subgraph Browser
        B[User's Browser<br/>localhost:5175]
    end
    
    subgraph Vite["Vite Dev Server"]
        V[React App<br/>App.jsx]
    end
    
    subgraph API["FastAPI Server<br/>localhost:8000"]
        E1["/predictions/current"]
        E2["/predictions/past"]
        E3["/predictions/refresh"]
    end
    
    subgraph DB["SQLite Database"]
        T1[(games)]
        T2[(predictions)]
    end
    
    B -->|HTTP GET| V
    V -->|Renders| B
    V -->|axios.get| E1
    V -->|axios.get| E2
    E1 -->|SELECT| T1
    E1 -->|SELECT| T2
    E2 -->|SELECT| T1
    E2 -->|SELECT| T2
    E3 -->|UPDATE| T1
    E3 -->|UPDATE| T2
    T2 -->|JSON| E1
    T2 -->|JSON| E2
    E1 -->|JSON| V
    E2 -->|JSON| V

    style B fill:#FAD7A0,stroke:#333,stroke-width:2px
    style E1 fill:#82E0AA,stroke:#333,stroke-width:2px
    style T1 fill:#85C1E9,stroke:#333,stroke-width:2px
```

## Technology Stack

```mermaid
mindmap
  root((NFL Prediction Bot))
    Backend
      Python 3.13
        FastAPI - Web API
        scikit-learn - ML Models
        pandas - Data Processing
        sqlite3 - Database
        requests - HTTP Client
      Machine Learning
        RandomForest
        XGBoost
        LightGBM
        Logistic Regression
        Gradient Boosting
        Neural Network
    Frontend
      JavaScript
        React 18 - UI Framework
        Vite - Build Tool
        Axios - HTTP Client
        CSS3 - Styling
    Data
      SQLite - Database
        games table
        predictions table
        team_stats table
      ESPN API
        Game schedules
        Scores
        Team data
    DevOps
      Git - Version Control
      npm - Package Manager
      pip - Python Packages
      uvicorn - ASGI Server
```

---

## How to View These Diagrams

1. **In VS Code**: Install "Markdown Preview Mermaid Support" extension
2. **On GitHub**: Push this file and view it there (Mermaid renders automatically)
3. **Online**: Copy diagrams to [Mermaid Live Editor](https://mermaid.live/)
4. **Export**: Use Mermaid CLI to export as PNG/SVG

## Additional Visualization Tools You Can Use

### For Real-Time Monitoring:
- **Postman**: Test your API endpoints
- **SQLite Browser**: View database contents
- **React DevTools**: Inspect component tree
- **Network Tab**: See HTTP requests in browser

### For Documentation:
- **Excalidraw**: Hand-drawn style diagrams
- **Draw.io**: Professional flowcharts
- **PlantUML**: Code-based UML diagrams
- **Lucidchart**: Collaborative diagramming

### For Understanding Code:
- **VS Code Bookmarks**: Mark important lines
- **CodeTour**: Create guided tours
- **Git Graph**: Visualize commit history

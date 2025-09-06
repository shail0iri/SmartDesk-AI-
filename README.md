SmartDesk AI: Intelligent Ticket Classification System

An End-to-End AI + Data pipeline for automated customer support ticket analysis, sentiment classification, and business intelligence reporting. It simulates real-world ML engineering skills beyond just training models. This project demonstrates full-stack data science skills with local LLM integration.

🎯 Business Problem - 
Manual customer support ticket analysis is:

Time-consuming: Hours spent reading and categorizing tickets

Inconsistent: Human analysts may categorize tickets differently

Scalability issues: Difficult to handle large volumes of tickets

Delayed insights: Slow response to emerging issues

Technical Solution -

Built an automated AI pipeline that:

Generates realistic synthetic data using local LLMs

Automatically classifies tickets by sentiment, urgency, and category

Provides actionable insights through visualizations and reports

Runs entirely locally with no cloud costs


🌟 Featured Highlights

🚀 Local AI Processing: Uses DeepSeek R1 8B via Ollama - no API costs!

📊 Automated Analysis: Classifies sentiment, urgency, and categories automatically

💡 Business Insights: Generates actionable reports and visualizations

🔒 Data Privacy: Everything runs locally - no data leaves your machine

⚡ Production Ready: Dockerized deployment and REST API endpoints


graph TD
    A[📝 Data Generation] --> B[🤖 LLM Analysis]
    B --> C[🔄 Data Processing]
    C --> D[📈 Visualization]
    D --> E[💡 Business Insights]
    E --> F[🎯 Decision Support]
    
    subgraph "Technical Stack"
        B --> O[Ollama]
        O --> DS[DeepSeek R1 8B]
        C --> P[Pandas]
        D --> M[Matplotlib]
        D --> S[Seaborn]
        F --> FA[FastAPI]
    end
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#bbdefb

The project covers the full ML lifecycle:
✔️ Data generation & preprocessing
✔️ Exploratory data analysis (EDA) & visualization
✔️ Model training & benchmarking with multiple classifiers
✔️ Saving best models for each task
✔️ Deployment via FastAPI + Docker
✔️ Hosting on Render (Free Tier) for live demo

🛠️ Tech Stack

Python (Data + ML)

Scikit-learn, XGBoost, CatBoost (Modeling)

Pandas, Matplotlib, Seaborn (EDA & Visualization)

FastAPI (Deployment API)

Docker (Containerization)

Render (Cloud Hosting)

✨ Key Highlights for Recruiters

✅ Complete end-to-end ML lifecycle (data → deployment)

✅ Multiple models benchmarked, best selected for each task

✅ Misclassification analysis for error insights

✅ Production-ready API with Docker & FastAPI

✅ Deployed live on Render for instant demo

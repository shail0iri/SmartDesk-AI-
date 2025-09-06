# 📊 Model Evaluation Report

This report summarizes the benchmarking results for the Sentiment, Urgency, and Category classification tasks.

## 🏆 Best Models Per Task

- **Sentiment** → CatBoost (Accuracy=0.84, F1=0.83)
- **Urgency** → XGBoost (Accuracy=0.63, F1=0.62)
- **Category** → CatBoost (Accuracy=0.81, F1=0.80)

## 📋 Full Benchmark Results

| Task      | Model        |   Accuracy |     F1 |
|:----------|:-------------|-----------:|-------:|
| Sentiment | LogReg       |     0.8009 | 0.795  |
| Sentiment | NaiveBayes   |     0.6239 | 0.5039 |
| Sentiment | RandomForest |     0.7832 | 0.7387 |
| Sentiment | LinearSVC    |     0.792  | 0.7811 |
| Sentiment | XGBoost      |     0.8319 | 0.8261 |
| Sentiment | CatBoost     |     0.8363 | 0.827  |
| Urgency   | LogReg       |     0.5885 | 0.5872 |
| Urgency   | NaiveBayes   |     0.4823 | 0.3235 |
| Urgency   | RandomForest |     0.5841 | 0.5563 |
| Urgency   | LinearSVC    |     0.615  | 0.6151 |
| Urgency   | XGBoost      |     0.6283 | 0.6208 |
| Urgency   | CatBoost     |     0.6106 | 0.6019 |
| Category  | LogReg       |     0.7699 | 0.767  |
| Category  | NaiveBayes   |     0.3274 | 0.2256 |
| Category  | RandomForest |     0.7832 | 0.761  |
| Category  | LinearSVC    |     0.7699 | 0.758  |
| Category  | XGBoost      |     0.8053 | 0.7897 |
| Category  | CatBoost     |     0.8142 | 0.7987 |

## 🔎 Confusion Matrices & Reports
Confusion matrices (`.png`) and detailed classification reports (`.txt`) for each model are saved in the `figures/` directory.

## 📈 F1 Score Comparison Chart
![F1 Score Comparison](figures/benchmark_f1_scores.png)

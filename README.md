# 🧤 Digital Twin: Handball Goalkeeper Performance Analysis

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://handball-digital-twin.streamlit.app/)

> [!IMPORTANT]
> **Elite Portfolio Update**: This version has been upgraded to **professional grade**, including Machine Learning predictive models, bilingual support (PT/EN), and automated PDF reporting.

## 🌟 Overview

This project implements a **Digital Twin** strategy for the performance and biometric analysis of Handball Goalkeepers in real-time. By mapping physical data (heart rate, reaction time) and technical events (shot position, outcome) into a digital dashboard, it provides coaches and technical staff with a "Mission Control" for high-performance decision-making.

![Dashboard Preview](assets/dashboard_preview.png)

---

## 🚀 Key Features

The system is organized into four specialized analysis modules:

### 1. 🥅 Spatial Visualization (Zone 1)
- **Goal Heatmap**: Interactive heatmap showing the density of shots and goals across the 3m x 2m area.
- **3x3 Efficiency Grid**: Detailed save rates for nine goal sectors (Top/Middle/Base x Left/Center/Right).
- **Shooter Position Mapping**: Performance analysis based on the attacker's role (Wing, Pivot, Back, Center).

### 2. 🧠 Predictive Twin (ML Module)
- **Save Probability Heatmap**: Utilizes a **Random Forest Classifier** to predict save probabilities in real-time.
- **Dynamic Simulation**: Adjust variables like shot technique, speed, and goalkeeper heart rate to visualize the "Digital Twin's" predicted response.

### 3. 📈 Temporal Evolution (Zone 2)
- **Efficiency Heatmap Matrix**: Tracks technical success over a sequence of games to identify trends in fatigue or tactical adaptation.
- **Dynamic Filtering**: Isolate specific shot types or time ranges during the season.

### 4. 🎯 Technical Dynamics (Zone 3)
- **Efficiency Ranking**: Success rates across different shot types (e.g., 6m, 9m, Fast Break).
- **Reaction Speed Analysis**: Precise measurement of reaction times (ms) to optimize cognitive training.

### 5. 🧬 Biometrics & Human Performance (Zone 4)
- **Physiological Monitoring**: Heart rate (BPM) tracking synchronized with gameplay events.
- **Pearson Correlation ($R$)**: Automated statistical calculation of the correlation between fatigue (HR) and cognitive performance (Reaction Time).

### 6. 🌍 Bilingual & Reporting
- **PT/EN Toggle**: Full internationalization support for the entire dashboard.
- **PDF Summary Export**: Generates a professional performance report with one click.

---

## 🛠️ Tech Stack

- **Core**: Python 3.10+
- **Frontend/Dashboard**: Streamlit (for high-performance interactive web UI)
- **Data Engine**: Pandas (for complex time-series and event-based data processing)
- **Machine Learning**: Scikit-learn (Random Forest Classifier for save prediction)
- **Visualization**: Plotly Graph Objects & Express
- **Reporting**: FPDF2 (Dynamic PDF generation)
- **Image Processing**: Pillow & Kaleido

---

## 💡 What I Learned

This project was a deep dive into the intersection of **Data Science** and **Elite Sports Performance**:

1. **The Digital Twin Concept**: Translating biological signals into actionable tactical insights.
2. **Predictive Modeling**: Implementing and deploying an ML model into a real-time dashboard.
3. **Pearson Correlation in Sports**: Quantifying the mathematical relationship between physiological fatigue (BPM) and motor output (Reaction Time).
4. **Professional i18n**: Building a scalable localization system for international portability.

---

## 🔧 Future Improvements

To take this platform to a professional production level, several enhancements are planned:
- **Anomaly Detection**: Identifying abnormal heart rate spikes or reaction time drops.
- **Real-time Wearable APIs**: Integrating directly with sensors (like Polar or Garmin) for live data ingestion during matches.
- **Mobile-First UX**: Optimization for tablet/mobile use for sideline coaches.
- **Multi-Player Benchmarking**: Adding a module for comparative analysis between different goalkeepers in a squad.

---

## 🏁 How to Run

### Path 1: Local Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/antonio-mmc/handball-digital-twin.git
   cd handball-digital-twin
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Launch the Dashboard**:
   ```bash
   streamlit run app.py
   ```

---

## 📂 Project Structure

- `app.py`: Main Dashboard entry point (Streamlit).
- `charts.py`: Visualization engine (Plotly logic).
- `utils.py`: Data processing, filtering, and theme management.
- `style.css`: Custom professional styling (root).
- `data/`: Contains `dataset_guarda_redes_v2.csv` (core performance log).
- `assets/`: Image assets for spatial mapping (`baliza.png`, `positions.png`).
---

## 👤 Author

**António Correia**
[MEGSI - Universidade do Minho](https://www.uminho.pt)
*Information Visualization Project*

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
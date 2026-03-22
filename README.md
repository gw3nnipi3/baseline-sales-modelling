# Baseline Sales Modelling

**Estimating baseline (non-promoted) sales for fast-moving consumer goods (FMCGs) using time-series modelling**

---

## 1. Project Overview

This project develops a **data-driven demand model** to estimate **baseline (non-promoted) sales** for retail products.

It is designed to:

- Separate intrinsic demand from promotional uplift
- Quantify true impact of promotions
- Provide a business-ready, interpretable baseline for decision-making

### Motivations

Retail sales data is often:

- Noisy and highly volatile  
- Strongly influenced by promotions  
- Difficult to interpret without decomposition  

Accurate baseline estimation is critical for:

- Marketing ROI analysis  
- Demand forecasting  
- Strategic pricing decisions  

---

## 2. Key Features

- Baseline demand modelling using statistical and ML approaches  
- Promotion impact analysis  
- Modular backend for preprocessing and modelling  
- Interactive dashboard built with Streamlit  
- Clean separation between experimentation (notebooks) and production code  

---

## 3. System Architecture

The system follows a modular pipeline:

1. Raw data is ingested from `data/raw/`  
2. Data is cleaned and preprocessed  
3. Features are engineered (e.g. promotions, time-based signals)  
4. Models are trained to estimate baseline sales  
5. Predictions are generated  
6. Results are visualised in an interactive dashboard  

---


## 4. Repository Structure

```

baseline-sales-modelling/
│
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── .gitignore                   # Ignore venv, raw data, outputs
│
├── data/
│   ├── raw/                     # Original raw datasets
│   └── processed/               # Cleaned datasets ready for modeling
│
├── notebooks/                   # Jupyter notebooks for exploration/experiments
│
├── src/                         # Core backend code
│   ├── models/                  # Model implementation (Meta Prophet)
│
├── tests/                       # Unit testing
├── dashboard/                   # Frontend interactive dashboard (Streamlit)
│   ├── utils/                   # Utility files with functions to run the model
└── .venv/                       # Python virtual environment (NOT committed)

```

---

## 5. Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/gw3nnipi3/baseline-sales-modelling.git
cd baseline-sales-modelling
````

### 2️⃣ Create a virtual environment

* On Windows:

```powershell
python -m venv .venv           # create virtual environment
.venv\Scripts\Activate.ps1     # activate on Windows
```

* On Mac/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 6. How to Run

### 1️⃣ Launch Dashboard

```bash
streamlit run dashboard/app.py
```

* Interactive interface for uploading new data
* Preview baseline predictions
* Ready for future retraining functionality

---

## 7. Notebooks

* `notebooks/experiment.ipynb` → Initial Visualisation of data using SARIMAX
* `notebooks/danielTest.ipynb` → Experimentation with Prophet Model and XGBoost
* `notebooks/cannibalisationTest.ipynb` → Testing Cannibalisation between products

> **Note:** Notebooks are used for **experimentation and visualization**. They are separate from production code in `src/`.

---
## 8. Modelling Approach

The project explores baseline estimation using:

- Meta Prophet (baseline model)
- LightGBM (cannibalisation)

The objective is to:

- Capture underlying demand patterns
- Isolate promotional effects
- Maintain interpretability

---

## 9. Evaluation

Model performance is evaluated using:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Mean Absolute Percentage Error (MAPE)

These metrics assess how closely predictions match actual sales.

---

## 10. Alternative Deployment

This dashboard is also deployed using **Azure Virtual Machine**. It can be accessed [here](http://20.90.13.83:8501) 

## 11. License & Notes

* The dataset used in this project was provided for **academic purposes** only
* This project follows best practices for **reproducibility and modularity**
* Users may substitute their own datasets following the same format to reproduce results
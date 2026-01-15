# Baseline Sales Modelling

**Subtitle:** Estimating normal sales for Coca-Cola–style products

---

## 1. Project Overview

This project focuses on building a **data-driven demand model** to estimate **baseline (non-promoted) sales** for retail products.  
It is designed to:

- Separate normal sales from promotional effects
- Quantify incremental sales from promotions
- Provide a business-ready, interpretable baseline for decision-making

**Why this is interesting/challenging:**

- Retail data is often **sparse, noisy, and promotional-driven**
- Accurate baseline estimation is **critical for marketing ROI**
- Combining interpretable linear models with ML benchmarks (like XGBoost) allows **robust and explainable results**

---

## 2. Repository Structure

```

baseline-sales-modelling/
│
├── README.md                    # Project overview & instructions
├── requirements.txt             # Python dependencies
├── .gitignore                   # Ignore venv, raw data, outputs
│
├── data/
│   ├── raw/                     # Original raw CSVs (NOT committed)
│   └── processed/               # Cleaned datasets ready for modeling
│
├── notebooks/                   # Jupyter notebooks for exploration/experiments
│
├── src/                         # Reusable backend code
│   ├── data/                    # Data loading / preprocessing
│   ├── models/                  # Model code (linear regression, XGBoost)
│   └── evaluation/              # Metrics and plotting
│
├── train.py                     # Central script to preprocess, train, and save models
├── models/                      # Saved trained model files (.pkl)
├── dashboard/                   # Frontend interactive dashboard (Streamlit)
└── .venv/                       # Python virtual environment (NOT committed)

````

---

## 3. Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your-username>/baseline-sales-modelling.git
cd baseline-sales-modelling
````

### 2️⃣ Set up Python environment

```powershell
python -m venv .venv           # create virtual environment
.venv\Scripts\Activate.ps1     # activate on Windows
```

* On Mac/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. How to Run

### 1️⃣ Preprocess and Train

```bash
python src/train.py
```

* Preprocessing reads raw data from `data/raw/`
* Saves cleaned data to `data/processed/`
* Trains **baseline linear regression model**
* Saves model in `models/linear_baseline.pkl`

### 2️⃣ Launch Dashboard

```bash
streamlit run dashboard/app.py
```

* Interactive interface for uploading new data
* Preview baseline predictions
* Ready for future retraining functionality

---

## 5. Notebooks

* `notebooks/01_data_exploration.ipynb` → Visualize raw sales trends, promos, and seasonality
* `notebooks/02_model_comparison.ipynb` → Compare linear baseline with ML models like XGBoost

> **Note:** Notebooks are used for **experimentation and visualization**. They are separate from production code in `src/`.

---

## 6. Future Work / Extensions

* Add **feature engineering**: lagged sales, seasonal indicators, promo interactions
* Benchmark **XGBoost** against baseline
* Expand **dashboard** to allow model retraining and dynamic plots
* Explore **causal inference** for promo uplift analysis

---

## 7. License & Notes

* All data is **simulated / anonymized for coursework**
* No proprietary Coca-Cola data is included
* Project follows best practices for **reproducibility and modularity**


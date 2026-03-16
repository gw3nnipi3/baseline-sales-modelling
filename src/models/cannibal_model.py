import lightgbm as lgb
import pandas as pd
import streamlit as st


@st.cache_resource
def run_cannibal_model(processed_df: pd.DataFrame):
    features = [col for col in processed_df.columns]
    features.remove("residual")

    target = "residual"

    processed_df.index.name = "date"
    processed_df = processed_df.reset_index()
    split_date = processed_df["date"].max() - pd.Timedelta(weeks=16)

    train = processed_df[processed_df["date"] < split_date]
    test = processed_df[processed_df["date"] >= split_date]

    X_train, X_test = train[features], test[features]
    y_train, y_test = train[target], test[target]

    train_data = lgb.Dataset(X_train, label=y_train)
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

    params = {
        "objective": "regression",
        "metric": "rmse",
        "learning_rate": 0.01,
        "max_depth": 7,         # Keep shallow to prevent overfitting
        "num_leaves": 120,
        "min_data_in_leaf": 10,
        "feature_fraction": 0.8,  # Randomly select 80% of features per tree to find weak signals
        "verbose": -1
    }

    model = lgb.train(
        params,
        train_data,
        num_boost_round=3000,
        valid_sets=[train_data, test_data],
        callbacks=[lgb.early_stopping(stopping_rounds=50)]
    )

    return model

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


def train_sarima(series, order=(1,1,1), seasonal_order=(1,1,1,52)):
    """
    Train SARIMA model on a time series.

    Parameters:
        series (pd.Series): indexed time series
        order (tuple): ARIMA order
        seasonal_order (tuple): Seasonal order

    Returns:
        results: fitted SARIMA model
    """
    model = SARIMAX(
        series,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    results = model.fit(disp=False)
    return results


def forecast_sarima(results, steps=12):
    """
    Forecast future values from fitted SARIMA model.
    """
    forecast = results.get_forecast(steps=steps)
    return forecast.predicted_mean, forecast.conf_int()


def backtest_sarima(model_df, test_ratio=0.1):
    split_index = int(len(model_df) * (1 - test_ratio))
    train = model_df.iloc[:split_index]
    test = model_df.iloc[split_index:]

    model = SARIMAX(
        train["sales"],
        order=(1,1,1),
        seasonal_order=(1,1,1,52),
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    results = model.fit(disp=False)

    forecast = results.get_forecast(steps=len(test))
    forecast_mean = forecast.predicted_mean
    forecast_ci = forecast.conf_int()

    # Align forecast with test index
    forecast_mean.index = test.index
    forecast_ci.index = test.index

    return train, test, forecast_mean, forecast_ci
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose


def decompose_series(series: pd.Series, period: int = 52):
    """
    Decompose a time series into trend, seasonal, and residual components.

    Parameters
    ----------
    series : pd.Series
        Time series indexed by datetime
    period : int
        Seasonal period (52 for weekly yearly seasonality)

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        ['observed', 'trend', 'seasonal', 'resid']
    """

    decomposition = seasonal_decompose(
        series,
        model="additive",
        period=period
    )

    df = pd.DataFrame({
        "observed": series,
        "trend": decomposition.trend,
        "seasonal": decomposition.seasonal,
        "resid": decomposition.resid
    })

    return df
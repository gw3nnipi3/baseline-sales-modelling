import pandas as pd

def load_data(path: str) -> pd.DataFrame:
    """
    Load raw CSV data and parse the 'yearweek' column into proper dates.
    """
    df = pd.read_csv(path)

    # Convert yearweek to datetime (Monday of the week)
    df["date"] = pd.to_datetime(df["yearweek"].astype(str) + "-1", format="%G%V-%u")

    # Sort by date for time series
    df = df.sort_values("date").reset_index(drop=True)

    return df


def create_baseline_series(
    df: pd.DataFrame,
    sku_id: int = None,
    customer_id: str = None,
    exclude_promotions: bool = True,
    agg_method: str = "sum"
) -> pd.Series:
    """
    Create a weekly baseline sales series ready for SARIMA modeling.

    Parameters
    ----------
    df : pd.DataFrame
        Raw data loaded from load_data()
    sku_id : int, optional
        If given, filters to a specific product SKU.
    customer_id : str, optional
        If given, filters to a specific customer.
    exclude_promotions : bool
        If True, removes weeks with promotion from the baseline.
    agg_method : str
        Aggregation method when multiple rows per week exist. Options: 'sum', 'mean'.

    Returns
    -------
    pd.Series
        Weekly baseline sales, indexed by date (Monday of the week).
    """

    df_work = df.copy()

    # Optional filtering
    if sku_id is not None:
        df_work = df_work[df_work["product_sku_code"] == sku_id]
    if customer_id is not None:
        df_work = df_work[df_work["customer"] == customer_id]

    # Exclude promotion weeks if requested
    if exclude_promotions:
        df_work = df_work[df_work["promotion_indicator"] == 0]

    # Aggregate duplicates per week
    agg_dict = {
        "nielsen_total_volume": agg_method,
        "promotion_indicator": "max"  # max to preserve any promotion flags
    }
    df_agg = df_work.groupby("date").agg(agg_dict)

    # Fill missing weeks and interpolate sales
    df_agg = df_agg.asfreq("W-MON")
    df_agg["nielsen_total_volume"] = df_agg["nielsen_total_volume"].interpolate()

    # Return a clean series for modeling
    baseline_series = df_agg["nielsen_total_volume"].rename("sales")
    return baseline_series
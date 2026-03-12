# NOTE: Global variables
WIDGET_SETTING = [
    "WIDGET_INDEX",
    "WIDGET_TITLE",
    "DATA_SOURCE",
    "DISPLAY_TYPE",
    "FILTERS",
    "START_DATE",
    "END_DATE",
    "FORECAST_LENGTH",  # only for forecast e.g."1Y" = 1 yr "1W" = 1 wk "1M" = 1 month
    "PROMOTION_WINDOWS",  # only for forecast
]

WIDGET_DISPLAY_TYPE = ["KPI",
                       "Forecast",
                       "Decomposition",
                       "Predicted Vs. Observed",
                       "Backtest Performance"]

WIDGET_COLUMN_COUNT = 2

FILTER_LIST = [
    "product_sku_code",
    "customer",
    "top_brand",
    "flavor_internal",
    "pack_type_internal",
    "pack_size_internal",
    "units_per_package_internal",
]

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
    "PROMOTION_WINDOWS",  # only for forecast this is a set data type
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

FLAVOR_MAPPING = {
    # COLAS
    'COLA': 'Cola',
    'COLA & VANILLA': 'Cola',
    'COLA & CHERRY': 'Cola',
    'COLA & LIME': 'Cola',
    'COLA & LEMON': 'Cola',
    'COLA & OREO': 'Cola',
    'COLA & CINNAMON': 'Cola',

    # CITRUS
    'LEMON': 'Citrus',
    'ORANGE': 'Citrus',
    'LEMON & LIME': 'Citrus',
    'CITRUS': 'Citrus',
    'GRAPEFRUIT': 'Citrus',
    'GRAPEFRUIT & PINEAPPLE': 'Citrus',
    'TONIC & LEMON': 'Citrus',
    'TONIC & GRAPEFRUIT': 'Citrus',
    'LEMON & RASPBERRY': 'Citrus',

    # TROPICAL & ENERGY PUNCH
    'MANGO': 'Tropical_Exotic',
    'PARADISE': 'Tropical_Exotic',
    'PACIFIC PUNCH': 'Tropical_Exotic',
    'GUAVA': 'Tropical_Exotic',
    'PINEAPPLE': 'Tropical_Exotic',
    'PASSION FRUIT': 'Tropical_Exotic',
    'DRAGONFRUIT': 'Tropical_Exotic',
    'GUAVA & ORANGE & PASSION FRUIT': 'Tropical_Exotic',
    'KHAOTIC': 'Tropical_Exotic',
    'PIPELINE PUNCH': 'Tropical_Exotic',
    'RIPPER': 'Tropical_Exotic',
    'MIXXD': 'Tropical_Exotic',
    'RIO PUNCH': 'Tropical_Exotic',
    'KIWI': 'Tropical_Exotic',
    'KIWI & STRAWBERRY': 'Tropical_Exotic',
    'WATERMELON': 'Tropical_Exotic',
    'MELON': 'Tropical_Exotic',
    'MELON & WATERMELON': 'Tropical_Exotic',
    'WATERLEMON': 'Tropical_Exotic',

    # BERRIES & RED FRUITS
    'RASPBERRY': 'Berries_Red_Fruit',
    'BERRY': 'Berries_Red_Fruit',
    'STRAWBERRY': 'Berries_Red_Fruit',
    'CRANBERRY': 'Berries_Red_Fruit',
    'CHERRY': 'Berries_Red_Fruit',
    'APPLE': 'Berries_Red_Fruit',
    'APPLE & RASPBERRY': 'Berries_Red_Fruit',
    'APPLE & KIWI': 'Berries_Red_Fruit',
    'BERRY & FRUIT': 'Berries_Red_Fruit',
    'BERRY & CARROT & HIBISCUS': 'Berries_Red_Fruit',
    'ACAI & BLUEBERRY & POMEGRANATE': 'Berries_Red_Fruit',
    'BLUEBERRY & MOJITO': 'Berries_Red_Fruit',


    # TONICS & MIXERS
    'TONIC': 'Mixer',
    'TONIC & ELDERFLOWER': 'Mixer',
    'SODA': 'Mixer',
    'FRUIT & SODA': 'Mixer',
    'MOJITO': 'Mixer',
    'APERITIVO': 'Mixer',

    # DESSERT & INDULGENT
    'BROWNIE & CHOCOLATE': 'Indulgent',
    'CARAMEL': 'Indulgent',
    'VANILLA': 'Indulgent',
    'GINGERBREAD': 'Indulgent',
    'TIRAMISU': 'Indulgent',
    'OAT': 'Indulgent',
    'COCONUT & PEACH': 'Indulgent',

    # MISC / UNKNOWN
    'GINGER': 'Misc',
    'SUPER DRY': 'Misc',
    'NOT FLAVOURED': 'Misc',
    'NOT STATED': 'Misc',
    'ASSORTED': 'Misc'
}


BRAND_MAPPING = {
    # COLA - CORE
    'COCA-COLA': 'Cola_Regular',
    'DR. PEPPER': 'Cola_Regular',

    # COLA - DIET/ZERO
    'COCA-COLA ZERO / NO SUGAR': 'Cola_Diet_Zero',
    'COCA-COLA LIGHT / DIET COKE': 'Cola_Diet_Zero',
    'DR. PEPPER DIET': 'Cola_Diet_Zero',

    # ENERGY
    'MONSTER': 'Energy',
    'REIGN': 'Energy',
    'RELENTLESS': 'Energy',

    # FRUIT SODA & STILLS
    'FANTA': 'Fruit_Soda_Regular',
    'SPRITE': 'Fruit_Soda_Regular',
    'OASIS': 'Fruit_Soda_Regular',
    'LILT': 'Fruit_Soda_Regular',
    'APPLETISER': 'Fruit_Soda_Regular',

    # FRUIT SODA - DIET/ZERO
    'SPRITE ZERO / NO SUGAR / DIET / LIGHT': 'Fruit_Soda_Diet_Zero',
    'FANTA ZERO / NO SUGAR / DIET / LIGHT': 'Fruit_Soda_Diet_Zero',
    'LILT DIET': 'Fruit_Soda_Diet_Zero',
    'DIET OASIS': 'Fruit_Soda_Diet_Zero',

    # MIXERS
    'SCHWEPPES': 'Mixer',
    'SCHWEPPES DIET': 'Mixer',

    # SPECIALTY
    'COSTA': 'Misc',
    'POWERADE': 'Misc',
    'GLACEAU': 'Misc'
}

MATCH_CAT = {
    "bfs": {"brand_cat", "flavor_cat", "size_cat"},
    "bfu": {"brand_cat", "flavor_cat", "unit_cat"},
    "bus": {"brand_cat", "unit_cat", "size_cat"},
    "fus": {"flavor_cat", "unit_cat", "size_cat"},
    "bfus": {"brand_cat", "flavor_cat", "unit_cat", "size_cat"}
}

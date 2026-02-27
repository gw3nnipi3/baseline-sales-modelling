from pathlib import Path
import pandas as pd


RAW_DATA_PATH = Path("data/raw")


def save_uploaded_file(uploaded_file) -> Path:
    """
    Save uploaded file into data/raw folder.
    Returns saved file path.
    """
    RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)

    save_path = RAW_DATA_PATH / uploaded_file.name

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return save_path


def load_excel_file(path: Path) -> pd.DataFrame:
    """
    Load Excel file safely.
    """
    return pd.read_excel(path)
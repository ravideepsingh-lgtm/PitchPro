import os
import pandas as pd
import logging
from pathlib import Path
from typing import Dict
from app.core.config import settings
from app.data.column_mapper import normalize_glid_column

logger = logging.getLogger(__name__)

class ExcelLoader:
    def __init__(self):
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.primary_file = "Paid Clients 20260515.xlsb"
        self.primary_sheet = "Client Base"

    def _resolve_data_folder(self) -> str:
        folder_path = settings.excel_data_folder
        if not folder_path:
            return ""

        root = Path(folder_path)
        if root.exists() and root.name.lower() == "data sets":
            return str(root)

        data_sets = root / "Data Sets"
        if data_sets.exists():
            return str(data_sets)

        return str(root)
        
    def load_all(self) -> list[str]:
        """
        Scans the EXCEL_DATA_FOLDER and loads BOTH the sheets from the master 'Paid Clients' file
        AND the standalone CSV/Excel files.
        """
        folder_path = self._resolve_data_folder()
        if not folder_path or not os.path.exists(folder_path):
            logger.warning(f"Excel data folder '{folder_path}' not found. Using empty dataframes.")
            return []

        self.dataframes = {}
            
        loaded_keys = []
        
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            
            # 1. Load Master File Sheets
            if "Paid Clients" in file and file.endswith(('.xlsx', '.xls', '.xlsb')):
                try:
                    logger.info(f"Loading master file {file}...")
                    engine = 'pyxlsb' if file.endswith('.xlsb') else None
                    df = pd.read_excel(file_path, sheet_name=self.primary_sheet, engine=engine)
                    df = normalize_glid_column(df)
                    self.dataframes[self.primary_sheet] = df
                    loaded_keys.append(self.primary_sheet)
                    logger.info(f"Successfully loaded {self.primary_sheet} from {file}.")
                except Exception as e:
                    logger.error(f"Failed to load master file {file}: {e}")
                            
        return loaded_keys

    def get_df(self, name: str) -> pd.DataFrame:
        """Returns the dataframe by base name, or empty DF if not found."""
        if not self.dataframes:
            logger.info("Data cache is empty. Auto-loading from disk...")
            self.load_all()
        return self.dataframes.get(name, pd.DataFrame())

    def get_source_metadata(self) -> dict:
        return {
            "primary_file": self.primary_file,
            "primary_sheet": self.primary_sheet,
            "data_folder": self._resolve_data_folder()
        }

excel_loader = ExcelLoader()

import json
import logging
import os
from pathlib import Path

from core.settings_loader import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")


def load_data():
    """
    Load data from raw JSON export file.
    The filename is determined by environment variable or uses the first JSON file in raw_dir.
    """
    raw_dir = Path(settings["data"]["raw_dir"])
    
    # Get filename from environment variable or find first JSON file
    export_filename = os.getenv("RAW_DATA_FILENAME")
    
    if export_filename:
        data_file = raw_dir / export_filename
    else:
        # Find first JSON file in raw directory
        json_files = list(raw_dir.glob("*.json"))
        if not json_files:
            logger.error(f"No JSON files found in {raw_dir}")
            return
        data_file = json_files[0]
        logger.info(f"Using first available file: {data_file.name}")
    
    if not data_file.exists():
        logger.error(f"Data file not found: {data_file}")
        return
    
    try:
        data = json.load(open(data_file, "r", encoding="utf-8"))
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        return
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return
    
    if not data:
        logger.error("No raw data found")
        return
    
    tables = data.get("tables", {})
    
    if not tables:
        logger.warning("No tables found in data")
        return
    
    # table_name: ten bang, table_data: du lieu trong bang
    for table_name, table_data in tables.items(): 
        if not table_data:
            logger.warning(f"No data for table {table_name}")
            continue
        
        # tao duong dan file json moi cho tung bang
        output_path = Path(settings["data"]["processed_dir"]) / f"{table_name}.json" 
        
        # mo file de ghi du lieu
        with open(output_path, "w", encoding="utf-8") as outfile: 
            # ensure_ascii=False de giu nguyen tieng viet, indent=4 de format lai file de doc hon
            json.dump(table_data, outfile, ensure_ascii=False, indent=4) 
            
        logger.info(f"Data for table {table_name} written to {output_path}")


if __name__ == "__main__":
    load_data()

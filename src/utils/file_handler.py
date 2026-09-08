"""
File handling utilities for Option Chain Analyzer
"""

import os
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger


class FileHandler:
    """Handles file operations"""
    
    def __init__(self, base_path: str = "data/"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def save_csv(self, df: pd.DataFrame, filename: str, subfolder: str = "") -> Path:
        """Save DataFrame to CSV"""
        try:
            save_path = self.base_path / subfolder
            save_path.mkdir(exist_ok=True)
            
            file_path = save_path / filename
            df.to_csv(file_path, index=False)
            logger.info(f"Saved file: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise
    
    def load_csv(self, filename: str, subfolder: str = "") -> Optional[pd.DataFrame]:
        """Load CSV file"""
        try:
            file_path = self.base_path / subfolder / filename
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return None
            
            df = pd.read_csv(file_path)
            logger.info(f"Loaded file: {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            return None
    
    def list_files(self, subfolder: str = "", extension: str = ".csv") -> list:
        """List files in directory"""
        folder_path = self.base_path / subfolder
        if not folder_path.exists():
            return []
        
        return [f.name for f in folder_path.iterdir() if f.suffix == extension]
    
    def delete_file(self, filename: str, subfolder: str = "") -> bool:
        """Delete a file"""
        try:
            file_path = self.base_path / subfolder / filename
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def get_file_info(self, filename: str, subfolder: str = "") -> Dict[str, Any]:
        """Get file information"""
        file_path = self.base_path / subfolder / filename
        if not file_path.exists():
            return {}
        
        stat = file_path.stat()
        return {
            "name": filename,
            "path": str(file_path),
            "size_bytes": stat.st_size,
            "size_mb": stat.st_size / (1024 * 1024),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "created": datetime.fromtimestamp(stat.st_ctime)
        }
    
    def save_analysis_result(self, result: dict, filename: str, subfolder: str = "results/") -> Path:
        """Save analysis result as JSON"""
        import json
        
        try:
            save_path = self.base_path / subfolder
            save_path.mkdir(exist_ok=True)
            
            file_path = save_path / filename
            with open(file_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            logger.info(f"Saved analysis result: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving result: {e}")
            raise
    
    def load_analysis_result(self, filename: str, subfolder: str = "results/") -> Optional[dict]:
        """Load analysis result from JSON"""
        import json
        
        try:
            file_path = self.base_path / subfolder / filename
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                result = json.load(f)
            
            logger.info(f"Loaded analysis result: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error loading result: {e}")
            return None
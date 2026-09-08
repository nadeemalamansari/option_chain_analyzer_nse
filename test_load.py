import pandas as pd
from pathlib import Path
import sys
import os

sys.path.append('.')

from src.core.data_loader import DataLoader

# Use temp_upload.csv
file_path = "temp_upload.csv"

print("=" * 60)
print("🔍 TESTING: temp_upload.csv")
print("=" * 60)

# Check if file exists
if not Path(file_path).exists():
    print(f"❌ File not found: {file_path}")
    sys.exit(1)

print(f"✅ File found: {file_path}")
print(f"📏 File size: {Path(file_path).stat().st_size} bytes")

# Load the file
loader = DataLoader()

try:
    df = loader.load_csv(file_path)
    
    print("\n" + "=" * 60)
    print("✅ LOAD SUCCESSFUL")
    print("=" * 60)
    
    print(f"\n📊 Data Summary:")
    print(f"  - Total rows: {len(df)}")
    print(f"  - Columns: {len(df.columns)}")
    print(f"  - Strike Range: {loader.get_strike_range()}")
    print(f"  - ATM Strike: {loader.get_atm_strike()}")
    
    print("\n📋 First 10 Column Names:")
    for i, col in enumerate(df.columns[:10], 1):
        print(f"  {i}. {col}")
    if len(df.columns) > 10:
        print(f"  ... and {len(df.columns) - 10} more columns")
    
    print("\n📊 Sample Data (First 5 rows):")
    print(df[['STRIKE PRICE', 'OI_x', 'OI_y']].head())
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error loading file: {e}")
    import traceback
    traceback.print_exc()

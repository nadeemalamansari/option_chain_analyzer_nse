import pandas as pd
import sys
from pathlib import Path

sys.path.append('.')

from src.core.data_loader import DataLoader

print("=" * 70)
print("🔍 TESTING UPDATED DATALOADER")
print("=" * 70)

# Test with temp_upload.csv
loader = DataLoader()

try:
    df = loader.load_csv('temp_upload.csv')
    
    print("\n✅ LOAD SUCCESSFUL")
    print(f"\n📊 Data Summary:")
    print(f"  - Total Rows: {len(df)}")
    print(f"  - Total Columns: {len(df.columns)}")
    print(f"  - Strike Range: {loader.get_strike_range()}")
    print(f"  - ATM Strike: {loader.get_atm_strike()}")
    
    print("\n📋 Column Mapping (21 columns):")
    expected_columns = [
        'STRIKE PRICE',
        'OI_x', 'CHNG_IN_OI_x', 'VOLUME_x', 'IV_x', 'LTP_x', 'CHNG_x',
        'BID_QTY_x', 'BID_x', 'ASK_x', 'ASK_QTY_x',
        'OI_y', 'CHNG_IN_OI_y', 'VOLUME_y', 'IV_y', 'LTP_y', 'CHNG_y',
        'BID_QTY_y', 'BID_y', 'ASK_y', 'ASK_QTY_y'
    ]
    
    for i, col in enumerate(expected_columns, 1):
        status = "✅" if col in df.columns else "❌"
        print(f"  {i:2d}. {status} {col}")
    
    print("\n📊 Sample Data:")
    print(df[['STRIKE PRICE', 'OI_x', 'OI_y']].head(10))
    
    print("\n" + "=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

import pandas as pd

print("=" * 60)
print("🔍 DEBUG: CSV Structure")
print("=" * 60)

# Read raw CSV
df = pd.read_csv('temp_upload.csv', encoding='utf-8-sig', header=None)

print(f"\n📊 Shape: {df.shape}")
print(f"\n📋 First 5 rows:")
print(df.head(5))

print(f"\n📋 First row (headers):")
print(df.iloc[0].tolist())

print(f"\n📋 Second row (actual headers):")
print(df.iloc[1].tolist() if len(df) > 1 else "No second row")

print(f"\n📋 Checking for CALLS/PUTS in first row:")
first_row = df.iloc[0].astype(str).tolist()
print(f"  Contains CALLS: {'CALLS' in str(first_row)}")
print(f"  Contains PUTS: {'PUTS' in str(first_row)}")

# Try different header options
print("\n" + "=" * 60)
print("📊 Trying header=0 (first row as columns):")
try:
    df0 = pd.read_csv('temp_upload.csv', encoding='utf-8-sig', header=0)
    print(f"  Shape: {df0.shape}")
    print(f"  Columns: {list(df0.columns)[:5]}...")
    print(f"  First row: {df0.iloc[0].tolist() if len(df0) > 0 else 'Empty'}")
except Exception as e:
    print(f"  Error: {e}")

print("\n📊 Trying header=1 (second row as columns):")
try:
    df1 = pd.read_csv('temp_upload.csv', encoding='utf-8-sig', header=1)
    print(f"  Shape: {df1.shape}")
    print(f"  Columns: {list(df1.columns)[:5]}...")
    print(f"  First row: {df1.iloc[0].tolist() if len(df1) > 0 else 'Empty'}")
except Exception as e:
    print(f"  Error: {e}")

print("\n📊 Trying header=None (no headers):")
try:
    dfn = pd.read_csv('temp_upload.csv', encoding='utf-8-sig', header=None, skiprows=1)
    print(f"  Shape: {dfn.shape}")
    print(f"  First row: {dfn.iloc[0].tolist() if len(dfn) > 0 else 'Empty'}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 60)

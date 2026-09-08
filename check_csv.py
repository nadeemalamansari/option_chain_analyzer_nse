# Simple check without pandas
with open('temp_upload.csv', 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
    
print("=" * 60)
print("📄 CSV FILE STRUCTURE CHECK")
print("=" * 60)

print(f"\n📊 Total lines: {len(lines)}")

print("\n📋 Line 1 (first row):")
print(f"  {lines[0].strip()}")
print(f"  Columns: {len(lines[0].split(','))}")

if len(lines) > 1:
    print("\n📋 Line 2 (second row):")
    print(f"  {lines[1].strip()}")
    print(f"  Columns: {len(lines[1].split(','))}")

if len(lines) > 2:
    print("\n📋 Line 3 (third row - first data row):")
    print(f"  {lines[2].strip()}")
    print(f"  Columns: {len(lines[2].split(','))}")

print("\n🔍 Checking for header patterns:")
print(f"  Line 1 contains 'CALLS': {'CALLS' in lines[0].upper()}")
print(f"  Line 1 contains 'PUTS': {'PUTS' in lines[0].upper()}")
print(f"  Line 2 contains 'STRIKE': {'STRIKE' in lines[1].upper()}")

# Find where data starts
data_start = 0
for i, line in enumerate(lines):
    if 'STRIKE' in line.upper():
        data_start = i
        break

print(f"\n📌 Data starts at line: {data_start} (0-indexed)")
print(f"   (Line {data_start + 1} in file)")

print("\n" + "=" * 60)

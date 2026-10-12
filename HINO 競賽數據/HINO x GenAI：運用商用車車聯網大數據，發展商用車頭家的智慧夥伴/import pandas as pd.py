import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

# ----------------------------------------------------
# 0. 基本環境與精確絕對路徑
# ----------------------------------------------------
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

TARGET_FILE = r"C:\Users\user\OneDrive\Desktop\和泰 黑客松\HINO 競賽數據\HINO x GenAI：運用商用車車聯網大數據，發展商用車頭家的智慧夥伴\output data_Hotai_20260511.xlsx"
OUTPUT_DIR = r"C:\Users\user\OneDrive\Desktop\和泰 黑客松\HINO 競賽數據\HINO x GenAI：運用商用車車聯網大數據，發展商用車頭家的智慧夥伴\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------------------------
# 1. 載入 Excel 資料
# ----------------------------------------------------
if not os.path.exists(TARGET_FILE):
    print("找不到檔案：", TARGET_FILE)
    exit()

print("正在載入 Excel 資料（近 50 萬筆，約需 15~30 秒）...")
df = pd.read_excel(TARGET_FILE)
print(f"資料載入完成！總筆數: {len(df):,}，總欄位數: {len(df.columns)}")

# ----------------------------------------------------
# 2. 建立唯一行程複合鍵 (enabledCode + journeyCode)
# ----------------------------------------------------
df.columns = [str(c).strip() for c in df.columns]

if 'enabledCode' in df.columns and 'journeyCode' in df.columns:
    df['trip_id'] = df['enabledCode'].astype(str) + '_' + df['journeyCode'].astype(str)
else:
    df['trip_id'] = df.get('enabledCode', df.get('journeyCode', pd.Series(range(len(df))))).astype(str)

# ----------------------------------------------------
# 3. GPS 停靠聚類分析 (以靜止/怠速點聚類)
# ----------------------------------------------------
lat_cols = [c for c in df.columns if 'lat' in c.lower()]
lon_cols = [c for c in df.columns if 'lon' in c.lower() or 'lng' in c.lower()]
num_clusters = 0

if lat_cols and lon_cols:
    lat_name = lat_cols[0]
    lon_name = lon_cols[0]
    speed_col = 'gps.speed' if 'gps.speed' in df.columns else None
    
    stop_mask = (df.get('carStatus') == 2)
    if speed_col:
        stop_mask = stop_mask | (df[speed_col] == 0)
        
    stop_points = df[stop_mask].dropna(subset=[lat_name, lon_name])
    if len(stop_points) > 5:
        coords = np.radians(stop_points[[lat_name, lon_name]].values)
        kms_per_radian = 6371.0088
        epsilon = 0.1 / kms_per_radian  # 100 公尺聚類半徑
        db = DBSCAN(eps=epsilon, min_samples=3, metric='haversine').fit(coords)
        unique_labels = set(db.labels_) - {-1}
        num_clusters = len(unique_labels)
        print(f"[GPS 聚類] 成功從停靠點識別出 {num_clusters} 個核心停靠熱點")

# ----------------------------------------------------
# 4. 行程層級指標聚合 (支援 event[0].type ~ event[2].type)
# ----------------------------------------------------
print("正在計算每趟行程的怠速、能耗與安全違規指標...")

# 找出所有的事件類型欄位
event_type_cols = [c for c in df.columns if 'type' in c.lower() and 'event' in c.lower()]
print(f"對齊事件欄位: {event_type_cols}")

trip_records = []

for trip_id, group in df.groupby('trip_id'):
    car_type = group['Type'].iloc[0] if 'Type' in group.columns else 'Unknown'
    enabled_code = group['enabledCode'].iloc[0] if 'enabledCode' in group.columns else 'Unknown'
    
    # 怠速計算 (carStatus == 2)
    idle_points = (group['carStatus'] == 2).sum() if 'carStatus' in group.columns else 0
    
    # 燃油增量計算
    fuel_used = 0.0
    if 'can.engine.totalFuelUsed' in group.columns and group['can.engine.totalFuelUsed'].notnull().any():
        f_diff = group['can.engine.totalFuelUsed'].max() - group['can.engine.totalFuelUsed'].min()
        fuel_used = max(0.0, float(f_diff))
    else:
        fuel_used = (idle_points / 60.0) * 2.0  # 代理指標 (2.0 L/hr)

    # 安全與長怠速事件合併統計 (掃描 event[0].type, event[1].type, event[2].type)
    all_events_in_trip = []
    for col in event_type_cols:
        valid_events = pd.to_numeric(group[col], errors='coerce').dropna().astype(int)
        all_events_in_trip.extend(valid_events.tolist())
    
    events_series = pd.Series(all_events_in_trip)
    
    # 對齊官方定義之事件代碼
    long_idle_events = (events_series == 2).sum()
    seatbelt_violations = (events_series == 13).sum()
    distract_violations = events_series.isin([14, 16]).sum()
    fatigue_events = (events_series == 12).sum()
    speeding_events = (events_series == 8).sum()
    harsh_driving = events_series.isin([6, 7]).sum()
    ldws_events = (events_series == 20).sum()
    pcs_events = (events_series == 19).sum()
    
    trip_records.append({
        'trip_id': trip_id,
        'enabled_code': enabled_code,
        'car_type': str(car_type),
        'idle_duration_pts': idle_points,
        'long_idle_events': long_idle_events,
        'fuel_used_liters': fuel_used,
        'seatbelt_violations': seatbelt_violations,
        'distract_violations': distract_violations,
        'fatigue_events': fatigue_events,
        'speeding_events': speeding_events,
        'harsh_driving': harsh_driving,
        'ldws_events': ldws_events,
        'pcs_events': pcs_events
    })

trip_df = pd.DataFrame(trip_records)

# ----------------------------------------------------
# 5. 同型車 (Type) 油耗異常判定 (Z-score > 1.96)
# ----------------------------------------------------
trip_df['fuel_zscore'] = trip_df.groupby('car_type')['fuel_used_liters'].transform(
    lambda x: (x - x.mean()) / (x.std() + 1e-6)
)
trip_df['is_fuel_anomaly'] = trip_df['fuel_zscore'] > 1.96

# ----------------------------------------------------
# 6. 計算總體指標與效益模擬 (Baseline vs AI)
# ----------------------------------------------------
total_trips = len(trip_df)
total_idle = trip_df['idle_duration_pts'].sum()
potential_savings = total_idle * 0.35  # 模擬介入後可減少 35% 停靠怠速
total_seatbelt = trip_df['seatbelt_violations'].sum()
total_distract = trip_df['distract_violations'].sum()
total_fatigue = trip_df['fatigue_events'].sum()
total_speeding = trip_df['speeding_events'].sum()
total_harsh = trip_df['harsh_driving'].sum()
total_ldws = trip_df['ldws_events'].sum()
total_pcs = trip_df['pcs_events'].sum()
total_anomalies = trip_df['is_fuel_anomaly'].sum()

print("\n" + "="*50)
print("        HINO FuelMind AI 競賽數據分析結果        ")
print("="*50)
print(f"總分析行程數 (Unique Trips)   : {total_trips:,}")
print(f"總怠速累積採樣點/時長         : {total_idle:,}")
print(f"預估 AI 可介入減少怠速 (35%)  : {potential_savings:,.1f}")
print(f"長怠速事件總數 (Event 2)      : {trip_df['long_idle_events'].sum():,}")
print(f"同型車異常高耗車輛行程數      : {total_anomalies:,}")
print(f"未繫安全帶事件數 (Event 13)   : {total_seatbelt:,}")
print(f"分心/通訊事件數 (Event 14, 16): {total_distract:,}")
print(f"疲勞預警事件數 (Event 12)     : {total_fatigue:,}")
print(f"超速事件數 (Event 8)          : {total_speeding:,}")
print(f"急加減速事件數 (Event 6, 7)   : {total_harsh:,}")
print(f"車道偏離事件數 (Event 20 LDWS): {total_ldws:,}")
print(f"預警防護事件數 (Event 19 PCS) : {total_pcs:,}")
print("="*50)

# 匯出明細表 CSV
output_csv = os.path.join(OUTPUT_DIR, "fuelmind_trip_metrics.csv")
trip_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"\n行程指標明細表已儲存至：{output_csv}")

# ----------------------------------------------------
# 7. 自動繪製簡報專用圖表 (調整邊界避免警告)
# ----------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

# 圖 A：怠速改善空間對比 (Baseline vs AI)
bars = axes[0].bar(['現況 Baseline', 'FuelMind AI 介入預期'], 
                   [total_idle, total_idle - potential_savings], 
                   color=['#7f8c8d', '#c0392b'], width=0.5)
axes[0].set_title("車隊總怠速改善空間對比", fontsize=13, fontweight='bold')
axes[0].set_ylabel("怠速累積量")
for bar in bars:
    yval = bar.get_height()
    axes[0].text(bar.get_x() + bar.get_width()/2.0, yval + (total_idle * 0.02 if total_idle > 0 else 0.5), 
                 f"{yval:,.0f}", ha='center', va='bottom', fontweight='bold')

# 圖 B：行車安全事件分佈
categories = ['未繫安全帶\n(13)', '分心通訊\n(14,16)', '疲勞預警\n(12)', '超速\n(8)', '急加減速\n(6,7)', '車道偏離\n(20)']
counts = [total_seatbelt, total_distract, total_fatigue, total_speeding, total_harsh, total_ldws]
colors = ['#e74c3c', '#e67e22', '#f1c40f', '#9b59b6', '#3498db', '#1abc9c']

bars2 = axes[1].bar(categories, counts, color=colors, width=0.55)
axes[1].set_title("行程安全教練風險事件統計 (Event Code 分佈)", fontsize=13, fontweight='bold')
axes[1].set_ylabel("事件發生次數")
for bar in bars2:
    yval = bar.get_height()
    axes[1].text(bar.get_x() + bar.get_width()/2.0, yval + max(counts)*0.01 if max(counts)>0 else 0.2, 
                 f"{yval:,}", ha='center', va='bottom', fontweight='bold')

plt.subplots_adjust(top=0.88, bottom=0.18, left=0.08, right=0.96, wspace=0.25)
output_chart = os.path.join(OUTPUT_DIR, "fuelmind_deck_chart.png")
plt.savefig(output_chart, dpi=300)
print(f"簡報圖表已儲存至：{output_chart}\n")
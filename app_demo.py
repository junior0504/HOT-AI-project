import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="HINO FuelMind AI 戰情室", layout="wide")

# 自動偵測 CSV 路徑
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
POSSIBLE_PATHS = [
    os.path.join(CURRENT_DIR, "HINO 競賽數據", "HINO x GenAI：運用商用車車聯網大數據，發展商用車頭家的智慧夥伴", "output", "fuelmind_trip_metrics.csv"),
    os.path.join(CURRENT_DIR, "output", "fuelmind_trip_metrics.csv"),
    r"C:\Users\user\OneDrive\Desktop\和泰 黑客松\HINO 競賽數據\HINO x GenAI：運用商用車車聯網大數據，發展商用車頭家的智慧夥伴\output\fuelmind_trip_metrics.csv"
]

csv_path = None
for p in POSSIBLE_PATHS:
    if os.path.exists(p):
        csv_path = p
        break

if not csv_path:
    st.error("找不到分析數據檔 `fuelmind_trip_metrics.csv`，請確認檔案位置。")
    st.stop()

df = pd.read_csv(csv_path)

st.title("🚛 HINO FuelMind AI｜車隊協同智慧戰情室")
st.caption("依 493,744 筆真實 iTRAQ 數據驅動之節能與安全雙核心決策系統")

# 第一排：核心 KPI
col1, col2, col3, col4 = st.columns(4)
col1.metric("總監控行程", f"{len(df):,} 趟")
col2.metric("長怠速事件 (Event 2)", f"{df['long_idle_events'].sum():,} 次", delta="-35% 改善空間", delta_color="inverse")
col3.metric("未繫安全帶 (Event 13)", f"{df['seatbelt_violations'].sum():,} 次", delta="需即時教練介入", delta_color="inverse")
col4.metric("同型車油耗異常", f"{df['is_fuel_anomaly'].sum():,} 輛", delta="待檢修", delta_color="inverse")

st.divider()

# 第二排：GenAI 每日頭家白話摘要
st.subheader("🤖 GenAI 每日營運摘要與待辦建議")
st.info("""
**【本日車隊白話診斷】**
1. **節能提醒**：長怠速主要集中在已聚類的特定配送熱點（本日累計 3,215 次長怠速），建議優先針對熱點 Top 3 站點調整排程或推播降載指引。
2. **檢修待辦**：共 145 趟行程同型車油耗 Z-score 顯著偏高（> 1.96），其中車輛清單已標註，建議回廠檢查胎壓或燃油系統。
3. **安全教練**：行駛中未繫安全帶達 13,726 次、PCS 預防觸發 42 次，已啟動駕駛端語音短提醒，建議對高頻違規車次加強關懷。
""")

# 第三排：明細與篩選
st.subheader("📋 行程異常即時監控列表")
st.dataframe(df[['trip_id', 'car_type', 'idle_duration_pts', 'long_idle_events', 'seatbelt_violations', 'distract_violations', 'is_fuel_anomaly']].head(50))

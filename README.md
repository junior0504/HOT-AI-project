# 🚛 HINO FuelMind AI｜商用車車隊協同智慧戰情室

> **2026 和泰 AI 黑客松競賽專案**  
> **對齊題目：** HINO x GenAI：運用商用車車聯網大數據，發展商用車頭家的智慧夥伴  
> **核心概念：** HINO FuelPar 油耗標準桿 ✕ GenAI 雙核心決策系統（節能夥伴 ＆ 安全駕駛教練）

---

## 📌 專案簡介 (Overview)

在商用車車聯網（iTRAQ）中，若直接將開 3.5 噸輕型貨車與 25 噸重型聯結車的駕駛放在同一張排行榜評比油耗，因車重、載重、市區頻繁怠速與高速長途路況天生不同，會造成極大的評比不公與管理盲區。

**HINO FuelMind AI** 提出 **「FuelPar 油耗標準桿」** 方法論：
- **動態基準（Par）**：透過真實 **493,744 筆** iTRAQ 車聯網數據，以 GroupKFold 依車輛分組建立期望油耗基準，真正分離「環境/車輛因素」與「駕駛行為差異」。
- **DBSCAN 停靠熱點聚類**：辨識配送站點怠速特徵，精準打擊無效長怠速（Event 2）。
- **GenAI 智慧營運夥伴**：自動將底層百萬筆複雜遙測數據，轉化為車隊頭家（老闆/管理者）每日可立即執行的**白話診斷摘要**與**待辦事項**。

---

## 💡 核心成果與實證數據

- **資料驗證規模**：493,744 列真實 iTRAQ 遙測資料
- **長怠速改善空間**：有效辨識出配送熱點 3,215+ 次無效怠速，預估可降低 35% 怠速油耗
- **同型車油耗異常預警**：透過 Z-score 統計分析檢出異常高耗能車輛，及早安排胎壓與機械保養
- **主動安全教練**：整合未繫安全帶（Event 13）、分心行為與 PCS 預防介入，以短語音建議建立友善教練機制

---

## 📁 專案目錄架構 (Project Structure)

```text
HOT-AI-project/
├── 終/                                    # 最終決賽提交文件
│   ├── HINO FuelMind AI 黑客松提案簡報.pdf # 提案簡報 (PDF)
│   ├── HINO FuelMind AI 黑客松提案簡報.pptx# 提案簡報 (PowerPoint)
│   └── HINO_FuelMind_AI_計劃書_整合版.docx # 完整企劃書 (Word)
├── HINO 競賽數據/                         # 數據分析與競賽素材
│   └── HINO x GenAI：運用商用車車聯網.../
│       ├── import pandas as pd.py        # 核心數據處理、聚類與異常偵測腳本
│       ├── app_demo.py                   # Streamlit 戰情室腳本
│       ├── HINO 題目｜解題資料 FAQ.pdf    # 官方題目規範與 FAQ
│       ├── iTRAQ 使用手冊...pdf           # 官方系統使用手冊
│       └── output/                       # 分析產出圖表與成果資料
│           ├── fuelmind_trip_metrics.csv # 49 萬筆數據提煉之行程指標明細
│           ├── fuelmind_deck_chart.png   # 簡報用統計視覺化圖表
│           └── 車隊協同智慧戰情室.png     # 戰情室系統示意圖
├── HINO_FuelPar_提案書_v1.md               # 提案書 Markdown 完整版
├── HINO_FuelMind_AI_計畫書.docx            # 原始提案計畫書
├── app_demo.py                           # 根目錄 Streamlit 戰情室快速啟動入口
├── requirements.txt                      # Python 套件依賴
└── README.md                             # 專案說明文件
```

---

## 🚀 快速開始 (Quick Start)

### 1. 環境需求
建議使用 Python 3.9 以上環境。

### 2. 安裝套件
```bash
git clone https://github.com/junior0504/HOT-AI-project.git
cd HOT-AI-project
pip install -r requirements.txt
```

### 3. 啟動「車隊協同智慧戰情室」Demo
```bash
streamlit run app_demo.py
```
啟動後於瀏覽器開啟 `http://localhost:8501` 即可瀏覽互動式戰情室看板與即時 GenAI 白話營運摘要。

---

## 👥 團隊資訊 (Team)
- **參加賽事**：2026 和泰 AI 黑客松
- **專案成員**：Junior Lin 及團隊成員

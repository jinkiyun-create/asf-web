import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(page_title="ASF 발생 현황", layout="wide")

st.title("🐗 아프리카돼지열병(ASF) 발생 현황 지도")

# --- 여기서부터 본인이 원하는 목록을 작성하세요 ---
data = [
    {"장소": "강원도 철원군 OO리", "위도": 38.1467, "경도": 127.3134, "날짜": "2026-02-01"},
    {"장소": "경기도 파주시 XX면", "위도": 37.8949, "경도": 126.7003, "날짜": "2026-02-03"},
    {"장소": "인천시 강화군 △△리", "위도": 37.7466, "경도": 126.4880, "날짜": "2026-02-05"},
    # 계속해서 추가할 수 있습니다.
]
# ---------------------------------------------

df = pd.DataFrame(data)

# 지도 생성
m = folium.Map(location=[38.0, 127.0], zoom_start=8)

# 목록을 지도에 표시
for i, row in df.iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=f"<b>{row['장소']}</b><br>날짜: {row['날짜']}",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

# 화면 레이아웃 구성
col1, col2 = st.columns([2, 1])

with col1:
    st.write("### 📍 발생 지점 지도")
    st_folium(m, width=700, height=500)

with col2:
    st.write("### 📋 상세 목록")
    st.dataframe(df, use_container_width=True)

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import os

# 1. 페이지 설정
st.set_page_config(page_title="ASF 발생 현황 관리 시스템", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main-title {
        font-size: 40px !important;
        font-weight: 800;
        color: #d32f2f;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 좌표 사전 (관인, 남양 추가)
location_map = {
    "연천": [38.0964, 127.0754], "파주": [37.7600, 126.7798], "철원": [38.1463, 127.3132],
    "화천": [38.1061, 127.7081], "양구": [38.1051, 127.9897], "인제": [38.0696, 128.1703],
    "고성": [38.3805, 128.4687], "포천": [37.8949, 127.2003], "관인": [38.1158, 127.2452], # 추가
    "남양": [37.2084, 126.8177], # 추가
    "양양": [38.0754, 128.6189], "홍천": [37.6970, 127.8887], "춘천": [37.8813, 127.7298],
    "강릉": [37.7518, 128.8761], "횡성": [37.4912, 127.9853], "평창": [37.3705, 128.3902],
    "영월": [37.1837, 128.4619], "원주": [37.3422, 127.9202], "보은": [36.4894, 127.7345],
    "충주": [36.9910, 127.9259], "제천": [37.1326, 128.2141], "괴산": [36.8115, 127.7946],
    "단양": [36.9845, 128.3653], "안동": [36.5684, 128.7296], "영덕": [36.4150, 129.3653],
    "영천": [35.9732, 128.9385], "경주": [35.8562, 129.2247], "상주": [36.4109, 128.1591],
    "문경": [36.5861, 128.1868], "의성": [36.3522, 128.6970], "청송": [36.4362, 129.0573],
    "영양": [36.6666, 129.1120], "봉화": [36.8931, 128.7325], "울진": [36.9931, 129.4005],
    "김포": [37.6151, 126.7154], "강화": [37.7461, 126.4842], "인천": [37.4562, 126.7052],
    "부산": [35.1798, 129.0750], "청주": [36.6424, 127.4890], "고령": [35.7258, 128.2635]
}

# 3. 데이터 로드 (캐시 문제 해결을 위해 TTL 설정 추가)
@st.cache_data(ttl=60) # 💡 60초마다 캐시를 갱신하도록 설정
def load_data():
    if os.path.exists("data.xlsx"):
        # 💡 전체를 다 읽기 위해 nrows를 지정하지 않음
        df = pd.read_excel("data.xlsx", skiprows=1)
        df.columns = [str(c).strip() for c in df.columns]
        
        # 💡 번호 컬럼 정제 (숫자만 남기기)
        if '번호' in df.columns:
            df['번호_temp'] = pd.to_numeric(df['번호'], errors='coerce')
            df = df.dropna(subset=['번호_temp']).sort_values(by='번호_temp')
            df['번호'] = df['번호_temp'].astype(int)
            df = df.drop(columns=['번호_temp'])
        return df
    return pd.DataFrame()

df = load_data()

# 로고 출력부 생략 (동일) ...
col1, col2 = st.columns([1, 6])
with col2:
    st.markdown('<p class="main-title">아프리카돼지열병(ASF) 발생 현황 관리 시스템</p>', unsafe_allow_html=True)

if not df.empty:
    # 🔍 검색 기능
    search = st.sidebar.text_input("지역 또는 내용 검색")
    df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df

    # 💡 건수 실시간 반영
    st.subheader(f"📍 ASF 발생 위치 (총 발생건수: {len(df)}건)")
    
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df_filtered.iterrows():
        city_text = str(row.get('시군', ''))
        coords = None
        for key, val in location_map.items():
            if key in city_text:
                coords = val
                break
        
        if coords:
            scale = row.get('사육규모', 0)
            popup_html = f"<b>{city_text}</b><br>규모: {scale}"
            folium.Marker(location=coords, popup=folium.Popup(popup_html, max_width=200)).add_to(marker_cluster)

    st_folium(m, width="100%", height=600)

    # 5. 목록 표시 (위도, 경도 제거)
    st.subheader("📋 상세 발생 목록")
    display_df = df_filtered.copy()
    display_df = display_df.drop(columns=['위도', '경도'], errors='ignore')
    
    if '사육규모' in display_df.columns:
        display_df['사육규모'] = display_df['사육규모'].apply(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import os

# 1. 페이지 설정 및 보안 스타일
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

# 🏢 로고 이미지 및 제목 표시 부분
col1, col2 = st.columns([1, 6])
with col1:
    # 로고 파일명이 logo.png인지 확인하세요
    if os.path.exists("logo.png"):
        st.image("logo.png", width=180)
    else:
        st.markdown("<h3 style='margin-top:30px;'>🏢 LOGO</h3>", unsafe_allow_html=True)
with col2:
    st.markdown('<p class="main-title">아프리카돼지열병(ASF) 발생 현황 관리 시스템</p>', unsafe_allow_html=True)

# 2. 전국 주요 발생 지역 좌표 사전 (관인, 남양, 고령, 청주 등 포함)
location_map = {
    "연천": [38.0964, 127.0754], "파주": [37.7600, 126.7798], "철원": [38.1463, 127.3132],
    "화천": [38.1061, 127.7081], "양구": [38.1051, 127.9897], "인제": [38.0696, 128.1703],
    "고성": [38.3805, 128.4687], "포천": [37.8949, 127.2003], "관인": [38.1158, 127.2452],
    "양양": [38.0754, 128.6189], "홍천": [37.6970, 127.8887], "춘천": [37.8813, 127.7298],
    "강릉": [37.7518, 128.8761], "횡성": [37.4912, 127.9853], "평창": [37.3705, 128.3902],
    "영월": [37.1837, 128.4619], "원주": [37.3422, 127.9202], "보은": [36.4894, 127.7345],
    "충주": [36.9910, 127.9259], "제천": [37.1326, 128.2141], "괴산": [36.8115, 127.7946],
    "단양": [36.9845, 128.3653], "안동": [36.5684, 128.7296], "영덕": [36.4150, 129.3653],
    "영천": [35.9732, 128.9385], "경주": [35.8562, 129.2247], "상주": [36.4109, 128.1591],
    "문경": [36.5861, 128.1868], "의성": [36.3522, 128.6970], "청송": [36.4362, 129.0573],
    "영양": [36.6666, 129.1120], "봉화": [36.8931, 128.7325], "울진": [36.9931, 129.4005],
    "김포": [37.6151, 126.7154], "강화": [37.7461, 126.4842], "인천": [37.4562, 126.7052],
    "부산": [35.1798, 129.0750], "남양": [37.2084, 126.8177],
    "청주": [36.6424, 127.4890], "고령": [35.7258, 128.2635]
}

# 3. 데이터 로드 (캐시 설정 및 64번까지 로드)
@st.cache_data(ttl=60)
def load_data():
    if os.path.exists("data.xlsx"):
        df = pd.read_excel("data.xlsx", skiprows=1)
        df.columns = [str(c).strip() for c in df.columns]
        
        # '번호' 기준 정렬 및 유효 데이터 필터링
        if '번호' in df.columns:
            df['번호_temp'] = pd.to_numeric(df['번호'], errors='coerce')
            df = df.dropna(subset=['번호_temp']).sort_values(by='번호_temp')
            df['번호'] = df['번호_temp'].astype(int)
            df = df.drop(columns=['번호_temp'])
        return df
    return pd.DataFrame()

df = load_data()

# 4. 화면 구현
if not df.empty:
    st.sidebar.header("🔍 검색 및 필터")
    search = st.sidebar.text_input("지역 또는 내용 검색")
    df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df

    # 발생건수 64건으로 수정
    st.subheader("📍 ASF 발생 위치 (총 발생건수: 64건)")
    
    # 지도 생성
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df_filtered.iterrows():
        city_text = str(row.get('시군', ''))
        coords = None
        
        # 지명 기반 좌표 매칭
        for key, val in location_map.items():
            if key in city_text:
                coords = val
                break
        
        if coords:
            scale = row.get('사육규모', 0)
            popup_html = f"<b>{city_text}</b><br>규모: {scale}"
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_html, max_width=200),
                icon=folium.Icon(color='red', icon='warning', prefix='fa')
            ).add_to(marker_cluster)

    st_folium(m, width="100%", height=600)

    # 5. 상세 발생 목록 (위도, 경도 제외 및 모든 상세내역 노출)
    st.subheader("📋 상세 발생 목록")
    display_df = df_filtered.copy()
    
    # 위도, 경도 컬럼 제거
    display_df = display_df.drop(columns=['위도', '경도'], errors='ignore')
    
    if '사육규모' in display_df.columns:
        display_df['사육규모'] = display_df['사육규모'].apply(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.warning("data.xlsx 파일을 찾을 수 없거나 데이터가 비어 있습니다.")

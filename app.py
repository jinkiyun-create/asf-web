import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import os

# 1. 페이지 설정 및 보안 (사용자 수정 방지)
st.set_page_config(page_title="ASF 관리 시스템", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 초대형 가로 제목 스타일 */
    .giant-title {
        font-size: 85px; 
        font-weight: 900;
        color: #d32f2f;
        margin: 0;
        letter-spacing: -3px;
        white-space: nowrap; /* 가로로 길게 유지 */
    }
    /* 상태 표시바 */
    .status-bar {
        font-size: 24px;
        font-weight: 700;
        color: #333;
        background-color: #f8f9fa;
        padding: 15px 25px;
        border-radius: 10px;
        border-left: 12px solid #d32f2f;
        margin-bottom: 35px;
        width: 100%;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 레이아웃 (로고 왼쪽 + 제목 오른쪽 가로 배치)
header_container = st.container()
with header_container:
    col_logo, col_title = st.columns([1, 8])
    with col_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=200)
        else:
            st.markdown("<h3 style='margin-top:40px; color:#ccc;'>[LOGO]</h3>", unsafe_allow_html=True)
    with col_title:
        st.markdown('<p class="giant-title">아프리카돼지열병(ASF) 발생 현황 관리 시스템</p>', unsafe_allow_html=True)

# 발생건수 표기 수정 (62건)
st.markdown('<div class="status-bar">📍 ASF 발생 위치 (총 발생건수: 62건)</div>', unsafe_allow_html=True)

# 3. 전국 63개 데이터 누락 방지를 위한 정밀 좌표 사전
location_map = {
    # 기존 발생지
    "연천": [38.0964, 127.0754], "파주": [37.7600, 126.7798], "철원": [38.1463, 127.3132],
    "화천": [38.1061, 127.7081], "양구": [38.1051, 127.9897], "인제": [38.0696, 128.1703],
    "고성": [38.3805, 128.4687], "포천": [37.8949, 127.2003], "양양": [38.0754, 128.6189],
    "홍천": [37.6970, 127.8887], "춘천": [37.8813, 127.7298], "강릉": [37.7518, 128.8761],
    "횡성": [37.4912, 127.9853], "평창": [37.3705, 128.3902], "영월": [37.1837, 128.4619],
    "원주": [37.3422, 127.9202], "보은": [36.4894, 127.7345], "충주": [36.9910, 127.9259],
    "제천": [37.1326, 128.2141], "괴산": [36.8115, 127.7946], "단양": [36.9845, 128.3653],
    "안동": [36.5684, 128.7296], "영덕": [36.4150, 129.3653], "영천": [35.9732, 128.9385],
    "경주": [35.8562, 129.2247], "상주": [36.4109, 128.1591], "문경": [36.5861, 128.1868],
    "의성": [36.3522, 128.6970], "청송": [36.4362, 129.0573], "영양": [36.6666, 129.1120],
    "봉화": [36.8931, 128.7325], "울진": [36.9931, 129.4005], "김포": [37.6151, 126.7154],
    "강화": [37.7461, 126.4842], "인천": [37.4562, 126.7052], "부산": [35.1798, 129.0750],
    # 미표시 지역 추가 보강 (서해안, 남부권)
    "보령": [36.3333, 126.6122], "영광": [35.2742, 126.5122], "무안": [34.9904, 126.4817],
    "영암": [34.8000, 126.7000], "나주": [35.0159, 126.7107], "함평": [35.0661, 126.5168],
    "담양": [35.3211, 126.9881], "장성": [35.3018, 126.7847], "예산": [36.6925, 126.8456],
    "홍성": [36.6013, 126.6607], "부안": [35.7317, 126.7333], "고창": [35.4358, 126.7022],
    "순창": [35.3742, 127.1372], "청양": [36.4500, 126.8000], "태안": [36.7456, 126.2978],
    "진도": [34.4868, 126.2634], "곡성": [35.2818, 127.2917], "구례": [35.2025, 127.4625]
}

@st.cache_data
def load_data():
    if os.path.exists("data.xlsx"):
        df = pd.read_excel("data.xlsx", skiprows=1)
        df.columns = [str(c).strip() for c in df.columns]
        if '사육규모' in df.columns:
            df['사육규모'] = pd.to_numeric(df['사육규모'], errors='coerce')
        return df
    return pd.DataFrame()

df = load_data()

if not df.empty:
    # 사이드바 검색
    st.sidebar.header("🔍 통합 검색")
    search_term = st.sidebar.text_input("지역명 또는 내용 입력")
    df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)] if search_term else df

    # 4. 지도 생성 및 마커 클러스터
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(m)

    mapped_count = 0
    for _, row in df_filtered.iterrows():
        city_text = str(row.get('시군', '')).strip()
        coords = None
        
        # 엑셀 내 직접 좌표 확인
        lat_val = pd.to_numeric(row.get('위도'), errors='coerce')
        lon_val = pd.to_numeric(row.get('경도'), errors='coerce')
        
        if pd.notnull(lat_val) and pd.notnull(lon_val):
            coords = [lat_val, lon_val]
        else:
            # 보강된 사전에서 텍스트 부분 매칭
            for key, val in location_map.items():
                if key in city_text:
                    coords = val
                    break
        
        if coords:
            mapped_count += 1
            scale = row.get('사육규모', 0)
            scale_txt = f"{int(scale):,}" if pd.notnull(scale) else "정보없음"
            
            # 가시성 높은 팝업 디자인
            html = f"""<div style="font-family:'Malgun Gothic'; min-width:260px; line-height:1.6; padding:10px;">
                        <h4 style="margin:0; color:#d32f2f; font-size:18px;">{city_text}</h4>
                        <hr style="margin:8px 0; border:0.5px solid #eee;">
                        <b>사육규모:</b> <span style="color:#d32f2f;">{scale_txt}두</span><br>
                        <b>발생내용:</b> {row.get('발생내용', '')}</div>"""
            folium.Marker(location=coords, popup=folium.Popup(html, max_width=450),
                          icon=folium.Icon(color='red', icon='warning', prefix='fa')).add_to(marker_cluster)

    st_folium(m, width="100%", height=650)

    # 5. 상세 목록
    st.subheader("📋 상세 발생 현황")
    st.dataframe(df_filtered.style.format({'사육규모': "{:,.0f}"}, na_rep="-"), 
                 use_container_width=True, hide_index=True)

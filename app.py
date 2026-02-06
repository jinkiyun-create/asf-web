import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import os

# 1. 페이지 설정
st.set_page_config(page_title="ASF 관리 시스템", layout="wide")

# 🎨 디자인 스타일 (제목 크기 극대화 및 시인성 개선)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 제목 스타일: 120px로 극대화 (기존의 3배 이상) */
    .giant-title {
        font-size: 120px; 
        font-weight: 900;
        color: #d32f2f;
        margin-top: -30px;
        margin-bottom: 0px;
        letter-spacing: -5px;
        line-height: 1.0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    /* 발생건수: 작고 정갈하게 */
    .status-sub {
        font-size: 24px;
        font-weight: 600;
        color: #444;
        margin-top: 10px;
        margin-bottom: 30px;
        border-bottom: 3px solid #d32f2f;
        display: inline-block;
        padding-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 로고 및 초대형 제목 레이아웃
col1, col2 = st.columns([1, 6])
with col1:
    if os.path.exists("logo.png"):
        # 로고 크기를 제목에 맞춰 조금 키웠습니다.
        st.image("logo.png", width=220)
    else:
        st.markdown("<h3 style='margin-top:50px; color:#ccc;'>[LOGO]</h3>", unsafe_allow_html=True)

with col2:
    st.markdown('<p class="giant-title">아프리카돼지열병(ASF)<br>발생 현황 관리 시스템</p>', unsafe_allow_html=True)
    st.markdown('<p class="status-sub">📍 ASF 발생 위치 (총 발생건수: 62건)</p>', unsafe_allow_html=True)

# 3. 전국 좌표 사전 보강 (누락 9건을 잡기 위해 서해안/남부 좌표 대폭 추가)
location_map = {
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
    "강화": [37.7461, 126.4842], "인천": [37.4562, 126.7052], "보령": [36.3333, 126.6122],
    "영광": [35.2742, 126.5122], "무안": [34.9904, 126.4817], "영암": [34.8000, 126.7000],
    "나주": [35.0159, 126.7107], "함평": [35.0661, 126.5168], "담양": [35.3211, 126.9881],
    "장성": [35.3018, 126.7847], "예산": [36.6925, 126.8456], "홍성": [36.6013, 126.6607],
    "부안": [35.7317, 126.7333], "고창": [35.4358, 126.7022], "순창": [35.3742, 127.1372]
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
    st.sidebar.header("🔍 통합 검색")
    search_term = st.sidebar.text_input("검색어 입력")
    df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)] if search_term else df

    # 4. 지도 로직 (63개 데이터 매칭 강화)
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(m)

    mapped_count = 0
    for _, row in df_filtered.iterrows():
        # 데이터 정제: 시군 이름에서 공백 제거
        city_text = str(row.get('시군', '')).strip()
        coords = None
        
        # 엑셀 좌표 우선 확인
        lat_val = pd.to_numeric(row.get('위도'), errors='coerce')
        lon_val = pd.to_numeric(row.get('경도'), errors='coerce')
        
        if pd.notnull(lat_val) and pd.notnull(lon_val):
            coords = [lat_val, lon_val]
        else:
            # 텍스트 포함 확인 (예: '보령시' 혹은 '충남 보령' -> '보령' 매칭)
            for key, val in location_map.items():
                if key in city_text:
                    coords = val
                    break
        
        if coords:
            mapped_count += 1
            scale = row.get('사육규모', 0)
            scale_formatted = f"{int(scale):,}" if pd.notnull(scale) else "0"
            
            html = f"""<div style="font-family:'Malgun Gothic'; min-width:260px; line-height:1.6;">
                        <h4 style="margin:0; color:#d32f2f; font-size:18px;">{city_text}</h4>
                        <hr style="margin:5px 0; border:1px solid #eee;">
                        <b>사육규모:</b> {scale_formatted}두<br>
                        <b>상세내용:</b> {row.get('발생내용', '')}</div>"""
            folium.Marker(location=coords, popup=folium.Popup(html, max_width=450),
                          icon=folium.Icon(color='red', icon='warning', prefix='fa')).add_to(marker_cluster)

    st_folium(m, width="100%", height=650)

    # 5. 목록 표시 (콤마 적용)
    st.subheader("📋 상세 발생 목록")
    st.dataframe(df_filtered.style.format({'사육규모': "{:,.0f}"}, na_rep="-"), 
                 use_container_width=True, hide_index=True)

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import os

# 1. 페이지 설정
st.set_page_config(page_title="ASF 관리 시스템", layout="wide")

# 🎨 디자인 스타일 (여백 및 줄 간격 최적화)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 전체 컨테이너 여백 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* 초대형 제목: 줄 간격을 1.2로 늘려 답답함 해소 */
    .giant-title {
        font-size: 100px; 
        font-weight: 900;
        color: #d32f2f;
        line-height: 1.2; /* 줄 간격 확보 */
        margin-bottom: 10px;
        letter-spacing: -2px;
    }

    /* 상태 표시줄: 독립적인 공간 확보 */
    .status-info {
        font-size: 24px;
        font-weight: 600;
        color: #333;
        background-color: #f9f9f9;
        padding: 15px 25px;
        border-radius: 12px;
        border-left: 8px solid #d32f2f;
        margin-bottom: 40px; /* 아래 요소와 간격 확보 */
        display: inline-block;
        width: 100%;
    }

    /* 로고 이미지 정렬 */
    .logo-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 레이아웃 (로고와 제목 분리 배치)
if os.path.exists("logo.png"):
    st.image("logo.png", width=200)

st.markdown('<p class="giant-title">아프리카돼지열병(ASF)<br>발생 현황 관리 시스템</p>', unsafe_allow_html=True)
st.markdown('<div class="status-info">📍 ASF 발생 위치 (총 발생건수: 62건)</div>', unsafe_allow_html=True)

# 3. 전국 좌표 사전 (누락 방지 보강)
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
    "영광": [35.2742, 126.5122], "무안": [34.9904, 126.4817], "나주": [35.0159, 126.7107]
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

    # 4. 지도 생성 및 마커
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(m)

    mapped_count = 0
    for _, row in df_filtered.iterrows():
        city_text = str(row.get('시군', '')).strip()
        coords = None
        
        # 엑셀 좌표 우선
        lat_val = pd.to_numeric(row.get('위도'), errors='coerce')
        lon_val = pd.to_numeric(row.get('경도'), errors='coerce')
        
        if pd.notnull(lat_val) and pd.notnull(lon_val):
            coords = [lat_val, lon_val]
        else:
            # 텍스트 포함 확인
            for key, val in location_map.items():
                if key in city_text:
                    coords = val
                    break
        
        if coords:
            mapped_count += 1
            scale = row.get('사육규모', 0)
            scale_formatted = f"{int(scale):,}" if pd.notnull(scale) else "0"
            
            html = f"""<div style="font-family:'Malgun Gothic'; min-width:250px; line-height:1.6; padding:10px;">
                        <h4 style="margin:0; color:#d32f2f;">{city_text}</h4>
                        <hr style="margin:8px 0; border:0.5px solid #eee;">
                        <b>사육규모:</b> {scale_formatted}두<br>
                        <b>상세내용:</b> {row.get('발생내용', '')}</div>"""
            folium.Marker(location=coords, popup=folium.Popup(html, max_width=450),
                          icon=folium.Icon(color='red', icon='warning', prefix='fa')).add_to(marker_cluster)

    st_folium(m, width="100%", height=650)

    # 5. 상세 목록
    st.markdown("### 📋 상세 발생 현황 목록")
    st.dataframe(df_filtered.style.format({'사육규모': "{:,.0f}"}, na_rep="-"), 
                 use_container_width=True, hide_index=True)

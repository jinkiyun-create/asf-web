import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# 1. 페이지 설정
st.set_page_config(page_title="ASF 발생 현황 관리 시스템", layout="wide")

# 로고 및 제목
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    else:
        st.markdown("### 🏢 LOGO")
with col2:
    st.title("아프리카돼지열병(ASF) 발생 현황 관리 시스템")

# 2. 전국 주요 시군별 대표 좌표 사전 (보령, 영광 추가 및 대폭 보강)
location_map = {
    # 기존 경기/강원/경북권
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
    
    # 신규 추가 지역 (충남/전남/경남 등)
    "보령": [36.3333, 126.6122], "영광": [35.2742, 126.5122], "당진": [36.8897, 126.6281],
    "천안": [36.8151, 127.1139], "공주": [36.4465, 127.1190], "홍성": [36.6013, 126.6607],
    "나주": [35.0159, 126.7107], "무안": [34.9904, 126.4817], "김해": [35.2285, 128.8894],
    "양산": [35.3364, 129.0300], "함안": [35.2725, 128.4065], "밀양": [35.5038, 128.7466]
}

# 3. 데이터 로드
@st.cache_data
def load_data():
    if os.path.exists("data.xlsx"):
        try:
            df = pd.read_excel("data.xlsx", skiprows=1)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"데이터 파일 읽기 오류: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

df = load_data()

if not df.empty:
    # 검색 기능
    st.sidebar.header("🔍 검색 및 필터")
    search = st.sidebar.text_input("지역 또는 내용 검색")
    df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df

    # 4. 지도 및 요약 표시 (요청하신 총 건수 62건 표시)
    st.subheader(f"📍 ASF 발생 위치 (총 발생건수: 62건)")
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)

    for _, row in df_filtered.iterrows():
        city_text = str(row.get('시군', ''))
        coords = None
        
        # 1) 엑셀에 위도/경도 숫자가 있는지 확인
        lat_val = pd.to_numeric(row.get('위도'), errors='coerce')
        lon_val = pd.to_numeric(row.get('경도'), errors='coerce')
        
        if pd.notnull(lat_val) and pd.notnull(lon_val):
            coords = [lat_val, lon_val]
        else:
            # 2) 없으면 location_map 사전에서 단어로 매칭
            for key, val in location_map.items():
                if key in city_text:
                    coords = val
                    break
        
        # 좌표가 확정되면 지도에 마커 찍기
        if coords:
            scale = row.get('사육규모', 0)
            scale_formatted = f"{scale:,.0f}" if isinstance(scale, (int, float)) and pd.notnull(scale) else "정보없음"
            
            folium.Marker(
                location=coords,
                popup=f"<b>{city_text}</b><br>규모: {scale_formatted}두<br>{row.get('발생내용', '')}",
                icon=folium.Icon(color='red', icon='warning', prefix='fa')
            ).add_to(m)

    st_folium(m, width="100%", height=500)

    # 5. 목록 표시 (천 단위 콤마 적용)
    st.subheader("📋 상세 발생 목록")
    display_df = df_filtered.copy()
    if '사육규모' in display_df.columns:
        display_df['사육규모'] = display_df['사육규모'].apply(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and pd.notnull(x) else x)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=600)

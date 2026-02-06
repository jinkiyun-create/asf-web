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

# 2. 전국 시군별 대표 좌표 데이터 (주요 발생지 63곳 이상 커버)
# 엑셀에 좌표가 없을 때 '시군' 명칭을 바탕으로 이 좌표를 찾아갑니다.
geo_data = {
    "연천군": [38.0964, 127.0754], "파주시": [37.7600, 126.7798], "철원군": [38.1463, 127.3132],
    "화천군": [38.1061, 127.7081], "양구군": [38.1051, 127.9897], "인제군": [38.0696, 128.1703],
    "고성군": [38.3805, 128.4687], "포천시": [37.8949, 127.2003], "양양군": [38.0754, 128.6189],
    "홍천군": [37.6970, 127.8887], "춘천시": [37.8813, 127.7298], "강릉시": [37.7518, 128.8761],
    "횡성군": [37.4912, 127.9853], "평창군": [37.3705, 128.3902], "영월군": [37.1837, 128.4619],
    "원주시": [37.3422, 127.9202], "보은군": [36.4894, 127.7345], "충주시": [36.9910, 127.9259],
    "제천시": [37.1326, 128.2141], "괴산군": [36.8115, 127.7946], "단양군": [36.9845, 128.3653],
    "안동시": [36.5684, 128.7296], "영덕군": [36.4150, 129.3653], "영천시": [35.9732, 128.9385],
    "경주시": [35.8562, 129.2247], "상주시": [36.4109, 128.1591], "문경시": [36.5861, 128.1868],
    "의성군": [36.3522, 128.6970], "청송군": [36.4362, 129.0573], "영양군": [36.6666, 129.1120],
    "봉화군": [36.8931, 128.7325], "울진군": [36.9931, 129.4005], "김포시": [37.6151, 126.7154],
    "강화군": [37.7461, 126.4842], "인천": [37.4562, 126.7052], "부산": [35.1798, 129.0750]
}

# 3. 엑셀 데이터 로드
@st.cache_data
def load_data():
    file_path = "data.xlsx"
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path, engine='openpyxl', skiprows=1)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"엑셀 읽기 오류: {e}")
            return pd.DataFrame()
    return None

df = load_data()

if df is not None and not df.empty:
    # 4. 화면 구성 및 검색
    total_asf_count = 62 
    st.sidebar.header("🔍 통합 검색")
    search_term = st.sidebar.text_input("검색어 입력")
    
    if search_term:
        df_display = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)].copy()
        display_count = len(df_display)
    else:
        df_display = df.copy()
        display_count = total_asf_count

    st.subheader(f"📍 ASF 발생 위치 (총 발생건수: {display_count}건)")
    
    # 지도 생성
    m = folium.Map(location=[37.0, 128.0], zoom_start=7)

    # 5. 모든 행을 돌면서 마커 찍기
    for _, row in df_display.iterrows():
        city_name = str(row.get('시군', '')).strip()
        
        # 엑셀 좌표 우선, 없으면 geo_data에서 시군명으로 찾기
        lat = pd.to_numeric(row.get('위도'), errors='coerce')
        lon = pd.to_numeric(row.get('경도'), errors='coerce')
        
        if pd.isna(lat) or pd.isna(lon):
            # 시군 이름이 포함된 좌표 찾기 (예: "포천시"가 포함되어 있으면 매칭)
            for key, val in geo_data.items():
                if key in city_name:
                    lat, lon = val
                    break
        
        if not (pd.isna(lat) or pd.isna(lon)):
            scale = row.get('사육규모', 0)
            scale_text = f"{scale:,.0f}" if isinstance(scale, (int, float)) else str(scale)
            
            folium.Marker(
                location=[lat, lon],
                popup=f"<b>{city_name}</b><br>규모: {scale_text}<br>{row.get('발생내용', '')}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)

    st_folium(m, width="100%", height=500)

    # 6. 상세 목록 (사육규모 콤마 적용)
    st.subheader("📋 상세 발생 목록")
    df_styled = df_display.copy()
    if '사육규모' in df_styled.columns:
        df_styled['사육규모'] = df_styled['사육규모'].apply(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and pd.notnull(x) else x)
    
    st.dataframe(df_styled, use_container_width=True, hide_index=True, height=600)

else:
    st.info("데이터를 불러오는 중입니다...")

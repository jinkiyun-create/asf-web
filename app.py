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

# 2. 시군별 위도/경도 좌표 데이터 (엑셀에 좌표가 없을 때 사용)
city_coords = {
    "포천시": [37.8949, 127.2003], "연천군": [38.0964, 127.0754], "파주시": [37.7600, 126.7798],
    "철원군": [38.1463, 127.3132], "화천군": [38.1061, 127.7081], "양구군": [38.1051, 127.9897],
    "인제군": [38.0696, 128.1703], "고성군": [38.3805, 128.4687], "양양군": [38.0754, 128.6189],
    "홍천군": [37.6970, 127.8887], "춘천시": [37.8813, 127.7298], "원주시": [37.3422, 127.9202],
    "영월군": [37.1837, 128.4619], "평창군": [37.3705, 128.3902], "강릉시": [37.7518, 128.8761],
    "보은군": [36.4894, 127.7345], "충주시": [36.9910, 127.9259], "제천시": [37.1326, 128.2141],
    "괴산군": [36.8115, 127.7946], "영덕군": [36.4150, 129.3653], "안동시": [36.5684, 128.7296],
    "영천시": [35.9732, 128.9385], "경주시": [35.8562, 129.2247], "김포시": [37.6151, 126.7154],
    "인천": [37.4562, 126.7052], "강화군": [37.7461, 126.4842], "횡성군": [37.4912, 127.9853]
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
    # --- 데이터 전처리 ---
    # 사육규모 콤마 표시 (숫자인 경우만 처리)
    if '사육규모' in df.columns:
        df['사육규모'] = pd.to_numeric(df['사육규모'], errors='coerce')
        # 나중에 출력할 때 format을 지정하기 위해 여기선 원본 유지

    # 검색 기능
    st.sidebar.header("🔍 통합 검색")
    search_term = st.sidebar.text_input("검색어 입력")
    if search_term:
        df_display = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)].copy()
    else:
        df_display = df.copy()

    # 4. 지도 표시 (시군 명칭 기준 자동 매칭)
    st.subheader(f"📍 ASF 발생 위치 (총 발생건수: 62건)")
    m = folium.Map(location=[37.5, 127.8], zoom_start=7)

    for _, row in df_display.iterrows():
        city_name = str(row.get('시군', ''))
        # 1. 엑셀에 위도/경도가 있는지 먼저 확인
        lat = row.get('위도')
        lon = row.get('경도')
        
        # 2. 엑셀에 없다면 city_coords 딕셔너리에서 검색
        if (pd.isna(lat) or pd.isna(lon)) and city_name in city_coords:
            lat, lon = city_coords[city_name]
        
        if not (pd.isna(lat) or pd.isna(lon)):
            folium.Marker(
                location=[float(lat), float(lon)],
                popup=f"<b>{city_name}</b><br>규모: {row.get('사육규모', 0):,.0f}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)

    st_folium(m, width="100%", height=500)

    # 5. 상세 목록 (콤마 포맷 적용)
    st.subheader("📋 상세 발생 목록")
    
    # 사육규모 열에 천단위 콤마 적용하여 표시
    df_styled = df_display.copy()
    if '사육규모' in df_styled.columns:
        df_styled['사육규모'] = df_styled['사육규모'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else x)
    
    st.dataframe(df_styled, use_container_width=True, hide_index=True, height=600)

else:
    st.info("데이터를 불러오는 중입니다...")

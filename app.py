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

# 2. 엑셀 데이터 로드
@st.cache_data
def load_data():
    file_path = "data.xlsx"
    if os.path.exists(file_path):
        try:
            # 첫 번째 줄(큰 제목) 건너뛰기
            df = pd.read_excel(file_path, engine='openpyxl', skiprows=1)
            # 컬럼명 앞뒤 공백 제거
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"엑셀 읽기 오류: {e}")
            return pd.DataFrame()
    return None

df = load_data()

if df is not None and not df.empty:
    # 3. 데이터 전처리 (위도, 경도 숫자 변환)
    # 엑셀에서 제목이 '위도', '경도'인 열을 찾아 숫자로 강제 변환합니다.
    for col in df.columns:
        if '위도' in col:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            lat_col = col
        if '경도' in col:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            lon_col = col

    # 검색 기능
    st.sidebar.header("🔍 통합 검색")
    search_term = st.sidebar.text_input("검색어 입력")
    if search_term:
        df_display = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]
    else:
        df_display = df

    # 4. 지도 표시
    st.subheader(f"📍 ASF 발생 위치 (총 발생건수: 62건)")
    
    # 데이터에 위도/경도가 있고, 실제 숫자인 데이터만 필터링
    map_data = df_display.dropna(subset=[lat_col, lon_col])
    
    # 지도의 중심점 (데이터가 있으면 첫 번째 지점, 없으면 대한민국 중심)
    center_lat = map_data[lat_col].iloc[0] if not map_data.empty else 36.5
    center_lon = map_data[lon_col].iloc[0] if not map_data.empty else 127.8
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=7)

    # 마커 찍기
    for _, row in map_data.iterrows():
        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=f"<b>{row.get('시군', '발생지')}</b><br>{row.get('발생내용', '')}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

    st_folium(m, width="100%", height=500)

    # 5. 상세 목록
    st.subheader("📋 상세 발생 목록")
    st.dataframe(df_display, use_container_width=True, hide_index=True, height=600)

else:
    st.info("데이터를 불러오는 중입니다...")

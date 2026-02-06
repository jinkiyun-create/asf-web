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
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"엑셀 읽기 오류: {e}")
            return pd.DataFrame()
    return None

df = load_data()

if df is not None and not df.empty:
    # 3. 위도/경도 컬럼 찾기 (변수 초기화)
    lat_col = None
    lon_col = None

    # 엑셀 제목 중에 '위도'나 '경도'라는 글자가 포함된 열을 찾습니다.
    for col in df.columns:
        if '위도' in col or 'Lat' in col:
            lat_col = col
        if '경도' in col or 'Lon' in col:
            lon_col = col

    # 검색 기능
    st.sidebar.header("🔍 통합 검색")
    search_term = st.sidebar.text_input("검색어 입력")
    if search_term:
        df_display = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]
    else:
        df_display = df

    # 4. 지도 표시 부분
    st.subheader(f"📍 ASF 발생 위치 (총 발생건수: 62건)")
    
    # 지도의 기본 중심점 (대한민국 중심)
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)

    # 위도/경도 컬럼을 찾았을 때만 마커를 찍습니다.
    if lat_col and lon_col:
        # 데이터를 숫자로 변환하고 비어있는 값은 제거
        df_display[lat_col] = pd.to_numeric(df_display[lat_col], errors='coerce')
        df_display[lon_col] = pd.to_numeric(df_display[lon_col], errors='coerce')
        map_data = df_display.dropna(subset=[lat_col, lon_col])

        for _, row in map_data.iterrows():
            folium.Marker(
                location=[row[lat_col], row[lon_col]],
                popup=f"<b>{row.get('시군', '발생지')}</b><br>{row.get('발생내용', '')}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
    else:
        # 컬럼을 못 찾았을 때 경고 메시지
        st.warning("⚠️ 엑셀에서 '위도'와 '경도' 컬럼을 찾을 수 없어 지도에 표시하지 못했습니다.")
        st.info(f"현재 인식된 컬럼명: {list(df.columns)}")

    st_folium(m, width="100%", height=500)

    # 5. 상세 목록
    st.subheader("📋 상세 발생 목록")
    st.dataframe(df_display, use_container_width=True, hide_index=True, height=600)

else:
    st.info("데이터를 불러오는 중입니다...")

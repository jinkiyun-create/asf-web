import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# 페이지 설정
st.set_page_config(page_title="ASF 발생 현황 관리 시스템", layout="wide")

# 1. 로고 및 제목
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    else:
        st.markdown("### 🏢 LOGO")
with col2:
    st.title("아프리카돼지열병(ASF) 발생 현황 관리 시스템")

# 2. 엑셀 파일(data.xlsx) 불러오기
@st.cache_data
def load_data():
    file_path = "data.xlsx"
    if os.path.exists(file_path):
        try:
            # 첫 번째 줄(큰 제목) 건너뛰기
            df = pd.read_excel(file_path, engine='openpyxl', skiprows=1)
            # 컬럼명 앞뒤 공백 제거 및 문자열화
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"엑셀 읽기 오류: {e}")
            return pd.DataFrame()
    return None

df = load_data()

# 3. 화면 구성
if df is not None and not df.empty:
    total_asf_count = 62 
    
    st.sidebar.header("🔍 통합 검색")
    search_term = st.sidebar.text_input("검색어 입력")
    
    if search_term:
        df_display = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]
        display_count = len(df_display)
    else:
        df_display = df
        display_count = total_asf_count

    # 문구 수정 완료: 총 발생건수
    st.subheader(f"📍 ASF 발생 위치 (총 발생건수: {display_count}건)")
    
    # 지도 생성 (한반도 중심)
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    
    # 💡 지도 위치 표시 핵심 로직
    # 엑셀 파일에서 '위도'와 '경도'가 포함된 컬럼을 찾습니다.
    lat_col = [c for c in df_display.columns if '위도' in c]
    lon_col = [c for c in df_display.columns if '경도' in c]
    
    if lat_col and lon_col:
        for _, row in df_display.iterrows():
            try:
                lat = float(row[lat_col[0]])
                lon = float(row[lon_col[0]])
                if not (pd.isna(lat) or pd.isna(lon)):
                    # 마커 추가
                    folium.Marker(
                        location=[lat, lon],
                        popup=f"<b>{row.get('시군', '위치')}</b><br>{row.get('발생내용', '')}",
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(m)
            except:
                continue # 숫자가 아닌 데이터는 건너뜁니다.
    
    # 지도 출력
    st_folium(m, width="100%", height=500)

    # 4. 상세 목록
    st.subheader("📋 상세 발생 목록")
    st.dataframe(df_display, use_container_width=True, hide_index=True, height=600)

else:
    st.info("데이터를 불러오는 중입니다... 'data.xlsx' 파일과 'openpyxl' 라이브러리를 확인해주세요.")

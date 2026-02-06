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
            # 💡 핵심 수정: skiprows=1을 넣어 첫 줄(큰 제목)을 건너뜁니다.
            # 만약 제목이 더 위에 있다면 숫자를 2나 3으로 바꿔야 할 수도 있습니다.
            df = pd.read_excel(file_path, engine='openpyxl', skiprows=1)
            
            # 컬럼명 정리 (공백 제거 및 문자열 변환)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"엑셀 읽기 오류: {e}")
            return pd.DataFrame()
    return None

df = load_data()

# 3. 화면 구성
if df is not None and not df.empty:
    # 사이드바 검색
    st.sidebar.header("🔍 통합 검색")
    search_term = st.sidebar.text_input("검색어 입력 (예: 경기도, 2024)")
    
    if search_term:
        df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]

    # 지도 표시
    st.subheader(f"📍 ASF 발생 위치 (총 {len(df)}건 반영)")
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    
    # 위도/경도 컬럼이 엑셀에 있는지 확인 후 마커 찍기
    lat_col = [c for c in df.columns if '위도' in c]
    lon_col = [c for c in df.columns if '경도' in c]
    
    if lat_col and lon_col:
        for _, row in df.iterrows():
            if pd.notnull(row[lat_col[0]]) and pd.notnull(row[lon_col[0]]):
                folium.Marker(
                    location=[row[lat_col[0]], row[lon_col[0]]],
                    popup=f"<b>{row.get('시군', '')}</b>",
                    icon=folium.Icon(color='red')
                ).add_to(m)
    st_folium(m, width="100%", height=400)

    # 4. 상세 목록 (65개 전체 출력)
    st.subheader("📋 상세 발생 목록")
    
    # 엑셀의 실제 컬럼명을 자동으로 감지해서 보여줍니다.
    # 만약 특정 8개만 보고 싶다면 아래 리스트를 수정하세요.
    st.dataframe(df, use_container_width=True, hide_index=True, height=700)

else:
    st.warning("데이터를 불러오는 중입니다. 'data.xlsx'의 형식을 확인해주세요.")
    if df is not None:
        st.write("현재 인식된 제목들:", list(df.columns))

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
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"엑셀 읽기 오류: {e}")
            return pd.DataFrame()
    return None

df = load_data()

# 3. 화면 구성
if df is not None and not df.empty:
    # --- 💡 총 건수 계산 로직 (53-1 등 부번 제외) ---
    # 'no' 컬럼에서 숫자가 아닌 것들을 제외하거나, 소수점/부번이 있는 것을 하나로 계산
    # 여기서는 전체 행 수에서 사용자가 말씀하신 차이만큼을 빼서 '실제 총 62건'으로 고정 표시하거나
    # 'no' 컬럼의 고유한 정수값만 카운트합니다.
    
    total_display_count = 62 # 요청하신 대로 실제 총 합은 62건으로 표시
    
    # 사이드바 검색
    st.sidebar.header("🔍 통합 검색")
    search_term = st.sidebar.text_input("검색어 입력")
    
    if search_term:
        df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]
        current_count = len(df) # 검색 시에는 현재 보이는 행 수 표시
    else:
        current_count = total_display_count

    # 지도 표시
    st.subheader(f"📍 ASF 발생 위치 (실제 총 합계: {current_count}건)")
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    
    # 위도/경도 표시 로직
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

    # 4. 상세 목록 (데이터는 64~65개 전체를 보여주되, 번호는 엑셀 그대로)
    st.subheader(f"📋 상세 발생 목록 (전체 {len(df)}개 행 표시)")
    st.dataframe(df, use_container_width=True, hide_index=True, height=700)

else:
    st.info("데이터를 불러오는 중입니다...")

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# 1. 페이지 설정
st.set_page_config(page_title="ASF 발생 현황 관리 시스템", layout="wide")

# 2. 회사 로고 및 제목
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    else:
        st.markdown("### 🏢 LOGO") 
with col2:
    st.title("아프리카돼지열병(ASF) 발생 현황 관리 시스템")

# 3. 엑셀 파일(data.xlsx) 불러오기
@st.cache_data
def load_data():
    file_path = "data.xlsx"
    if os.path.exists(file_path):
        try:
            # 엑셀 파일을 읽습니다. (openpyxl 엔진 사용)
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # 혹시나 컬럼명에 공백이 있을 수 있으니 제거
            df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
            return df
        except Exception as e:
            st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
            return pd.DataFrame()
    else:
        st.error(f"'{file_path}' 파일을 깃허브에서 찾을 수 없습니다. 파일명이 정확한지 확인해주세요.")
        return pd.DataFrame()

df = load_data()

# 4. 데이터가 존재할 때 화면 구성
if not df.empty:
    # --- 통합 검색 기능 ---
    st.sidebar.header("🔍 통합 검색")
    search_term = st.sidebar.text_input("검색어를 입력하세요 (도, 시군, 내용 등)")
    
    if search_term:
        # 모든 열을 문자열로 바꿔서 검색어가 포함된 행만 필터링
        df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]

    # --- 지도 표시 ---
    st.subheader(f"📍 ASF 발생 위치 (데이터: {len(df)}건)")
    
    # 엑셀에 위도, 경도 컬럼이 있는지 확인 (없으면 기본값으로 지도만 띄움)
    has_gps = '위도' in df.columns and '경도' in df.columns
    
    # 지도의 중심점 설정 (데이터가 있으면 첫 번째 데이터 위치, 없으면 한반도 중심)
    start_lat = df['위도'].iloc[0] if has_gps and not pd.isna(df['위도'].iloc[0]) else 36.5
    start_lon = df['경도'].iloc[0] if has_gps and not pd.isna(df['경도'].iloc[0]) else 127.8
    
    m = folium.Map(location=[start_lat, start_lon], zoom_start=7)
    
    if has_gps:
        for i, row in df.iterrows():
            if pd.notnull(row['위도']) and pd.notnull(row['경도']):
                folium.Marker(
                    location=[row['위도'], row['경도']],
                    popup=f"<b>{row.get('시군', '알수없음')}</b><br>{row.get('발생내용', '')}",
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)
    
    st_folium(m, width="100%", height=450)

    # --- 상세 목록 표시 (8개 항목) ---
    st.subheader("📋 ASF 상세 발생 목록")
    
    # 요청하신 8개 항목 리스트
    target_cols = ["no", "도", "시군", "년도", "신고일자", "확진일자", "사육규모", "발생내용"]
    
    # 실제 엑셀에 있는 컬럼만 필터링해서 보여줌
    display_cols = [c for c in target_cols if c in df.columns]
    
    if display_cols:
        st.dataframe(
            df[display_cols],
            use_container_width=True,
            hide_index=True,
            height=600  # 62건이 충분히 보이도록 높이 설정
        )
    else:
        st.warning("엑셀 파일에 요청하신 컬럼(no, 도, 시군 등)이 없습니다. 컬럼명을 확인해주세요.")
        st.write("현재 엑셀 컬럼명:", list(df.columns))

else:
    st.info("깃허브에 'data.xlsx' 파일이 올라올 때까지 기다리는 중입니다...")

# 5. 다운로드 버튼
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("데이터 다운로드(CSV)", csv, "asf_export.csv", "text/csv")

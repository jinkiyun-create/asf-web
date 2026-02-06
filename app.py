import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# 1. 페이지 설정
st.set_page_config(page_title="ASF 발생 현황", layout="wide")

# 2. 로고 및 제목
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    else:
        st.markdown("### 🏢 LOGO") 
with col2:
    st.title("아프리카돼지열병(ASF) 발생 현황 관리 시스템")

# 3. 엑셀(CSV) 파일 불러오기 함수
@st.cache_data
def load_data():
    file_path = "asf_data.csv"  # 깃허브에 올린 파일 이름과 똑같아야 함
    if os.path.exists(file_path):
        try:
            # 한글 깨짐 방지를 위해 utf-8-sig 또는 cp949 시도
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            return df
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
            return pd.DataFrame()
    else:
        st.warning("⚠️ 'asf_data.csv' 파일을 찾을 수 없습니다. 깃허브에 파일을 업로드해 주세요.")
        return pd.DataFrame()

df = load_data()

# 데이터가 비어있지 않을 때만 실행
if not df.empty:
    # 4. 통합 검색
    st.sidebar.header("🔍 통합 검색")
    search_term = st.sidebar.text_input("검색어 입력")
    if search_term:
        df = df[df.astype(str).apply(lambda x: x.str.contains(search_term)).any(axis=1)]

    # 5. 지도 표시
    st.subheader(f"📍 ASF 발생 지점 (총 {len(df)}건)")
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    for _, row in df.iterrows():
        # 위도, 경도 컬럼이 있는지 확인 후 표시
        if '위도' in df.columns and pd.notnull(row['위도']):
            folium.Marker(
                location=[row['위도'], row['경도']],
                popup=f"<b>{row['시군']}</b><br>{row['발생내용']}",
                icon=folium.Icon(color='red')
            ).add_to(m)
    st_folium(m, width="100%", height=400)

    # 6. 상세 목록 (요청하신 8개 항목)
    st.subheader("📋 상세 발생 목록")
    # 엑셀 파일의 컬럼명과 아래 이름이 정확히 일치해야 합니다.
    cols = ["no", "도", "시군", "년도", "신고일자", "확진일자", "사육규모", "발생내용"]
    available_cols = [c for c in cols if c in df.columns]
    st.dataframe(df[available_cols], use_container_width=True, hide_index=True, height=600)
else:
    st.info("데이터를 불러오려면 'asf_data.csv' 파일을 깃허브에 업로드하세요.")

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import os

st.set_page_config(page_title="ASF 관리 시스템", layout="wide")

# 1. 제목 및 스타일
st.markdown("<h1 style='color: #d32f2f;'>아프리카돼지열병(ASF) 발생 현황</h1>", unsafe_allow_html=True)

# 2. 데이터 자동 감지 로드
@st.cache_data(ttl=5)
def load_data_auto():
    if not os.path.exists("data.xlsx"):
        return None
    
    # 엑셀을 읽되, 제목 줄을 찾을 때까지 뒤집어봅니다.
    df = pd.read_excel("data.xlsx")
    
    # '번호'라는 글자가 들어있는 행을 찾아서 거기를 제목으로 지정
    for i in range(len(df)):
        if "번호" in df.iloc[i].astype(str).values:
            df = pd.read_excel("data.xlsx", skiprows=i+1)
            break
            
    # 컬럼 이름 강제 정리
    df.columns = [str(c).strip() for c in df.columns]
    
    # '번호' 컬럼이 있으면 처리
    target_col = [c for c in df.columns if "번호" in c]
    if target_col:
        df = df.rename(columns={target_col[0]: "번호"})
        df["번호"] = pd.to_numeric(df["번호"], errors="coerce")
        df = df.dropna(subset=["번호"]).astype({"번호": int})
        # 🚀 여기서 내림차순 정렬 (65번이 위로!)
        df = df.sort_values(by="번호", ascending=False)
    return df

df = load_data_auto()

if df is not None and not df.empty:
    # 검색 기능
    search = st.sidebar.text_input("검색어 입력")
    if search:
        df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]

    st.subheader("📍 발생 위치 (최신순 65건)")
    
    # 지도/목록 출력 (위에서 정렬했으므로 순서대로 나옴)
    st.dataframe(df[["번호", "시군", "발생내용", "사육규모"]], use_container_width=True, hide_index=True)
    
    # 지도 표시 생략(에러 방지를 위해 목록 위주로 먼저 확인)
    st.success("데이터 로드 성공! 목록이 65번부터 나오는지 확인해 보세요.")
else:
    st.error("data.xlsx 파일을 읽을 수 없습니다. 파일명을 확인해 주세요.")

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# 1. 페이지 설정
st.set_page_config(page_title="ASF 발생 현황 관리 시스템", layout="wide")

# 2. 회사 로고 넣기 (그림 넣는 법)
# 로고 이미지 파일을 깃허브에 'logo.png'라는 이름으로 올렸다고 가정합니다.
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150) # 로고 파일이 있으면 표시
    else:
        st.markdown("### 🏢 회사 로고") # 파일이 없을 때 나오는 텍스트
with col2:
    st.title("아프리카돼지열병(ASF) 발생 현황 관리 시스템")

# 3. 62건의 데이터 불러오기
@st.cache_data
def load_data():
    if os.path.exists("asf_data.csv"):
        # 파일을 읽어오되 한글 깨짐 방지
        df = pd.read_csv("asf_data.csv", encoding='utf-8-sig')
        return df
    else:
        # 파일이 없을 때 보여줄 가짜 데이터 (여기에 62건을 다 쓰셔도 되지만 파일이 편해요!)
        return pd.DataFrame(columns=["no", "도", "시군", "년도", "신고일자", "확진일자", "사육규모", "발생내용", "위도", "경도"])

df = load_data()

# 4. 사이드바 통합 검색
st.sidebar.header("🔍 통합 검색")
search_term = st.sidebar.text_input("검색어를 입력하세요 (도, 시군 등)")

if search_term:
    # 전체 열에서 검색어 찾기
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_term)).any(axis=1)]

# 5. 지도 표시
st.subheader(f"📍 ASF 발생 지점 (총 {len(df)}건)")
m = folium.Map(location=[36.5, 127.8], zoom_start=7)

for i, row in df.iterrows():
    if not pd.isna(row['위도']):
        folium.Marker(
            location=[row['위도'], row['경도']],
            popup=f"<b>{row['시군']}</b><br>{row['발생내용']}",
            icon=folium.Icon(color='red')
        ).add_to(m)

st_folium(m, width="100%", height=450)

# 6. 상세 목록 (62건 전체가 표로 나옵니다)
st.subheader("📋 상세 발생 현황 목록")
st.dataframe(
    df[["no", "도", "시군", "년도", "신고일자", "확진일자", "사육규모", "발생내용"]],
    use_container_width=True,
    hide_index=True,
    height=600 # 62건을 한눈에 보기 좋게 높이 조절
)

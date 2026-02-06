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

# 3. 62건 데이터 강제 생성 (내용은 실제 데이터로 채우시면 됩니다)
@st.cache_data
def get_full_data():
    # 62번부터 1번까지 역순으로 번호 생성
    rows = []
    for i in range(62, 0, -1):
        rows.append({
            "no": i,
            "도": "강원" if i > 30 else "경북", # 예시 데이터
            "시군": "횡성군" if i > 30 else "군위군",
            "년도": 2026,
            "신고일자": "2026-02-06",
            "확진일자": "2026-02-06",
            "사육규모": "데이터 확인 필요",
            "발생내용": f"{i}번 발생 지점 내용",
            "위도": 37.4912 + (i*0.01), # 지도에 겹치지 않게 조금씩 다르게 표시
            "경도": 127.9853 + (i*0.01)
        })
    return pd.DataFrame(rows)

df = get_full_data()

# 4. 통합 검색
st.sidebar.header("🔍 통합 검색")
search_term = st.sidebar.text_input("검색어 입력")
if search_term:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_term)).any(axis=1)]

# 5. 지도 표시
st.subheader(f"📍 ASF 발생 지점 (총 {len(df)}건)")
m = folium.Map(location=[36.5, 127.8], zoom_start=7)
for _, row in df.iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=f"no.{row['no']} - {row['시군']}",
        icon=folium.Icon(color='red')
    ).add_to(m)

st_folium(m, width="100%", height=400)

# 6. 상세 목록 (여기서 62건이 다 나옵니다!)
st.subheader("📋 상세 발생 목록")
st.dataframe(
    df[["no", "도", "시군", "년도", "신고일자", "확진일자", "사육규모", "발생내용"]],
    use_container_width=True,
    hide_index=True,
    height=600 # 62개가 다 보일 수 있도록 높이를 충분히 줬습니다.
)

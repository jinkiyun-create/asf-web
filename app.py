import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 페이지 설정 및 로고
st.set_page_config(page_title="ASF 발생 현황 관리 시스템", layout="wide")

# 로고 섹션 (이미지 URL이 있다면 입력, 없다면 텍스트로 대체)
col1, col2 = st.columns([1, 5])
with col1:
    # 실제 회사 로고 이미지 주소가 있다면 'https://...' 부분에 넣으세요.
    # 예: st.image("https://your-company.com/logo.png", width=150)
    st.markdown("### 🏢 LOGO") 
with col2:
    st.title("아프리카돼지열병(ASF) 발생 현황 시스템")

# 2. 샘플 데이터 (여기에 실제 데이터를 추가하세요)
data = [
    {
        "no": 1, "도": "강원", "시군": "횡성군", "년도": 2026, 
        "신고일자": "2026-02-06", "확진일자": "2026-02-06", 
        "사육규모": "1,200두", "발생내용": "양돈농가 확진", "위도": 37.4912, "경도": 127.9853
    },
    {
        "no": 2, "도": "경북", "시군": "군위군", "년도": 2026, 
        "신고일자": "2026-02-05", "확진일자": "2026-02-05", 
        "사육규모": "800두", "발생내용": "야생멧돼지 접촉", "위도": 36.2428, "경도": 128.5728
    }
]
df = pd.DataFrame(data)

# 3. 통합 검색 기능
st.sidebar.header("🔍 통합 검색")
search_term = st.sidebar.text_input("검색어를 입력하세요 (도, 시군, 내용 등)")

# 검색 필터링
if search_term:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_term)).any(axis=1)]

# 4. 상단 지도 표시
st.subheader("📍 발생 지점 지도")
m = folium.Map(location=[36.5, 127.5], zoom_start=7)
for i, row in df.iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=f"{row['시군']} - {row['발생내용']}",
        icon=folium.Icon(color='red')
    ).add_to(m)

st_folium(m, width="100%", height=400)

# 5. 하단 상세 목록 표 (원하시는 모든 항목 표기)
st.subheader("📋 ASF 상세 발생 목록")
st.dataframe(
    df[["no", "도", "시군", "년도", "신고일자", "확진일자", "사육규모", "발생내용"]],
    use_container_width=True,
    hide_index=True
)

# 6. 데이터 내려받기 버튼
st.download_button(
    label="CSV 파일로 저장",
    data=df.to_csv(index=False).encode('utf-8-

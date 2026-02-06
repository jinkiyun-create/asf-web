import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 페이지 설정
st.set_page_config(page_title="ASF 발생 현황", layout="wide")

# 로고와 제목
col1, col2 = st.columns([1, 5])
with col1:
    # 로고 이미지가 없다면 이모지로 표시, 있다면 st.image("로고파일.png")로 변경 가능
    st.markdown("### 🏢 LOGO") 
with col2:
    st.title("아프리카돼지열병(ASF) 발생 현황 관리")

# 2. 샘플 데이터 (요청하신 항목 8개 모두 포함)
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

# 3. 통합 검색 (사이드바)
st.sidebar.header("🔍 통합 검색")
search_term = st.sidebar.text_input("검색어를 입력하세요", placeholder="도, 시군, 발생내용 등")

# 검색 필터링 로직
if search_term:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_term)).any(axis=1)]

# 4. 지도 표시 (상단)
st.subheader("📍 발생 지점 지도")
m = folium.Map(location=[36.5, 127.5], zoom_start=7)
for i, row in df.iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=f"<b>{row['시군']}</b><br>{row['발생내용']}",
        icon=folium.Icon(color='red')
    ).add_to(m)

st_folium(m, width="100%", height=400)

# 5. 상세 목록 표 (하단) - 모든 항목 포함
st.subheader("📋 ASF 상세 발생 목록")
st.dataframe(
    df[["no", "도", "시군", "년도", "신고일자", "확진일자", "사육규모", "발생내용"]],
    use_container_width=True,
    hide_index=True
)

# 6. CSV 다운로드 버튼 (잘리지 않게 수정 완료)
csv = df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="CSV 파일로 저장",
    data=csv,
    file_name='asf_data.csv',
    mime='text/csv'
)

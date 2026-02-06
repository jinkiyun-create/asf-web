import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 페이지 설정
st.set_page_config(page_title="ASF 발생 현황", layout="wide")

# 로고와 제목
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("### 🏢 LOGO") 
with col2:
    st.title("아프리카돼지열병(ASF) 발생 현황 관리")

# 2. 데이터 불러오기 (62개 목록이 담긴 CSV 파일 읽기)
@st.cache_data
def load_data():
    # 파일이 깃허브에 업로드되어 있어야 합니다.
    try:
        df = pd.read_csv("asf_data.csv")
        return df
    except:
        # 파일이 없을 경우를 대비한 빈 데이터프레임
        return pd.DataFrame(columns=["no", "도", "시군", "년도", "신고일자", "확진일자", "사육규모", "발생내용", "위도", "경도"])

df = load_data()

# 3. 통합 검색 (사이드바)
st.sidebar.header("🔍 통합 검색")
search_term = st.sidebar.text_input("검색어를 입력하세요", placeholder="도, 시군, 발생내용 등")

if search_term:
    df = df[df.astype(str).apply(lambda x: x.str.contains(search_term)).any(axis=1)]

# 4. 지도 표시 (상단)
st.subheader(f"📍 발생 지점 지도 (총 {len(df)}건)")
m = folium.Map(location=[36.5, 127.5], zoom_start=7)

for i, row in df.iterrows():
    if pd.notnull(row['위도']) and pd.notnull(row['경도']):
        folium.Marker(
            location=[row['위도'], row['경도']],
            popup=f"<b>{row['시군']}</b><br>{row['발생내용']}",
            icon=folium.Icon(color='red')
        ).add_to(m)

st_folium(m, width="100%", height=450)

# 5. 상세 목록 표 (하단) - 62개 전체 출력
st.subheader("📋 ASF 상세 발생 목록")
st.dataframe(
    df[["no", "도", "시군", "년도", "신고일자", "확진일자", "사육규모", "발생내용"]],
    use_container_width=True,
    hide_index=True,
    height=500 # 표 높이를 조절하여 62개가 잘 보이게 함
)

# 6. CSV 다운로드 버튼
csv = df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="전체 데이터 CSV 저장",
    data=csv,
    file_name='asf_full_data.csv',
    mime='text/csv'
)

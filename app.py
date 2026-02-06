import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(page_title="ASF 지도", layout="wide")

st.title("🐗 ASF 발생 현황 지도 (실시간)")

# 1. 데이터 준비 (오류 방지를 위한 기본 샘플 데이터)
data = {
    '장소': ['포천', '연천', '철원', '화천'],
    '위도': [37.8949, 38.1021, 38.1467, 38.1062],
    '경도': [127.2003, 127.0754, 127.3134, 127.7083]
}
df = pd.DataFrame(data)

# 2. 지도 만들기
m = folium.Map(location=[38.1, 127.3], zoom_start=9)

# 지도에 점 찍기
for i, row in df.iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=row['장소'],
        icon=folium.Icon(color='red')
    ).add_to(m)

# 3. 지도 화면에 뿌리기
st_folium(m, width=800, height=500)

# 4. 표 보여주기
st.write("### 발생 상세 목록", df)

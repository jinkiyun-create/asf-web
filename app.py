import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 페이지 설정 (웹 타이틀)
st.set_page_config(page_title="ASF 현황 대시보드", layout="wide")

st.title("🐗 아프리카돼지열병(ASF) 발생 현황 지도")
st.write("실시간 데이터를 지도로 확인하세요.")

# 2. 데이터 불러오기 (예시 데이터 - 실제 파일 경로에 맞게 수정 가능)
# 본인의 CSV 파일 이름이 'data.csv'라면 아래 주석을 해제하고 쓰세요.
# df = pd.read_csv('data.csv')

# 임시 테스트용 데이터 (위도, 경도 포함)
data = {
    '장소': ['포천', '연천', '철원'],
    '위도': [37.8949, 38.1021, 38.1467],
    '경도': [127.2003, 127.0754, 127.3134]
}
df = pd.DataFrame(data)

# 3. 지도 생성
m = folium.Map(location=[38.0, 127.2], zoom_start=9)

# 지도에 마커 추가
for i, row in df.iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=row['장소'],
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

# 4. 스트림릿에 지도 표시
st_folium(m, width=1000, height=600)

# 5. 데이터 표 표시
st.subheader("발생 상세 데이터")
st.dataframe(df)

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import os

# 1. 페이지 설정
st.set_page_config(page_title="ASF 발생 현황 관리 시스템", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 35px; font-weight: 800; color: #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">아프리카돼지열병(ASF) 발생 현황 관리 시스템</p>', unsafe_allow_html=True)

# 2. 좌표 사전
location_map = {
    "연다산동": [37.7402, 126.7481], "백학면": [37.9625, 126.9112], "통진읍": [37.6865, 126.5912],
    "적성면": [38.0035, 126.9234], "송해면": [37.7852, 126.4746], "불은면": [37.6961, 126.5055],
    "삼산면": [37.6841, 126.3312], "강화읍": [37.7461, 126.4842], "하점면": [37.7944, 126.4252],
    "파평면": [37.9304, 126.8521], "문산읍": [37.8542, 126.7885], "신서면": [38.2215, 127.1082],
    "하성면": [37.7112, 126.6341], "월곶면": [37.7011, 126.5412], "미산면": [37.9812, 126.9854],
    "상서면": [38.1631, 127.6321], "동송읍": [38.2062, 127.2215], "관인면": [38.1158, 127.2452],
    "영중면": [37.9942, 127.2512], "창수면": [38.0055, 127.1654], "갈말읍": [38.1462, 127.3465],
    "남면": [37.8561, 126.9912], "주천면": [37.2712, 128.2715], "간성읍": [38.3712, 128.4612],
    "인제읍": [38.0696, 128.1703], "내촌면": [37.8212, 128.1412], "화촌면": [37.7412, 127.9612],
    "국토정중앙면": [38.1051, 127.9897], "동산면": [37.7912, 127.7812], "손양면": [38.0412, 128.6412],
    "남양읍": [37.2084, 126.8177], "봉황면": [34.9315, 126.7958]
}

# 3. 데이터 로드 (순서 기반 강제 이름 지정)
@st.cache_data(ttl=2)
def load_data():
    if os.path.exists("data.xlsx"):
        # 1단계: 일단 엑셀을 헤더 없이 읽어서 실제 데이터 시작점을 찾습니다.
        try:
            df = pd.read_excel("data.xlsx", skiprows=1) # 대부분의 양식이 2행부터 제목임
            
            # 컬럼명이 이상하게 읽혔을 경우를 대비해 첫 4개 컬럼 강제 명명
            original_cols = df.columns.tolist()
            new_names = {original_cols[0]: '번호', original_cols[1]: '시군', 
                         original_cols[2]: '발생내용', original_cols[3]: '사육규모'}
            df = df.rename(columns=new_names)

            # '번호' 열을 숫자로 변환 (NaN 제거)
            df['번호'] = pd.to_numeric(df['번호'], errors='coerce')
            df = df.dropna(subset=['번호'])
            df['번호'] = df['번호'].astype(int)

            # 🚀 여기서 내림차순 정렬 (65번이 위로!)
            df = df.sort_values(by='번호', ascending=False)
            return df
        except Exception as e:
            st.error(f"데이터 처리 중 오류 발생: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

df = load_data()

# 4. 화면 구성
if not df.empty:
    st.sidebar.header("🔍 검색")
    search = st.sidebar.text_input("지역/내용 검색")
    
    if search:
        df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
    else:
        df_filtered = df.copy()

    st.subheader("📍 ASF 발생 위치 (총 발생건수: 65건)")
    
    # 지도 생성
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df_filtered.iterrows():
        try:
            num = int(row['번호'])
            city = str(row['시군'])
            coords = None
            
            # 시군 이름으로 좌표 매핑
            for key, val in location_map.items():
                if key in city:
                    coords = val
                    break
            
            if coords:
                pop_html = f"<b>{num}번 발생</b><br>지역: {city}<br>내용: {row['발생내용']}"
                folium.Marker(coords, popup=folium.Popup(pop_html, max_width=200), 
                              icon=folium.Icon(color='red')).add_to(marker_cluster)
        except:
            continue

    st_folium(m, width="100%", height=550)

    # 5. 목록 표시 (무조건 번호 내림차순)
    st.subheader("📋 상세 발생 목록 (최신순)")
    
    # 표시용 데이터 정리 (번호, 시군, 발생내용, 사육규모만 추출)
    final_list = df_filtered[['번호', '시군', '발생내용', '사육규모']].copy()
    
    # 다시 한번 확실하게 정렬
    final_list = final_list.sort_values(by='번호', ascending=False)
    
    # 사육규모 콤마 포맷
    final_list['사육규모'] = final_list['사육규모'].apply(
        lambda x: f"{int(x):,}" if pd.notnull(x) and isinstance(x, (int, float)) else x
    )
    
    st.dataframe(final_list, use_container_width=True, hide_index=True)

else:
    st.warning("data.xlsx 파일을 찾을 수 없거나 데이터 형식이 맞지 않습니다.")

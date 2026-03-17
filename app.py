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
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main-title {
        font-size: 40px !important;
        font-weight: 800;
        color: #d32f2f;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

# 🏢 로고 및 제목
col1, col2 = st.columns([1, 6])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=180)
    else:
        st.markdown("<h3 style='margin-top:30px;'>🏢 LOGO</h3>", unsafe_allow_html=True)
with col2:
    st.markdown('<p class="main-title">아프리카돼지열병(ASF) 발생 현황 관리 시스템</p>', unsafe_allow_html=True)

# 2. 좌표 사전 (번호를 포함하여 중복 오류 방지)
location_map = {
    "연다산동_1": [37.7402, 126.7481], "백학면_2": [37.9625, 126.9112], "통진읍_3": [37.6865, 126.5912],
    "적성읍_4": [38.0035, 126.9234], "송해면_5": [37.7852, 126.4746], "불은면_6": [37.6961, 126.5055],
    "삼산면_7": [37.6841, 126.3312], "강화읍_8": [37.7461, 126.4842], "하점면_9": [37.7944, 126.4252],
    "파평면_10": [37.9304, 126.8521], "적성면_11": [38.0035, 126.9234], "문산읍_12": [37.8542, 126.7885],
    "통진읍_13": [37.6865, 126.5912], "신서면_14": [38.2215, 127.1082], "상서면_15": [38.1631, 127.6321],
    "상서면_16": [38.1631, 127.6321], "간성읍_17": [38.3712, 128.4612], "간성읍_18": [38.3712, 128.4612],
    "인제읍_19": [38.0696, 128.1703], "내촌면_20": [37.8212, 128.1412], "남면_21": [38.0696, 128.1703],
    "화촌면_22": [37.7412, 127.9612], "국토정중앙면_23": [38.1051, 127.9897], "동산면_24": [37.7912, 127.7812],
    "동산면_25": [37.7912, 127.7812], "하성면_26": [37.7112, 126.6341], "문산읍_27": [37.8542, 126.7885],
    "동송읍_28": [38.2062, 127.2215], "관인면_29": [38.1158, 127.2452], "동송읍_30": [38.2062, 127.2215],
    "통진읍_31": [37.6865, 126.5912], "손양면_32": [38.0412, 128.6412], "영중면_33": [37.9942, 127.2512],
    "창수면_34": [38.0055, 127.1654], "영중면_35": [37.9942, 127.2512], "창수면_36": [38.0055, 127.1654],
    "갈말읍_37": [38.1462, 127.3465], "하남면_38": [38.0612, 127.6741], "축산면_39": [36.5012, 129.4112],
    "적성면_40": [38.0035, 126.9234], "갈말읍_41": [38.1462, 127.3465], "화남면_42": [36.0512, 128.9512],
    "남선면_43": [36.5212, 128.7912], "효자면_44": [36.8012, 128.3712], "화남면_45": [36.0512, 128.9512],
    "월곶면_46": [37.7011, 126.5412], "사내면_47": [38.0712, 127.5231], "남면_48": [37.8561, 126.9912],
    "남면_49": [37.8561, 126.9912], "남면_50": [37.8561, 126.9912], "은현면_51": [37.8712, 127.0212],
    "남면_52": [37.8561, 126.9912], "파평면_53": [37.9304, 126.8521], "파평면_53-1": [37.9304, 126.8521],
    "미산면_54": [37.9812, 126.9854], "송산면_55": [36.9512, 126.6812], "강동면_56": [37.7212, 128.9812],
    "미양면_57": [36.9312, 127.2412], "관인면_58": [38.1158, 127.2452], "홍농읍_59": [35.3912, 126.4412],
    "성송면_60": [35.3512, 126.6512], "청소면_61": [36.4312, 126.5812], "대합면_62": [35.6112, 128.5112],
    "관인면_63": [38.1158, 127.2452], "남양읍_64": [37.2084, 126.8177], "봉황면_65": [34.9315, 126.7958],
    "순성면_66": [36.8531, 126.6854], "덕천면_67": [35.6133, 126.8144], "구성면_68": [36.0592, 128.0581],
    "은하면_69": [36.5273, 126.5915], "창녕읍_70": [35.5412, 128.5007], "장안면_71": [37.0792, 126.8114],
    "오성면_72": [37.0012, 126.9315], "오성면_72-1": [37.0012, 126.9315], "서면_73": [38.2259, 127.4294],
    "서면_73-1": [38.2259, 127.4294], "함경면_74": [35.0934, 126.3151], "부림면_75": [35.5186, 128.3241],
    "가야면_76": [35.7954, 128.1408], "군남면_77": [37.9575, 127.0267], "단성면_78": [35.3115, 127.9463],
    "신광면_79": [35.1385, 126.4952]
}

# 3. 데이터 로드 및 전처리
@st.cache_data(ttl=10)
def load_data():
    if os.path.exists("data.xlsx"):
        # 엑셀의 헤더 위치에 따라 skiprows를 0 또는 1로 조정해 보세요.
        df = pd.read_excel("data.xlsx", skiprows=1)
        
        # 컬럼 이름의 공백을 제거하고 표준화
        df.columns = [str(c).strip() for c in df.columns]
        
        # 팝업에서 깨지지 않도록 컬럼명 강제 재정의 (순서대로 1~5번째 컬럼)
        # 만약 엑셀 컬럼 순서가 [번호, 시군, 발생내용, 사육규모...] 라면 아래가 정확히 작동합니다.
        # df.columns.values[0] = "번호" 
        
        # 데이터 정제: '번호'가 있는 행만 사용
        if '번호' in df.columns:
            df = df.dropna(subset=['번호'])
            df['번호'] = pd.to_numeric(df['번호'], errors='coerce').fillna(0).astype(int)
            df = df[df['번호'] > 0].sort_values(by='번호')
        return df
    return pd.DataFrame()

df = load_data()

# 4. 필터링 및 지도
if not df.empty:
    st.sidebar.header("🔍 검색 및 필터")
    search = st.sidebar.text_input("지역 또는 내용 검색")
    df_filtered = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df

    st.subheader("📍 ASF 발생 위치 (총 발생건수: 79건)")
    
    m = folium.Map(location=[36.5, 127.8], zoom_start=7)
    marker_cluster = MarkerCluster(spiderfy_on_max_zoom=True).add_to(m)

    for _, row in df_filtered.iterrows():
        # 데이터 추출 (컬럼명이 일치하지 않을 경우를 대비해 순서로 가져오는 방법 병행)
        num = row.get('번호') if pd.notnull(row.get('번호')) else _ + 1
        city_text = str(row.get('시군', '정보없음'))
        content = str(row.get('발생내용', '내용 없음'))
        scale = str(row.get('사육규모', '-'))

        coords = None
        lat_ex = pd.to_numeric(row.get('위도'), errors='coerce')
        lon_ex = pd.to_numeric(row.get('경도'), errors='coerce')
        
        if pd.notnull(lat_ex) and pd.notnull(lon_ex):
            coords = [lat_ex, lon_ex]
        else:
            for key, val in location_map.items():
                if key in city_text:
                    coords = val
                    break
        
        if coords:
            # 팝업 HTML (변수를 확실하게 매핑)
            popup_html = f"""
            <div style="width:200px; font-family: 'Malgun Gothic', sans-serif;">
                <h4 style="margin:0; color:#d32f2f;">{int(num)}번 발생</h4>
                <hr style="margin:5px 0;">
                <p style="margin:2px 0;"><b>📍 지역:</b> {city_text}</p>
                <p style="margin:2px 0;"><b>🐷 규모:</b> {scale}</p>
                <p style="margin:2px 0;"><b>📝 내용:</b> {content}</p>
            </div>
            """
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='red', icon='warning', prefix='fa')
            ).add_to(marker_cluster)

    st_folium(m, width="100%", height=600)

    # 5. 목록 표시
    st.subheader("📋 상세 발생 목록")
    display_df = df_filtered.copy()
    display_df = display_df.drop(columns=['위도', '경도'], errors='ignore')
    
    if '사육규모' in display_df.columns:
        display_df['사육규모'] = display_df['사육규모'].apply(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.warning("데이터가 없습니다. 엑셀 파일의 컬럼명이 '번호', '시군'으로 시작하는지 확인해 주세요.")














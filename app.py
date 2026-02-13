for _, row in df_filtered.iterrows():
        # 1. 'no' 또는 'No' 컬럼에서 번호 추출 (대소문자 무관하게 탐색)
        # 만약 'no' 컬럼이 없으면 '번호'를 찾고, 그것도 없으면 기본 인덱스 사용
        num_val = row.get('no') if pd.notnull(row.get('no')) else row.get('No')
        
        if pd.isnull(num_val):
            num_val = row.get('번호', _ + 1) # 'no'가 없을 때의 대비책
        
        # 2. 번호 출력 형식 정리 (소수점 제거)
        try:
            display_num = int(float(num_val))
        except:
            display_num = num_val

        city_text = str(row.get('시군', '정보없음'))
        content = str(row.get('발생내용', '내용 없음'))
        scale = str(row.get('사육규모', '-'))

        # 좌표 설정 로직 (기존과 동일)
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
            # 팝업 HTML (display_num 반영)
            popup_html = f"""
            <div style="width:200px; font-family: 'Malgun Gothic', sans-serif;">
                <h4 style="margin:0; color:#d32f2f;">{display_num}번 발생</h4>
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

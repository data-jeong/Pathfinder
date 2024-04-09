import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from streamlit_option_menu import option_menu

# 메인 앱 설정
st.set_page_config(layout="wide")

road_map = pd.read_csv('2024-04-09_roadmap.csv')

# 멀티페이지 구조 설정
with st.sidebar:
    selected = option_menu("Main Categories", list(road_map['main_category'].unique()), icons=['house', 'book', 'search', 'list'])

# 선택된 카테고리에 따라 페이지 내용을 동적으로 변경
if selected:
    st.title(f'{selected} Development Roadmaps')

    # 검색 기능
    search_query = st.text_input("Search for a roadmap:", "")

    # 선택된 카테고리의 데이터 필터링
    filtered_df = road_map[(road_map['main_category'] == selected) & (road_map['title'].str.contains(search_query, case=False))]

    # 'study_order' 열에 따라 데이터프레임 정렬
    filtered_df = filtered_df.sort_values(by='study_order', ascending=True)
    
    # 하이퍼링크가 포함된 테이블을 Markdown으로 생성하여 표시
    for index, row in filtered_df.iterrows():
        # 각 로우에 대한 하이퍼링크 문자열 생성
        markdown_link = f"[{row['title']}]({row['url']})({row['study_order']})"
        st.markdown(markdown_link, unsafe_allow_html=True)

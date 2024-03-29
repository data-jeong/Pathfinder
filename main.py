import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from streamlit_option_menu import option_menu

# 웹사이트 데이터를 한 번만 불러오기 위해 st.cache 데코레이터 사용
@st.cache_data()
def load_data(url):
    data = requests.get(url)
    soup = BeautifulSoup(data.text, 'html.parser')
    target_list = soup.select('body > div.flex.bg-gray-100.pt-4.pb-14.sm\:pt-8.sm\:pb-16 > div > div > a')

    title_list = []
    href_list = [] 

    for i in target_list:
        title_list.append(i.text.strip().replace('\nNew', '').strip())
        href_list.append(i.get('href'))

    road_map = pd.DataFrame({
        'title': title_list,
        'url': [url + href.replace('/roadmaps', '') for href in href_list]
    })

    return road_map

def remove_duplicates(roadmap):
    seen_titles = set()
    clean_roadmap = {}

    for category, topics in roadmap.items():
        clean_topics = {}
        for title, order in topics.items():
            if title not in seen_titles:
                seen_titles.add(title)
                clean_topics[title] = order
        clean_roadmap[category] = clean_topics
    
    return clean_roadmap

# 메인 앱 설정
st.set_page_config(layout="wide")

# Roadmaps 데이터 로드
url = 'https://roadmap.sh/roadmaps'
road_map = load_data(url)

# 정리된 로드맵 데이터 구조
# 정리된 로드맵 데이터 구조
roadmap_revised = {
    "AI": {
        "Python Developer": 1,
        "Data Structures & Algorithms Roadmap": 2,
        "AI and Data Scientist Roadmap": 3,
        "MLOps Roadmap": 4
    },
    "BACKEND": {
        "SQL Roadmap": 1,
        "PostgreSQL DBA": 2,
        "Python Developer": 3,
        "Java Developer": 4,
        "Node.js Developer": 5,
        "System Design": 6,
        "Backend Developer": 7,
        "ASP.NET Core Developer": 8,
        "Spring Boot Developer": 9,
        "C++ Developer Roadmap": 10,
        "Go Developer": 11,
        "Rust Developer": 12,
        "GraphQL": 13,
        "Software Design and Architecture": 14
    },
    "FRONT": {
        "JavaScript Roadmap": 1,
        "HTML/CSS": 2,  # Added for completeness
        "React Developer": 3,
        "Angular Developer": 4,
        "Vue Developer": 5,
        "TypeScript": 6,
        "Frontend Developer": 7,
        "UX Design": 8,
        "Design System": 9
    },
    "APP": {
        "Android Developer": 1,
        "React Native Developer": 2,
        "Flutter Developer": 3
    },
    "EXT": {
        "Computer Science": 1,  # Added as a foundational knowledge base
        "DevOps Roadmap": 2,
        "AWS Roadmap": 3,
        "Docker Roadmap": 4,
        "Kubernetes Roadmap": 5,
        "Full Stack Developer": 6,
        "Cyber Security Expert": 7,
        "Blockchain Developer": 8,
        "QA Engineer": 9,
        "Game Developer": 10,
        "Server Side Game Developer": 11,
        "Technical Writer": 12,
        "Software Architect": 13,
        "MongoDB Roadmap": 14,
        "Prompt Engineering Roadmap": 15
    }
}

roadmap_no_duplicates = remove_duplicates(roadmap_revised)

# 중복 제거 로직 적용 및 학습 순서 및 메인 카테고리 할당
road_map['main_category'] = ''
road_map['study_order'] = ''

for main_category, sub_category in roadmap_no_duplicates.items():
    for sub_category_real, rank in sub_category.items():
        road_map.loc[road_map['title'].str.contains(sub_category_real,  regex=False), 'main_category'] = main_category
        road_map.loc[road_map['title'].str.contains(sub_category_real,  regex=False), 'study_order'] = rank

# 멀티페이지 구조 설정
with st.sidebar:
    selected = option_menu("Main Categories", list(roadmap_no_duplicates.keys()), icons=['house', 'book', 'search', 'list'])

# 선택된 카테고리에 따라 페이지 내용을 동적으로 변경
if selected:
    st.title(f'{selected} Development Roadmaps')

    # 검색 기능
    search_query = st.text_input("Search for a roadmap:", "")

    # 선택된 카테고리의 데이터 필터링
    filtered_df = road_map[(road_map['main_category'] == selected) & (road_map['title'].str.contains(search_query, case=False))]

    # 'study_order' 열에 따라 데이터프레임 정렬
    filtered_df = filtered_df.sort_values(by='study_order', ascending=True)
    
    filtered_df['url'] = filtered_df['url'].str.replace('/roadmaps','')
    # 하이퍼링크가 포함된 테이블을 Markdown으로 생성하여 표시
    for index, row in filtered_df.iterrows():
        # 각 로우에 대한 하이퍼링크 문자열 생성
        markdown_link = f"[{row['title']}]({row['url']})({row['study_order']})"
        st.markdown(markdown_link, unsafe_allow_html=True)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import pandas as pd

def fetch_elements(driver, class_name):
    """
    Fetch elements with a given class name and extract their data.
    """
    elements = driver.find_elements(By.CLASS_NAME, class_name)
    elements_data = []
    for element in elements:
        try:
            data = {
                'category': element.get_attribute('data-group-id'),
                'contents': element.text,
                'x': float(element.find_element(By.TAG_NAME, 'rect').get_attribute('x')),
                'y': float(element.find_element(By.TAG_NAME, 'rect').get_attribute('y'))
            }
            elements_data.append(data)
        except NoSuchElementException:
            print(f"Element {element} missing expected attributes.")
    return elements_data

def preprocess_data(elements_data):
    """
    Preprocess the data: Filter, sort, and aggregate.
    """
    df = pd.DataFrame(elements_data)
    mask = df['category'].str.contains(r'\d+')
    df = df[mask]
    df.sort_values(by=['y', 'x'], inplace=True)
    df['category'] = df['category'].str.split(':', expand=True)[0].str.replace('\d+\s*-\s*', '', regex=True)
    df['contents'] = df['contents'] + '\n'
    df['sort_order'] = range(len(df))
    return df

def aggregate_data(df):
    """
    Aggregate contents by category.
    """
    return df.groupby('category').agg({
        'contents': lambda x: '\n '.join(x),
        'sort_order': 'min'
    }).sort_values('sort_order').reset_index()

# Main
if __name__ == "__main__":
    options = Options()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    target_url = input("TARGET ULR PLZ \n:")
    driver.get(target_url)
    elements_data = fetch_elements(driver, 'clickable-group')
    preprocessed_data = preprocess_data(elements_data)
    aggregated_df = aggregate_data(preprocessed_data)
    aggregated_df['contents'] = aggregated_df.apply(lambda row: row['category'] + "\n" + row['contents'], axis=1)
    aggregated_df['contents'] = aggregated_df['contents']
    aggregated_df.to_csv('computer_science_roadmap.csv', index=False)
    driver.close()


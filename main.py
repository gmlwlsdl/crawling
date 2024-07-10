from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import pandas as pd
import os

# 올바른 ChromeDriver 경로 설정
driver_path = 'D:/IDA/chromedriver-win64/chromedriver-win64/chromedriver.exe'
service = Service(driver_path)

# Chrome 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--allow-insecure-localhost')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# WebDriver 초기화
driver = webdriver.Chrome(service=service, options=options)

# 사이트 리스트
urls = [
    'https://www.outdoorresearch.com/collections/womens-tops/products/womens-echo-t-shirt-287658', # 여성 상의
    'https://www.outdoorresearch.com/collections/womens-bottoms/products/womens-ferrosi-pants-regular-287668', # 여성 하의
    'https://www.outdoorresearch.com/collections/mens-tops/products/mens-astroman-air-short-sleeve-shirt-300940', # 남성 상의
    'https://www.outdoorresearch.com/collections/mens-bottoms/products/mens-ferrosi-pants-32-287641', # 남성 하의
]

# 데이터 저장을 위한 리스트
all_data = []

# 폴더 생성
output_folder = 'output'

def click_element_js(driver, element):
    try:
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        print(f"An error occurred while trying to click the element: {e}")

def extract_table_data(table):
    rows = table.find_elements(By.TAG_NAME, "tr")
    data = []
    for row in rows:
        if row.find_elements(By.TAG_NAME, "th"):
            cols = row.find_elements(By.TAG_NAME, "th")
        else:
            cols = row.find_elements(By.TAG_NAME, "td")
        cols = [col.text for col in cols if col.text.strip()]
        data.append(cols)
    return data

for url in urls:
    # 웹 페이지 열기
    driver.get(url)
    WebDriverWait(driver, 5)  # 페이지 로드 대기

    # 쿠키 처리
    try:
        cookie = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))
        )
        cookie.click()
    except Exception as e:
        print("No cookie banner found or could not click it.")
    
    try:
        button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'js-size-chart-button')]"))
        )
        click_element_js(driver, button)

        table = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'table table-dark table-striped text-center')]"))
        )

        # 테이블 크롤링
        table_data = extract_table_data(table)

        # 데이터프레임으로 변환
        if table_data and len(table_data[0]) > 0:  # 데이터가 존재하는 경우에만 변환
            df = pd.DataFrame(table_data[1:], columns=table_data[0])  # 첫 번째 행을 헤더로 사용
            all_data.append(df)
            print(f"Data from {url}:")
            print(df)
        else:
            print(f"No data found in the table at {url}")

    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")

# 모든 데이터를 하나의 데이터프레임으로 결합
if all_data:
    combined_df = pd.concat(all_data, ignore_index=True)

    # 엑셀 파일로 저장
    excel_path = os.path.join(output_folder, 'size_table_outdoorresearch.xlsx')
    combined_df.to_excel(excel_path, index=False)

    print(f"Data saved to {excel_path}")
else:
    print("No data was collected.")

# 드라이버 종료
driver.quit()

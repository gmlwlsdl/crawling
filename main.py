from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import pandas as pd
import os

# 올바른 ChromeDriver 경로 설정
driver_path = 'D:/IDA/chromedriver-win64/chromedriver-win64/chromedriver.exe'  # chromedriver.exe의 정확한 경로로 변경
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
    'https://www.everlane.com/products/womens-organic-cotton-slim-crew-tee-white?collection=womens-all-tops', # 여성 반팔
    'https://www.everlane.com/products/womens-premium-weight-jersey-top-navy?collection=womens-all-tops', # 여성 긴팔
    'https://www.everlane.com/products/womens-a-line-denim-short-spring-blue?collection=womens-skirts-shorts', # 여성 반바지
    'https://www.everlane.com/products/womens-utility-arc-pant-organic-bone?collection=womens-pants-trousers', # 여성 긴바지
    'https://www.everlane.com/products/mens-essential-organic-crew-uniform-white?collection=mens-all-shirts-tops', # 남성 반팔
    'https://www.everlane.com/products/mens-linen-ls-shirt-bone-black?collection=mens-all-shirts-tops', # 남성 긴팔
    'https://www.everlane.com/products/mens-renew-nylon-short-black?collection=mens-bottoms', # 남성 반바지
    'https://www.everlane.com/products/mens-organic-cotton-straight-leg-jean-salt-lake?collection=mens-jeans' # 남성 긴바지
    # 다른 사이트 URL 추가
]

# 데이터 저장을 위한 리스트
all_data = []

# 폴더 생성
output_folder = 'output'
os.makedirs(output_folder, exist_ok=True)

for url in urls:
    # 웹 페이지 열기
    driver.get(url)

    try:
        # 'SIZE GUIDE' 버튼 클릭 (XPath로 찾기)
        button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='SIZE GUIDE']"))
        )
        button.click()

        # 단위 변환 버튼 클릭 (XPath로 찾기)
        button2 = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'styles_toggle__b5Nom styles_size-guide-content__unit-toggle__A_2wg')]"))
        )
        button2.click()

        # 테이블이 나타날 때까지 대기 (XPath 사용)
        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'styles_size-guide-table__QW7Nu')]"))
        )

        # 테이블 크롤링
        rows = table.find_elements(By.TAG_NAME, "tr")
        data = []

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            cols = [col.text for col in cols]
            data.append(cols)

        # 데이터프레임으로 변환
        df = pd.DataFrame(data)
        all_data.append(df)

        print(f"Data from {url}:")
        print(df)

    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")

# 모든 데이터를 하나의 데이터프레임으로 결합
combined_df = pd.concat(all_data, ignore_index=True)

# 엑셀 파일로 저장
excel_path = os.path.join(output_folder, 'size_tables_everlane.xlsx')
combined_df.to_excel(excel_path, index=False)

# 드라이버 종료
driver.quit()
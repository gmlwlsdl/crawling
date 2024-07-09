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
    'https://www.hollisterco.com/shop/wd/p/seamless-fabric-longline-crew-t-shirt-56759328?categoryId=120721&faceout=model&seq=12', # 여성 반팔
    'https://www.hollisterco.com/shop/wd/p/easy-crew-sweater-56740835?categoryId=12627&faceout=model&seq=04', # 여성 긴팔
    'https://www.hollisterco.com/shop/wd/p/relaxed-cooling-tee-57410320?categoryId=166245&faceout=model&seq=04', # 남성 반팔
    'https://www.hollisterco.com/shop/wd/p/relaxed-atlanta-1996-olympics-graphic-crew-sweatshirt-57206820?categoryId=12572&faceout=model&seq=02', # 남성 긴팔
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
        cookie = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@id, 'onetrust-accept-btn-handler')]"))
        )
        cookie.click()
    except Exception as e:
            print("No cookie banner found or could not click it.")
    
    try:
        button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Size Guide']"))
        )
        button.click()

        button1 = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@data-testid, 'toggle-block-measurement-cm')]"))
        )
        button1.click()

        # 테이블이 나타날 때까지 대기 (XPath 사용)
        table = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'size-tables__table')]"))
        )

        # 테이블 크롤링
        rows = table.find_elements(By.TAG_NAME, "tr")
        data = []

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            cols = [col.text for col in cols]
            data.append(cols)

        df = pd.DataFrame(data)
        all_data.append(df)

        print(f"Data from {url}:")
        print(df)

    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")

# 모든 데이터를 하나의 데이터프레임으로 결합
combined_df = pd.concat(all_data, ignore_index=True)

# 엑셀 파일로 저장
excel_path = os.path.join(output_folder, 'size_tables_hollisterco.xlsx')
combined_df.to_excel(excel_path, index=False)

# 드라이버 종료
driver.quit()
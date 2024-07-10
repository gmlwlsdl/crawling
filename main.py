from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import os
import time

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
    'https://www.yoox.com/kr/customercare/article/%EC%97%AC%EC%84%B1---%EC%9D%98%EB%A5%98_ccid604300000002296', # 여성 의류
    'https://www.yoox.com/kr/customercare/article/%EB%82%A8%EC%84%B1---%EC%9D%98%EB%A5%98_ccid604300000002307' # 남성 의류
]

# 데이터 저장을 위한 리스트
all_data = []

# 폴더 생성
output_folder = 'output'

for url in urls:
    # 웹 페이지 열기
    driver.get(url)
    time.sleep(5)

    # 쿠키 처리
    try:
        cookie = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@id, 'onetrust-accept-btn-handler')]"))
        )
        cookie.click()
    except Exception as e:
            print("No cookie banner found or could not click it.")
    
    try:
        table = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/section/main/div[2]/main/div[2]/div/div[1]/div/table[2]"))
        )

        # 테이블 크롤링
        rows = table.find_elements(By.TAG_NAME, "tr")
        data = []

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            cols = [col.text for col in cols]
            data.append(cols)

        # 데이터프레임으로 변환
        if data:  # 데이터가 존재하는 경우에만 변환
            df = pd.DataFrame(data)
            all_data.append(df)
            print(f"Data from {url}:")
            print(df)
        else:
            print(f"No data found in the table at {url}")

    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")

# 모든 데이터를 하나의 데이터프레임으로 결합
combined_df = pd.concat(all_data, ignore_index=True)

# 엑셀 파일로 저장
excel_path = os.path.join(output_folder, 'size_table_yoox.xlsx')
combined_df.to_excel(excel_path, index=False)

# 드라이버 종료
driver.quit()
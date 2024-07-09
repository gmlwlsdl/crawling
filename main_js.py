from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import pandas as pd
import os
import time

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
    'https://www.ae.com/us/en/p/women/t-shirts/view-all-t-shirts-/ae-hey-baby-waffle-t-shirt/2370_9647_106?menu=cat4840004', # 여성 반팔
    'https://www.ae.com/us/en/p/women/hoodies-sweatshirts/hoodies-sweatshirts/ae-oversized-mustang-graphic-sweatshirt/0453_2197_237?menu=cat4840004', # 여성 긴팔
    'https://www.ae.com/us/en/p/women/high-waisted-shorts/high-waisted-baggy-relaxed-shorts/ae-strigid-super-high-waisted-relaxed-denim-short/1334_7767_471?menu=cat4840004', # 여성 반바지
    'https://www.ae.com/us/en/p/women/baggy-wide-leg-jeans/baggy-wide-leg-jeans/ae-dreamy-drape-stretch-super-high-waisted-baggy-wide-leg-ripped-jean/0437_5349_911?menu=cat4840004', # 여성 긴바지
    'https://www.ae.com/us/en/p/men/polos/jersey-polos/ae-legend-jersey-polo-shirt/1165_3478_620?menu=cat4840004', # 남성 반팔
    'https://www.ae.com/us/en/p/men/hoodies-sweatshirts/pullover-hoodies/ae-solid-hoodie/0193_2307_001?menu=cat4840004', # 남성 긴팔
    'https://www.ae.com/us/en/p/men/shorts/khaki-shorts/ae-flex-5-linen-blend-trekker-short/4132_7755_317?menu=cat4840004', # 남성 반바지
    'https://www.ae.com/us/en/p/men/jeans/baggy-loose-jeans/ae-easyflex-loose-ripped-jean/1114_6830_926?menu=cat4840004' # 남성 긴바지
]

# 데이터 저장을 위한 리스트
all_data = []

# 폴더 생성
output_folder = 'output'
os.makedirs(output_folder, exist_ok=True)

def click_element_js(driver, xpath):
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        print(f"An error occurred while trying to click the element: {e}")

for url in urls:
    # 웹 페이지 열기
    driver.get(url)
    time.sleep(5)  # 페이지가 완전히 로드되도록 대기

    try:
        # 쿠키 배너 닫기
        try:
            click_element_js(driver, "//button[@id='onetrust-accept-btn-handler']")
        except Exception as e:
            print("No cookie banner found or could not click it.")

        # 'Size & Fit' 섹션 클릭
        click_element_js(driver, "//div[contains(@data-track-args, 'size_fit:clicked')]")

        # Size Details 버튼 클릭
        click_element_js(driver, "//button[contains(@aria-label, 'Size Details')]")

        # 단위 변환 버튼 클릭 (XPath로 찾기)
        click_element_js(driver, "//li[contains(@class, 'active nav-pill-item _active_lmu52w _nav-pill-item_lmu52w')]")

        time.sleep(10)

        # 테이블이 나타날 때까지 대기 (XPath 사용)
        table = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "//table"))
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
if all_data:  # 데이터가 존재하는 경우에만 결합
    combined_df = pd.concat(all_data, ignore_index=True)

    # 엑셀 파일로 저장
    excel_path = os.path.join(output_folder, 'size_tables_ae.xlsx')
    combined_df.to_excel(excel_path, index=False)

    print(f"Data saved to {excel_path}")
else:
    print("No data was collected.")

# 드라이버 종료
driver.quit()

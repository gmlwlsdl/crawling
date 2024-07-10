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
    'https://www.ssense.com/en-kr/women/product/versace-jeans-couture/white-institutional-logo-t-shirt/15834731', # 여성 반팔
    'https://www.ssense.com/en-kr/women/product/khaite/black-the-jo-sweater/15993171', # 여성 긴팔
    'https://www.ssense.com/en-kr/women/product/simone-rocha/black-utility-bloomer-shorts/16589711', # 여성 반바지
    'https://www.ssense.com/en-kr/women/product/khaite/blue-the-abigail-stretch-jeans/15992821', # 여성 긴바지
    'https://www.ssense.com/en-kr/men/product/ashley-williams/sense-exclusive-gray-poodle-t-shirt/16891751', # 남성 반팔
    'https://www.ssense.com/en-kr/men/product/sunspel/black-classic-long-sleeve-t-shirt/15836911', # 남성 긴팔
    'https://www.ssense.com/en-kr/men/product/balenciaga/gray-camo-shorts/15668531', # 남성 반바지
    'https://www.ssense.com/en-kr/men/product/jw-anderson/gray-twisted-workwear-jeans/16277131' # 남성 긴바지
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

def extract_size_chart(driver):
    size_data = []
    size_elements = driver.find_elements(By.XPATH, "//div[@class='pdp-size-chart__guide-image-measurements']//ul//li")
    for element in size_elements:
        try:
            style = element.get_attribute("style")
            text = element.text.strip()
            left = style.split("left:")[1].split("%")[0].strip()
            top = style.split("top:")[1].split("%")[0].strip()
            size_data.append({"left": left, "top": top, "text": text})
        except:
            continue
    return size_data

for url in urls:
    # 웹 페이지 열기
    driver.get(url)

    clickable = driver.find_element(By.ID, "kIjAXDfDWuFqlzS")
    ActionChains(driver)\
        .click_and_hold(clickable)\
        .perform()

    try:
        cookie = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@id, 'onetrust-accept-btn-handler')]"))
        )
        cookie.click()
    except Exception as e:
            print("No cookie banner found or could not click it.")
    
    try:
        button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'pdp-size-chart__model-wearing')]"))
        )
        button.click()

        button1 = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'btn-cm')]"))
        )
        button1.click()

        # 활성화된 li 요소를 순회하며 클릭
        size_buttons = driver.find_elements(By.XPATH, "//ul[@class='pdp-size-chart__size-buttons-list']/li[not(contains(@class, 'disabled'))]")
        
        for button in size_buttons:
            click_element_js(driver, button)
            time.sleep(2)  # 테이블이 로드되도록 대기

            # 사이즈 차트 데이터 크롤링
            size_chart = extract_size_chart(driver)
            data = []

            # 데이터프레임으로 변환
            if data:  # 데이터가 존재하는 경우에만 변환
                df = pd.DataFrame(data)
                df['Size Chart'] = str(size_chart)  # 사이즈 차트 데이터를 데이터프레임에 추가
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
excel_path = os.path.join(output_folder, 'size_tables_ssense.xlsx')
combined_df.to_excel(excel_path, index=False)

# 드라이버 종료
driver.quit()
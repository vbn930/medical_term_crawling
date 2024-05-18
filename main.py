from manager import log_manager

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from googletrans import Translator
import pandas as pd
import time

def translator(src, dst, trans_str):
    result_str = ""
    is_translated = False
    error_cnt = 0
    while(not is_translated):
        if error_cnt > 5:
            return ""
        try:
            translator = Translator(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            result_str = translator.translate(text=trans_str, src=src, dest=dst).text
            time.sleep(2)
            is_translated = True
        except Exception as e:
            error_cnt += 1
    return result_str

def get_terms_from_csv(path):
    org_terms = []
    
    data = pd.read_csv(path)
    
    org_terms = data["TERM"].to_list()
    
    return org_terms

def get_chrome_driver(logger: log_manager.Logger):
    chrome_options = Options()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    chrome_options.add_argument('user-agent=' + user_agent)
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-blink-features=AnimationControlled")
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--log-level=3') # 브라우저 로그 레벨을 낮춤
    chrome_options.add_argument('--disable-loging') # 로그를 남기지 않음
    # chrome_options.add_argument("headless")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def KMLE_crawler(keyword):
    dis_term = ""
    try:
        driver.get("https://www.kmle.co.kr/")
        search = driver.find_element(By.ID, "Search")
        search.send_keys(org_term)
        search.send_keys("\n")
        dis_term = driver.find_element(By.XPATH, '//*[@id="EbookTerminologyB"]/div/table/tbody/tr[1]/td[1]').text
    except Exception as e:
        logger.log_error(f"Error in KMLE tanslate term")
        
    return dis_term

def NAVER_crawler(keyword):
    dis_term = ""
    try:
        driver.get(f"https://en.dict.naver.com/#/search?range=all&query={keyword}")
        dis_term = driver.find_element(By.XPATH, '//*[@id="searchPage_entry"]/div/div[1]/ul').text
    except Exception as e:
        logger.log_error(f"Error in NAVER tanslate term")
        
    return dis_term

if __name__ == '__main__':
    logger = log_manager.Logger(log_manager.LogType.BUILD)
    driver = get_chrome_driver(logger=logger)
    driver.implicitly_wait(2)
    org_terms = get_terms_from_csv("./terms.csv")
    logger.log_info(f"Total terms : {len(org_terms)}")
    result = []
    failed_list = []
    trans_cnt = 0
    cnt = 0
    for org_term in org_terms:
        cnt += 1
        dist_term = KMLE_crawler(org_term)
        if dist_term == "":
            dist_term = NAVER_crawler(org_term)
        
        if dist_term == "":
            dist_term = translator("ko", "en", org_term)
        if dist_term != "":
            trans_cnt += 1
            logger.log_info(f"Term {org_term} -> {dist_term}, count : {trans_cnt}, progress : {cnt}/{len(org_terms)}")
        else:
            logger.log_error("Failed to translate")
        result.append(dist_term)
            
    logger.log_info(f"Result : {trans_cnt}/{len(org_terms)}")
    data = {"DIST" : result}
    path = f"./result.csv"
    data_frame = pd.DataFrame(data)
    data_frame.to_csv(path, index=False, encoding='cp949')
            
            
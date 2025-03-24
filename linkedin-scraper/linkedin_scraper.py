import logging
import time
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 設定 logging
logging.basicConfig(level=logging.INFO)

# 限制最多爬取的職缺數
MAX_JOBS = 10

# 設定 Chrome WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")  # 反自動化偵測
options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 隱藏自動化標記
options.add_experimental_option("useAutomationExtension", False)

# 啟動 WebDriver
driver = webdriver.Chrome(options=options)

# 開啟登入頁面
driver.get("https://www.linkedin.com/login")

# 手動輸入帳號密碼登入
username = input("Enter linkedIn email: ")
password = getpass("Enter linkedIn password: ")

driver.find_element(By.ID, "username").send_keys(username)
driver.find_element(By.ID, "password").send_keys(password)
driver.find_element(By.ID, "password").send_keys(Keys.RETURN)

# 開啟 LinkedIn 職缺搜尋
logging.info("🚀 正在開啟 LinkedIn 工作搜尋頁面...")
driver.get("https://www.linkedin.com/jobs/search?keywords=UI%2FUX+Designer&location=Worldwide&f_WT=2&f_TPR=r86400")

# **等待職缺清單出現**
try:
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "job-card-container__link")))
    job_listings = driver.find_elements(By.CLASS_NAME, "job-card-container__link")
    logging.info(f"✅ 找到 {len(job_listings)} 筆職種顯示，開始爬取...")
except Exception as e:
    logging.error(f"❌ 找不到職種列表元素，錯誤訊息：{e}")

# 儲存爬取的職缺資料
jobs_data = []

# 捲動頁面來載入更多職缺
while len(jobs_data) < MAX_JOBS:
    try:
        job_listings = driver.find_elements(By.CLASS_NAME, "job-card-container__link")

        for job in job_listings:
            try:
                title = job.text
                job_link = job.get_attribute("href")

                jobs_data.append((title, job_link))
                logging.info(f"✅ 抓取成功：{title}")

                if len(jobs_data) >= MAX_JOBS:
                    break

            except Exception as e:
                logging.warning(f"⚠️ 無法抓取職種：{e}")

        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(3)

    except KeyboardInterrupt:
        print('Exiting.')
        break
    except Exception as e:
        logging.error(f"❌ 發生錯誤：{e}")
        break

# **輸出結果**
print("\n🔍 爬取結果：\n")
for job in jobs_data:
    print(f"💼 職種：{job[0]}")
    print(f"🔗 連結：{job[1]}\n")

# **關閉 WebDriver**
driver.quit()
logging.info("✅ 爬取完成，已關閉瀏覽器。")

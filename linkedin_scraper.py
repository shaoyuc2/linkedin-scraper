import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# 設定 logging
logging.basicConfig(level=logging.INFO)

# 限制最多爬取的職缺數
MAX_JOBS = 10

# 設定 Chrome WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # 瀏覽器最大化
options.add_argument("--disable-blink-features=AutomationControlled")  # 反自動化偵測
options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 隱藏自動化標記
options.add_experimental_option("useAutomationExtension", False)

# 啟動 WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# **開啟 LinkedIn 職缺搜尋**
logging.info("🚀 正在開啟 LinkedIn 工作搜尋頁面...")
driver.get("https://www.linkedin.com/jobs/search?keywords=UI%2FUX+Designer&location=Worldwide&f_WT=2&f_TPR=r86400")

# **等待網站完全加載**
time.sleep(5)

# **檢查是否成功載入 LinkedIn 頁面**
if "linkedin.com/jobs" not in driver.current_url:
    logging.error("❌ 目前不在 LinkedIn 職缺搜尋頁面，請確認是否被登出或 IP 被封鎖！")
    driver.quit()
    exit()

# **手動登入**
input("🔐 請手動登入 LinkedIn，並選擇 'Remember me'，完成後按 Enter 繼續...")

# **檢查是否載入職缺**
job_listings = driver.find_elements(By.CLASS_NAME, "base-card")
print(f"🔎 檢測：找到 {len(job_listings)} 個職缺")

if len(job_listings) == 0:
    logging.error("⚠️ 找不到職缺！可能是 LinkedIn 頁面結構變更或未成功登入。")
    driver.quit()
    exit()

# **開始爬取**
jobs_data = []
for job in job_listings:
    try:
        title = job.find_element(By.CLASS_NAME, "base-search-card__title").text
        company = job.find_element(By.CLASS_NAME, "base-search-card__subtitle").text
        location = job.find_element(By.CLASS_NAME, "job-search-card__location").text
        job_link = job.find_element(By.TAG_NAME, "a").get_attribute("href")

        # **確認是否為 Remote 職缺**
        if "remote" in location.lower():
            jobs_data.append((title, company, location, job_link))
            logging.info(f"✅ 抓取成功：{title} – {company}")

        if len(jobs_data) >= MAX_JOBS:
            break

    except Exception as e:
        logging.warning(f"⚠️ 無法抓取職缺：{e}")

# **輸出結果**
print("\n🔍 爬取結果：\n")
if not jobs_data:
    print("⚠️ 沒有找到符合條件的職缺，請確認搜尋條件或稍後再試。")
else:
    for job in jobs_data:
        print(f"💼 職缺：{job[0]}")
        print(f"🏢 公司：{job[1]}")
        print(f"📍 地點：{job[2]}")
        print(f"🔗 連結：{job[3]}\n")

# **關閉 WebDriver**
driver.quit()
logging.info("✅ 爬取完成，已關閉瀏覽器。")

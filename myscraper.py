import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# --- 1. THE SCRAPER ENGINE ---
def run_udemy_scraper():
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    
    # IMPORTANT: We turn HEADLESS OFF so you can solve any CAPTCHAs manually
    # options.add_argument("--headless") 

    driver = uc.Chrome(options=options, version_main=145)
    scraped_data = []
    
    try:
        url = "https://www.udemy.com/courses/it-and-software/it-certification/"
        driver.get(url)
        
        # Give you time to click "I am human" if it pops up
        time.sleep(8) 

        # Scroll to load the cards
        driver.execute_script("window.scrollBy(0,1000)")
        time.sleep(2)

        # We use a broader XPath to find cards even if classes shift
        # This looks for any DIV that contains 'course-card' in its class name
        wait = WebDriverWait(driver, 30)
        cards_xpath = "//div[contains(@class, 'course-card-container') or contains(@class, 'course-card--container')]"
        
        cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, cards_xpath)))

        for card in cards:
            try:
                # Use relative XPaths for better stability
                title = card.find_element(By.XPATH, ".//h3//a").text
                
                try:
                    price = card.find_element(By.XPATH, ".//div[contains(@class, 'price-text')]").text
                except: price = "N/A"

                try:
                    rating = card.find_element(By.XPATH, ".//span[contains(@data-purpose, 'rating')]").text
                except: rating = "N/A"

                if title:
                    scraped_data.append({
                        "Title": title,
                        "Price": price,
                        "Rating": rating
                    })
            except:
                continue
                
    finally:
        driver.quit()
    return scraped_data

# --- 2. THE STREAMLIT USER INTERFACE ---
st.set_page_config(page_title="Udemy Auto-Loader", layout="wide")

st.title("🎓 Udemy Live Dashboard")

# Memory management
if 'scraped_results' not in st.session_state:
    with st.spinner("🔄 Initializing browser... Please solve any CAPTCHAs in the Chrome window if they appear!"):
        st.session_state.scraped_results = run_udemy_scraper()

# --- 3. DISPLAY LOGIC ---
if st.session_state.scraped_results:
    df = pd.DataFrame(st.session_state.scraped_results)
    st.success(f"Loaded {len(df)} courses.")
    st.dataframe(df, use_container_width=True)
    
    if st.button("🔄 Refresh Data"):
        del st.session_state.scraped_results
        st.rerun()
else:
    st.warning("Timeout occurred or no data found. Please check the browser window and refresh the page.")
    if st.button("Try Again"):
        st.rerun()
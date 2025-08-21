

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

BASE_URL = "https://www.kleinanzeigen.de/s-wohnung-kaufen/01159/c196l3848r20"


def fetch_listings(max_price=None):
    import re, random
    from selenium.webdriver.common.action_chains import ActionChains
    options = Options()
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(BASE_URL)
    time.sleep(3)  # wait for page to load
    items = driver.find_elements(By.CSS_SELECTOR, ".aditem")
    listings = []
    for item in items:
        try:
            html = item.get_attribute("outerHTML")
            # ...Extraktion wie bisher...
            price = None
            try:
                price_elem = item.find_element(By.CSS_SELECTOR, "p.aditem-main--middle--price-shipping--price, p.aditem-price")
                price = price_elem.text.strip()
                euro_idx = price.find('€')
                if euro_idx != -1:
                    price = price[:euro_idx+1]
            except:
                pass
            if not price:
                try:
                    script_elems = item.find_elements(By.CSS_SELECTOR, "script[type='application/ld+json']")
                    for script in script_elems:
                        data = json.loads(script.get_attribute("innerHTML"))
                        if "price" in data:
                            price = str(data["price"]).strip()
                        elif "description" in data:
                            price_match = re.search(r"([\d\.,]+\s*€)", data["description"])
                            if price_match:
                                price = price_match.group(1).strip()
                except:
                    pass
            if not price:
                price_match = re.search(r"([\d\.,]+\s*€)", html)
                if price_match:
                    price = price_match.group(1).strip()

            qm = None
            try:
                tags_elem = item.find_element(By.CSS_SELECTOR, "p.aditem-main--middle--tags")
                tags_text = tags_elem.text
                qm_match = re.search(r"([\d\.,]+)\s*m²", tags_text)
                if qm_match:
                    qm = qm_match.group(1).replace(',', '.').strip()
            except:
                pass
            if not qm:
                try:
                    script_elems = item.find_elements(By.CSS_SELECTOR, "script[type='application/ld+json']")
                    for script in script_elems:
                        data = json.loads(script.get_attribute("innerHTML"))
                        if "description" in data:
                            qm_match = re.search(r"([\d\.,]+)\s*m²", data["description"])
                            if qm_match:
                                qm = qm_match.group(1).replace(',', '.').strip()
                except:
                    pass
            if not qm:
                qm_match = re.search(r"([\d\.,]+)\s*m²", html)
                if qm_match:
                    qm = qm_match.group(1).replace(',', '.').strip()

            location = None
            try:
                loc_elem = item.find_element(By.CSS_SELECTOR, "div.aditem-main--top--left")
                location = loc_elem.text.strip()
            except:
                pass
            # Die leere try-except-Konstruktion wird entfernt
            if not location:
                loc_match = re.search(r"\d{5}\s+[A-Za-zäöüÄÖÜß\-/ ]+", html)
                if loc_match:
                    location = loc_match.group(0).strip()

            listings.append({
                "price": price,
                "qm": qm,
                "location": location
            })
        except Exception as e:
            pass
    return listings

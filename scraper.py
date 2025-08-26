

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

BASE_URL = "https://www.kleinanzeigen.de/s-wohnung-kaufen/01159/c196l3848r20"


def fetch_listings(max_price=None):
    import re, random, json
    from selenium.webdriver.common.action_chains import ActionChains
    
    # URL dynamisch mit max_price erstellen
    if max_price:
        base_url = f"https://www.kleinanzeigen.de/s-wohnung-kaufen/01159/preis::{max_price}/c196l3848r20"
    else:
        base_url = BASE_URL
    
    options = Options()
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    all_listings = []
    page = 1
    
    while True:
        # URL für aktuelle Seite erstellen
        if page == 1:
            url = base_url
        else:
            if max_price:
                url = f"https://www.kleinanzeigen.de/s-wohnung-kaufen/01159/preis::{max_price}/seite:{page}/c196l3848r20"
            else:
                url = f"https://www.kleinanzeigen.de/s-wohnung-kaufen/01159/seite:{page}/c196l3848r20"
        
        print(f"Scraping page {page}: {url}")
        driver.get(url)
        time.sleep(3)  # wait for page to load
        
        items = driver.find_elements(By.CSS_SELECTOR, ".aditem")
        
        # Wenn keine Items gefunden werden, sind wir am Ende
        if not items:
            print(f"No items found on page {page}, stopping.")
            break
            
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
        
        print(f"Found {len(listings)} listings on page {page}")
        all_listings.extend(listings)
        
        # Prüfen ob es eine nächste Seite gibt
        try:
            # Suche nach Pagination-Elementen oder "Weiter"-Button
            next_page_elements = driver.find_elements(By.CSS_SELECTOR, ".pagination-next, .pagination .fa-chevron-right, a[aria-label='Nächste Seite']")
            
            # Alternative: Prüfe ob es mehr als die aktuelle Anzahl an Seiten gibt
            pagination_elements = driver.find_elements(By.CSS_SELECTOR, ".pagination-page, .pagination a")
            has_next_page = False
            
            for elem in pagination_elements:
                try:
                    if elem.text.strip().isdigit() and int(elem.text.strip()) > page:
                        has_next_page = True
                        break
                except:
                    pass
            
            # Wenn kein Next-Button oder höhere Seitenzahl gefunden wurde, beende die Schleife
            if not next_page_elements and not has_next_page:
                print(f"No next page found after page {page}, stopping.")
                break
                
        except Exception as e:
            print(f"Error checking for next page: {e}")
            break
            
        page += 1
        
        # Sicherheitsbegrenzung: Maximal 10 Seiten
        if page > 10:
            print("Reached maximum page limit (10), stopping.")
            break
    
    driver.quit()
    print(f"Total listings found: {len(all_listings)}")
    return all_listings
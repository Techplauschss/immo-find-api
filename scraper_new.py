import requests
from bs4 import BeautifulSoup
import re
import json
import time
import random

def get_headers():
    """Generate headers that look like a real browser"""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1'
    }

def extract_best_price(item_soup, html):
    """Extrahiert den besten Preis (höchster Wert) aus einer Anzeige"""
    price = None
    
    # Versuch 1: Direkt aus dem Preis-Element
    price_elem = item_soup.select_one("p.aditem-main--middle--price-shipping--price, p.aditem-price")
    if price_elem:
        price = price_elem.get_text().strip()
        euro_idx = price.find('€')
        if euro_idx != -1:
            price = price[:euro_idx+1]
    
    # Versuch 2: Aus JSON-LD Daten
    if not price:
        script_elems = item_soup.select("script[type='application/ld+json']")
        for script in script_elems:
            try:
                data = json.loads(script.string)
                if "price" in data:
                    price = str(data["price"]).strip() + "€"
                    break
                elif "description" in data:
                    price_match = re.search(r"([\d\.,]+\s*€)", data["description"])
                    if price_match:
                        price = price_match.group(1).strip()
                        break
            except:
                continue
    
    # Versuch 3: Alle Preise im HTML finden und den höchsten wählen
    if not price:
        price_matches = re.findall(r"([\d\.,]+)\s*€", html)
        if price_matches:
            max_price = 0
            best_price = None
            for match in price_matches:
                try:
                    clean_price = match.replace('.', '').replace(',', '.')
                    num_price = float(clean_price)
                    if num_price > max_price:
                        max_price = num_price
                        best_price = match + "€"
                except:
                    continue
            if best_price:
                price = best_price
    
    return price

def scrape_listings(url, session):
    """Scrape eine einzelne Seite von Listings"""
    try:
        response = session.get(url, headers=get_headers())
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = soup.select(".aditem")
        if not items:
            return [], False  # Keine Items gefunden
        
        listings = []
        for item in items:
            try:
                html = str(item)
                
                # Link extrahieren
                link = None
                link_elem = item.select_one("article.aditem > a, a.ellipsis")
                if not link_elem:
                    link_elem = item.select_one("a[href*='/s-anzeige/']")
                
                if link_elem:
                    href = link_elem.get('href')
                    if href:
                        if href.startswith('/'):
                            link = f"https://www.kleinanzeigen.de{href}"
                        else:
                            link = href
                
                # Preis extrahieren
                price = extract_best_price(item, html)
                
                # Quadratmeter extrahieren
                qm = None
                tags_elem = item.select_one("p.aditem-main--middle--tags")
                if tags_elem:
                    tags_text = tags_elem.get_text()
                    qm_match = re.search(r"([\d\.,]+)\s*m²", tags_text)
                    if qm_match:
                        qm = qm_match.group(1).replace(',', '.').strip()
                
                if not qm:
                    qm_match = re.search(r"([\d\.,]+)\s*m²", html)
                    if qm_match:
                        qm = qm_match.group(1).replace(',', '.').strip()
                
                # Standort extrahieren
                location = None
                loc_elem = item.select_one("div.aditem-main--top--left")
                if loc_elem:
                    # Entferne alle Whitespaces und Newlines und normalisiere den Text
                    location_text = loc_elem.get_text()
                    # Entferne alle zusätzlichen Whitespaces und Newlines
                    location_text = ' '.join(location_text.split())
                    # Extrahiere PLZ und Stadtteil mit Regex
                    loc_match = re.search(r"(\d{5}\s+[A-Za-zäöüÄÖÜß\-/​ ]+)(?:\s*\(\d+\s*km\))?", location_text)
                    if loc_match:
                        location = loc_match.group(1).strip()
                
                if not location:
                    loc_match = re.search(r"\d{5}\s+[A-Za-zäöüÄÖÜß\-/​ ]+", html)
                    if loc_match:
                        location = loc_match.group(0).strip()
                
                listings.append({
                    "price": price,
                    "qm": qm,
                    "location": location,
                    "link": link
                })
                
            except Exception as e:
                continue
        
        # Prüfen ob es eine nächste Seite gibt
        has_next = False
        pagination = soup.select(".pagination-next, .pagination .fa-chevron-right, a[aria-label='Nächste Seite']")
        if pagination:
            has_next = True
        else:
            # Alternative: Prüfe ob es mehr Seiten gibt
            page_numbers = []
            for elem in soup.select(".pagination-page, .pagination a"):
                try:
                    if elem.get_text().strip().isdigit():
                        page_numbers.append(int(elem.get_text().strip()))
                except:
                    continue
            current_page = int(url.split("seite:")[-1].split("/")[0]) if "seite:" in url else 1
            has_next = any(num > current_page for num in page_numbers)
        
        return listings, has_next
        
    except Exception as e:
        print(f"Error scraping page: {e}")
        return [], False

def fetch_listings(max_price=None, min_price=None, max_qm=None, min_qm=None, radius=None, location_plz="01069"):
    """Hauptfunktion zum Abrufen aller Listings"""
    location_radius = radius if radius else 20
    
    # URL aufbauen
    base_url = f"https://www.kleinanzeigen.de/s-wohnung-kaufen/{location_plz}/"
    
    # Preis-Parameter
    if min_price or max_price:
        if min_price and max_price:
            base_url += f"preis:{min_price}:{max_price}/"
        elif min_price:
            base_url += f"preis:{min_price}/"
        elif max_price:
            base_url += f"preis::{max_price}/"
    
    base_url += f"c196l3833r{location_radius}"
    
    # QM-Parameter
    if min_qm or max_qm:
        qm_param = ""
        if min_qm:
            qm_param += str(min_qm)
        qm_param += "%2C"
        if max_qm:
            qm_param += str(max_qm)
        base_url += f"+wohnung_kaufen.qm_d:{qm_param}"
    
    all_listings = []
    page = 1
    
    # Session für wiederverwendbare Verbindung
    with requests.Session() as session:
        while True:
            # URL für aktuelle Seite
            url = base_url if page == 1 else f"{base_url}/seite:{page}/"
            
            print(f"Scraping page {page}: {url}")
            listings, has_next = scrape_listings(url, session)
            
            if not listings:
                print(f"No items found on page {page}, stopping.")
                break
            
            print(f"Found {len(listings)} listings on page {page}")
            all_listings.extend(listings)
            
            if not has_next:
                print(f"No next page found after page {page}, stopping.")
                break
            
            page += 1
            
            if page > 10:
                print("Reached maximum page limit (10), stopping.")
                break
            
            # Kurze Pause zwischen den Anfragen
            time.sleep(random.uniform(1, 3))
    
    print(f"Total listings found: {len(all_listings)}")
    return all_listings

def fetch_leipzig_listings(max_price=None, min_price=None, max_qm=None, min_qm=None, radius=None):
    """Leipzig-spezifische Version der Hauptfunktion"""
    location_area = "leipzig%2C-zentrum"
    location_code = "l4278"
    location_radius = radius if radius else 20
    
    # URL aufbauen
    base_url = f"https://www.kleinanzeigen.de/s-wohnung-kaufen/{location_area}/"
    
    # Preis-Parameter
    if min_price or max_price:
        if min_price and max_price:
            base_url += f"preis:{min_price}:{max_price}/"
        elif min_price:
            base_url += f"preis:{min_price}/"
        elif max_price:
            base_url += f"preis::{max_price}/"
    
    base_url += f"c196{location_code}r{location_radius}"
    
    # QM-Parameter
    if min_qm or max_qm:
        qm_param = ""
        if min_qm:
            qm_param += str(min_qm)
        qm_param += "%2C"
        if max_qm:
            qm_param += str(max_qm)
        base_url += f"+wohnung_kaufen.qm_d:{qm_param}"
    
    all_listings = []
    page = 1
    
    # Session für wiederverwendbare Verbindung
    with requests.Session() as session:
        while True:
            # URL für aktuelle Seite
            url = base_url if page == 1 else f"{base_url}/seite:{page}/"
            
            print(f"Scraping Leipzig page {page}: {url}")
            listings, has_next = scrape_listings(url, session)
            
            if not listings:
                print(f"No items found on Leipzig page {page}, stopping.")
                break
            
            print(f"Found {len(listings)} listings on Leipzig page {page}")
            all_listings.extend(listings)
            
            if not has_next:
                print(f"No next page found after Leipzig page {page}, stopping.")
                break
            
            page += 1
            
            if page > 10:
                print("Reached maximum page limit (10), stopping.")
                break
            
            # Kurze Pause zwischen den Anfragen
            time.sleep(random.uniform(1, 3))
    
    print(f"Total Leipzig listings found: {len(all_listings)}")
    return all_listings


def fetch_senftenberg_listings(max_price=None, min_price=None, max_qm=None, min_qm=None, radius=None):
    """Senftenberg-spezifische Version der Hauptfunktion"""
    location_area = "senftenberg"
    location_code = "l7838"
    location_radius = radius if radius else 20
    
    # URL aufbauen
    base_url = f"https://www.kleinanzeigen.de/s-wohnung-kaufen/{location_area}/"
    
    # Preis-Parameter
    if min_price or max_price:
        if min_price and max_price:
            base_url += f"preis:{min_price}:{max_price}/"
        elif min_price:
            base_url += f"preis:{min_price}/"
        elif max_price:
            base_url += f"preis::{max_price}/"
    
    base_url += f"c196{location_code}r{location_radius}"
    
    # QM-Parameter
    if min_qm or max_qm:
        qm_param = ""
        if min_qm:
            qm_param += str(min_qm)
        qm_param += "%2C"
        if max_qm:
            qm_param += str(max_qm)
        base_url += f"+wohnung_kaufen.qm_d:{qm_param}"
    
    all_listings = []
    page = 1
    
    # Session für wiederverwendbare Verbindung
    with requests.Session() as session:
        while True:
            # URL für aktuelle Seite
            url = base_url if page == 1 else f"{base_url}/seite:{page}/"
            
            print(f"Scraping Senftenberg page {page}: {url}")
            listings, has_next = scrape_listings(url, session)
            
            if not listings:
                print(f"No items found on Senftenberg page {page}, stopping.")
                break
            
            print(f"Found {len(listings)} listings on Senftenberg page {page}")
            all_listings.extend(listings)
            
            if not has_next:
                print(f"No next page found after Senftenberg page {page}, stopping.")
                break
            
            page += 1
            
            if page > 10:
                print("Reached maximum page limit (10), stopping.")
                break
            
            # Kurze Pause zwischen den Anfragen
            time.sleep(random.uniform(1, 3))
    
    print(f"Total Senftenberg listings found: {len(all_listings)}")
    return all_listings

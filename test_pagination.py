#!/usr/bin/env python3
"""
Test script to demonstrate the multi-page scraping functionality with all filters including location
"""

from scraper import fetch_listings

def test_all_filters_with_location():
    print("Testing all filters with custom location...")
    print("=" * 50)
    
    # Test mit allen Filtern inklusive Ort
    min_price = 80000
    max_price = 150000
    min_qm = 40
    max_qm = 70
    plz = "01099"
    radius = 10
    
    print(f"Fetching listings with:")
    print(f"  Location: PLZ {plz}, Radius {radius}km")
    print(f"  Price range: {min_price}€ - {max_price}€")
    print(f"  QM range: {min_qm}m² - {max_qm}m²")
    
    listings = fetch_listings(
        min_price=min_price, 
        max_price=max_price, 
        min_qm=min_qm, 
        max_qm=max_qm,
        plz=plz,
        radius=radius
    )
    
    print("=" * 50)
    print(f"Total listings scraped: {len(listings)}")
    
    if listings:
        print("\nFirst 3 listings:")
        for i, listing in enumerate(listings[:3]):
            print(f"{i+1}. Price: {listing['price']}, Qm: {listing['qm']}, Location: {listing['location']}")
    
    return listings

def test_default_location():
    print("\nTesting with default location (01159, 20km)...")
    print("=" * 50)
    
    # Test mit Standard-Ort
    min_price = 100000
    max_price = 150000
    print(f"Fetching listings with default location and price range: {min_price}€ - {max_price}€")
    
    listings = fetch_listings(min_price=min_price, max_price=max_price)
    
    print(f"Total listings scraped: {len(listings)}")
    return listings

def test_location_only():
    print("\nTesting location filter only...")
    print("=" * 30)
    
    plz = "01069"
    radius = 5
    print(f"Fetching listings for PLZ {plz} with radius {radius}km (no other filters)")
    
    listings = fetch_listings(plz=plz, radius=radius)
    
    print(f"Total listings scraped: {len(listings)}")
    return listings

def test_price_range_with_location():
    print("\nTesting price range with custom location...")
    print("=" * 40)
    
    min_price = 100000
    max_price = 120000
    plz = "01159"
    radius = 20
    print(f"Fetching listings:")
    print(f"  Location: PLZ {plz}, Radius {radius}km")
    print(f"  Price range: {min_price}€ - {max_price}€")
    
    listings = fetch_listings(
        min_price=min_price, 
        max_price=max_price, 
        plz=plz, 
        radius=radius
    )
    
    print(f"Total listings scraped: {len(listings)}")
    return listings

if __name__ == "__main__":
    test_all_filters_with_location()
    test_default_location()
    test_location_only()
    test_price_range_with_location()

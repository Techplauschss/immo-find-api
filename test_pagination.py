#!/usr/bin/env python3
"""
Test script to demonstrate the multi-page scraping functionality with all filters
"""

from scraper import fetch_listings

def test_all_filters():
    print("Testing all filters combined...")
    print("=" * 50)
    
    # Test mit allen Filtern
    min_price = 80000
    max_price = 150000
    min_qm = 40
    max_qm = 70
    print(f"Fetching listings with:")
    print(f"  Price range: {min_price}€ - {max_price}€")
    print(f"  QM range: {min_qm}m² - {max_qm}m²")
    
    listings = fetch_listings(min_price=min_price, max_price=max_price, min_qm=min_qm, max_qm=max_qm)
    
    print("=" * 50)
    print(f"Total listings scraped: {len(listings)}")
    
    if listings:
        print("\nFirst 3 listings:")
        for i, listing in enumerate(listings[:3]):
            print(f"{i+1}. Price: {listing['price']}, Qm: {listing['qm']}, Location: {listing['location']}")
    
    return listings

def test_price_range():
    print("\nTesting price range only...")
    print("=" * 30)
    
    min_price = 100000
    max_price = 120000
    print(f"Fetching listings with price range: {min_price}€ - {max_price}€")
    
    listings = fetch_listings(min_price=min_price, max_price=max_price)
    
    print(f"Total listings scraped: {len(listings)}")
    return listings

def test_min_price_only():
    print("\nTesting min price only...")
    print("=" * 30)
    
    min_price = 100000
    print(f"Fetching listings with min price: {min_price}€")
    
    listings = fetch_listings(min_price=min_price)
    
    print(f"Total listings scraped: {len(listings)}")
    return listings

def test_qm_range():
    print("\nTesting QM range filter...")
    print("=" * 30)
    
    min_qm = 40
    max_qm = 70
    print(f"Fetching listings with QM range: {min_qm}-{max_qm}m²")
    
    listings = fetch_listings(min_qm=min_qm, max_qm=max_qm)
    
    print(f"Total listings scraped: {len(listings)}")
    return listings

if __name__ == "__main__":
    test_all_filters()
    test_price_range()
    test_min_price_only()
    test_qm_range()

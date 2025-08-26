#!/usr/bin/env python3
"""
Test script to demonstrate the multi-page scraping functionality
"""

from scraper import fetch_listings

def test_pagination():
    print("Testing multi-page scraping functionality...")
    print("=" * 50)
    
    # Test with a price limit that should have multiple pages
    max_price = 150000
    print(f"Fetching listings with max price: {max_price}€")
    
    listings = fetch_listings(max_price=max_price)
    
    print("=" * 50)
    print(f"Total listings scraped: {len(listings)}")
    
    if listings:
        print("\nFirst 3 listings:")
        for i, listing in enumerate(listings[:3]):
            print(f"{i+1}. Price: {listing['price']}, Qm: {listing['qm']}, Location: {listing['location']}")
    
    return listings

if __name__ == "__main__":
    test_pagination()


from fastapi import FastAPI, Query, Response
from scraper_new import fetch_listings, fetch_leipzig_listings

app = FastAPI()

@app.get("/testdaten")
def get_testdaten():
    return [
        {"id": 1, "name": "Immobilie A", "preis": 100000},
        {"id": 2, "name": "Immobilie B", "preis": 150000},
        {"id": 3, "name": "Immobilie C", "preis": 200000}
    ]

@app.get("/dresden-listings")
def get_listings(
    response: Response, 
    max_price: int = Query(None, description="Maximaler Preis in Euro"),
    min_price: int = Query(None, description="Minimaler Preis in Euro"),
    max_qm: int = Query(None, description="Maximale Quadratmeter"),
    min_qm: int = Query(None, description="Minimale Quadratmeter"),
    radius: int = Query(None, description="Suchradius in km (Standard: 20)")
):
    listings = fetch_listings(
        max_price=max_price, 
        min_price=min_price, 
        max_qm=max_qm, 
        min_qm=min_qm,
        radius=radius
    )
    
    # Anzahl der Listings im Response Header hinzufügen
    listings_count = len(listings) if listings else 0
    response.headers["X-Total-Listings"] = str(listings_count)
    response.headers["X-Scraped-Count"] = str(listings_count)
    
    if not listings:
        return {"message": "Keine Daten gefunden oder Bot-Schutz aktiv.", "count": 0}
    
    return {"listings": listings, "count": listings_count}


@app.get("/leipzig-listings")
def get_leipzig_listings(
    response: Response, 
    max_price: int = Query(None, description="Maximaler Preis in Euro"),
    min_price: int = Query(None, description="Minimaler Preis in Euro"),
    max_qm: int = Query(None, description="Maximale Quadratmeter"),
    min_qm: int = Query(None, description="Minimale Quadratmeter"),
    radius: int = Query(None, description="Suchradius in km (Standard: 20)")
):
    listings = fetch_leipzig_listings(
        max_price=max_price, 
        min_price=min_price, 
        max_qm=max_qm, 
        min_qm=min_qm,
        radius=radius
    )
    
    # Anzahl der Listings im Response Header hinzufügen
    listings_count = len(listings) if listings else 0
    response.headers["X-Total-Listings"] = str(listings_count)
    response.headers["X-Scraped-Count"] = str(listings_count)
    
    if not listings:
        return {"message": "Keine Daten gefunden oder Bot-Schutz aktiv.", "count": 0}
    
    return {"listings": listings, "count": listings_count}

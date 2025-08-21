
from fastapi import FastAPI
from scraper import fetch_listings

app = FastAPI()

@app.get("/testdaten")
def get_testdaten():
    return [
        {"id": 1, "name": "Immobilie A", "preis": 100000},
        {"id": 2, "name": "Immobilie B", "preis": 150000},
        {"id": 3, "name": "Immobilie C", "preis": 200000}
    ]



from fastapi import Query

@app.get("/dresden-listings")
def get_dresden_listings(max_price: int = Query(None, description="Maximaler Preis in Euro")):
    listings = fetch_listings(max_price=max_price)
    if not listings:
        return {"message": "Keine Daten gefunden oder Bot-Schutz aktiv."}
    return listings

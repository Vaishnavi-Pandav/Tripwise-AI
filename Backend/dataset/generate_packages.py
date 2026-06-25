"""
Generate 5,000 travel packages for TripWise AI.
Run: python dataset/generate_packages.py
Output: dataset/output/travel_packages.csv + travel_packages.json
"""
import uuid, json, random, os
import pandas as pd

os.makedirs("dataset/output", exist_ok=True)

AGENCIES = ["TripWise Tours","SunSea Holidays","Hill Adventures","Royal Rajasthan Tours",
            "Kerala Dreams","Bali Escapes","Budget Bees","India Explorer","Globe Trotter",
            "Adventure Awaits","Heritage Journeys","Beach Bliss Tours","Mountain Magic",
            "City Breaks","Cultural Trails","Eco Voyages","Luxury Escapes","Backpacker Hub",
            "Family Fun Tours","Couple Retreats","Nomad Travels","Sacred Journeys",
            "Wildlife Wonders","Coastal Cruises","Desert Dunes","Snow Peaks Travel",
            "Island Hoppers","Temple Trails","Foodie Tours","Photography Expeditions"]

DESTINATIONS = [
    ("Goa","India"),("Manali","India"),("Kerala","India"),("Rajasthan","India"),
    ("Himachal Pradesh","India"),("Uttarakhand","India"),("Kashmir","India"),
    ("Ladakh","India"),("Ooty","India"),("Coorg","India"),("Andaman","India"),
    ("Sikkim","India"),("Meghalaya","India"),("Northeast India","India"),
    ("Varanasi","India"),("Agra","India"),("Jaipur","India"),("Udaipur","India"),
    ("Mumbai","India"),("Delhi","India"),("Golden Triangle","India"),
    ("South India","India"),("North India","India"),("East India","India"),
    ("Bali","Indonesia"),("Thailand","Thailand"),("Singapore","Singapore"),
    ("Dubai","UAE"),("Maldives","Maldives"),("Sri Lanka","Sri Lanka"),
    ("Nepal","Nepal"),("Bhutan","Bhutan"),("Vietnam","Vietnam"),
    ("Europe","Europe"),("Switzerland","Switzerland"),("Italy","Italy"),
    ("France","France"),("Spain","Spain"),("Greece","Greece"),
    ("Turkey","Turkey"),("Egypt","Egypt"),("Morocco","Morocco"),
    ("Japan","Japan"),("South Korea","South Korea"),("Australia","Australia"),
    ("New Zealand","New Zealand"),("USA","USA"),("Canada","Canada"),
    ("Peru","Peru"),("Brazil","Brazil"),("South Africa","South Africa"),
]

INCLUSIONS_POOL = ["Return Flights","Hotel Stay","Breakfast","All Meals","Airport Transfer",
                   "Guided Tour","Entry Tickets","Sightseeing","Houseboat Night","Safari",
                   "Ski Pass","Adventure Activities","Spa Session","Visa Assistance",
                   "Travel Insurance","Local Transport","Cruise","Snorkelling Kit",
                   "Camping Gear","Cycle Rental","Photography Session","Cooking Class",
                   "Ayurveda Package","Desert Camp","Bonfire Evening","Cultural Show"]

EXCLUSIONS_POOL = ["Personal Expenses","Tips","Gratuities","Alcohol","Visa Fee",
                   "Travel Insurance","Optional Activities","Porterage","Laundry",
                   "Phone Calls","Extra Meals","Mineral Water","Camera Fee"]

TYPES = ["budget","standard","premium","luxury"]
PRICE_RANGES = {"budget":(3000,12000),"standard":(12001,35000),"premium":(35001,80000),"luxury":(80001,300000)}
DURATION_RANGES = {"budget":(2,5),"standard":(4,8),"premium":(5,12),"luxury":(7,21)}

def make_package_name(destination, pkg_type, days):
    templates = [
        f"{destination} {'Budget' if pkg_type=='budget' else 'Premium' if pkg_type=='premium' else 'Luxury' if pkg_type=='luxury' else 'Explorer'} {days}N/{days+1}D",
        f"Magical {destination} {days} Days",
        f"{destination} {'Bliss' if pkg_type=='luxury' else 'Adventure' if pkg_type=='budget' else 'Escape'} Package",
        f"Discover {destination} {days}N",
        f"{destination} {'Grand Tour' if pkg_type=='premium' else 'Quick Getaway'}",
        f"{days} Days in {destination}",
        f"{destination} {'Honeymoon Special' if pkg_type=='luxury' else 'Family Package' if pkg_type=='standard' else 'Trip'}",
    ]
    return random.choice(templates)

def generate():
    rows = []
    for _ in range(5000):
        dest, country = random.choice(DESTINATIONS)
        pkg_type = random.choices(TYPES, weights=[25,40,25,10])[0]
        days = random.randint(*DURATION_RANGES[pkg_type])
        pmin, pmax = PRICE_RANGES[pkg_type]
        n_incl = random.randint(4, min(10, len(INCLUSIONS_POOL)))
        n_excl = random.randint(2, min(6, len(EXCLUSIONS_POOL)))
        incl = random.sample(INCLUSIONS_POOL, n_incl)
        excl = random.sample(EXCLUSIONS_POOL, n_excl)
        rows.append({
            "id": str(uuid.uuid4()),
            "agency_name": random.choice(AGENCIES),
            "package_name": make_package_name(dest, pkg_type, days),
            "destination": dest,
            "country": country,
            "duration_days": days,
            "price": random.randint(pmin, pmax),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "package_type": pkg_type,
            "inclusions": json.dumps(incl),
            "exclusions": json.dumps(excl),
            "description": f"Experience the best of {dest} with this {pkg_type} {days}-day package. "
                           f"{'Perfect for budget travelers.' if pkg_type=='budget' else 'Ideal for families and couples.' if pkg_type=='standard' else 'Premium experiences included.' if pkg_type=='premium' else 'Ultimate luxury experience.'}",
        })

    df = pd.DataFrame(rows)
    df.to_csv("dataset/output/travel_packages.csv", index=False, encoding="utf-8")
    with open("dataset/output/travel_packages.json","w",encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"✅ Generated {len(rows)} packages → dataset/output/travel_packages.csv + .json")

if __name__ == "__main__":
    generate()

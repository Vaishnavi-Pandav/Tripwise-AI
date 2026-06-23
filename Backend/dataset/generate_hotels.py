"""
Generate 10,000 hotels for TripWise AI.
Run: python dataset/generate_hotels.py
Output: dataset/output/hotels.csv + hotels.json
"""
import uuid, json, random, os
import pandas as pd

os.makedirs("dataset/output", exist_ok=True)

HOTEL_PREFIXES = ["The","Grand","Royal","Hotel","Resort","Inn","Palace","Park","City","Sea View",
                  "Taj","Oberoi","Leela","ITC","Marriott","Hilton","Hyatt","Radisson","Holiday",
                  "Heritage","Comfort","Budget","Green","Blue","White","Golden","Silver","Mountain",
                  "Ocean","Garden","Lakeview","Sunrise","Sunset","Star","Crown","Pearl","Diamond"]

HOTEL_SUFFIXES = ["Hotel","Resort","Inn","Suites","Lodge","Palace","Residency","Boutique Hotel",
                  "Guesthouse","Homestay","Hostel","Villa","Retreat","Spa Resort","Beach Resort",
                  "Heritage Hotel","Eco Resort","Jungle Lodge","Cliff Resort","Lake Resort"]

AMENITY_POOLS = {
    "budget":   ["WiFi","AC","TV","Hot Water","Reception 24x7"],
    "standard": ["WiFi","AC","TV","Restaurant","Parking","Room Service","Laundry"],
    "premium":  ["WiFi","Pool","Gym","Restaurant","Bar","Spa","Parking","Room Service","Conference Hall"],
    "luxury":   ["WiFi","Infinity Pool","Spa","Fine Dining","Bar","Concierge","Butler","Gym",
                 "Airport Transfer","Helipad","Private Beach","Yoga","Kids Club","Business Center"],
}

PRICE_RANGES = {"budget":(400,2000),"standard":(2001,6000),"premium":(6001,15000),"luxury":(15001,80000)}

CITIES = [
    ("Goa","Goa","India"),("Mumbai","Maharashtra","India"),("Delhi","Delhi","India"),
    ("Jaipur","Rajasthan","India"),("Manali","Himachal Pradesh","India"),
    ("Shimla","Himachal Pradesh","India"),("Kerala","Kerala","India"),
    ("Coorg","Karnataka","India"),("Ooty","Tamil Nadu","India"),("Udaipur","Rajasthan","India"),
    ("Varanasi","Uttar Pradesh","India"),("Agra","Uttar Pradesh","India"),
    ("Rishikesh","Uttarakhand","India"),("Darjeeling","West Bengal","India"),
    ("Mysore","Karnataka","India"),("Amritsar","Punjab","India"),
    ("Leh","Ladakh","India"),("Andaman","Andaman","India"),
    ("Kolkata","West Bengal","India"),("Hyderabad","Telangana","India"),
    ("Chennai","Tamil Nadu","India"),("Bangalore","Karnataka","India"),
    ("Pune","Maharashtra","India"),("Ahmedabad","Gujarat","India"),
    ("Bangkok","Bangkok","Thailand"),("Bali","Bali","Indonesia"),
    ("Singapore","Singapore","Singapore"),("Dubai","Dubai","UAE"),
    ("Paris","Ile-de-France","France"),("London","England","UK"),
    ("Rome","Lazio","Italy"),("Barcelona","Catalonia","Spain"),
    ("Tokyo","Tokyo","Japan"),("Sydney","New South Wales","Australia"),
    ("New York","New York","USA"),("Maldives","South Asia","Maldives"),
    ("Phuket","Phuket","Thailand"),("Kuala Lumpur","KL","Malaysia"),
    ("Istanbul","Istanbul","Turkey"),("Cairo","Cairo","Egypt"),
    ("Cape Town","Western Cape","South Africa"),("Kathmandu","Bagmati","Nepal"),
    ("Colombo","Western Province","Sri Lanka"),("Muscat","Muscat","Oman"),
    ("Jodhpur","Rajasthan","India"),("Jaisalmer","Rajasthan","India"),
    ("Munnar","Kerala","India"),("Alleppey","Kerala","India"),
    ("Hampi","Karnataka","India"),("Ladakh","Ladakh","India"),
]

IMAGES = [
    "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800",
    "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800",
    "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800",
    "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800",
    "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800",
    "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800",
    "https://images.unsplash.com/photo-1496417263034-38ec4f0b665a?w=800",
    "https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800",
    "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800",
    "https://images.unsplash.com/photo-1611892440504-42a792e24d32?w=800",
]

def make_hotel_name(city, category):
    prefix = random.choice(HOTEL_PREFIXES)
    suffix = random.choice(HOTEL_SUFFIXES)
    if category == "budget":
        return f"{random.choice(['Budget','Economy','Value','Comfort'])} {suffix} {city}"
    if category == "luxury":
        return f"The {random.choice(['Grand','Royal','Taj','Leela','Oberoi'])} {city}"
    return f"{prefix} {city} {suffix}"

def generate():
    rows = []
    for _ in range(10000):
        city, state, country = random.choice(CITIES)
        cat = random.choices(
            ["budget","standard","premium","luxury"],
            weights=[30,40,20,10]
        )[0]
        pmin, pmax = PRICE_RANGES[cat]
        amenities = random.sample(AMENITY_POOLS[cat], k=min(len(AMENITY_POOLS[cat]),
                                  random.randint(3, len(AMENITY_POOLS[cat]))))
        lat_base = random.uniform(8, 35) if country == "India" else random.uniform(-40, 60)
        lng_base = random.uniform(68, 98) if country == "India" else random.uniform(-120, 150)
        rows.append({
            "id": str(uuid.uuid4()),
            "hotel_name": make_hotel_name(city, cat),
            "city": city,
            "state": state,
            "country": country,
            "category": cat,
            "description": f"{'Comfortable' if cat=='budget' else 'Well-appointed' if cat=='standard' else 'Elegant' if cat=='premium' else 'Luxurious'} {random.choice(['hotel','resort','property'])} in the heart of {city}.",
            "price_per_night": random.randint(pmin, pmax),
            "rating": round(random.uniform(3.0 if cat=="budget" else 3.5, 5.0), 1),
            "amenities": json.dumps(amenities),
            "latitude": round(lat_base + random.uniform(-0.5, 0.5), 4),
            "longitude": round(lng_base + random.uniform(-0.5, 0.5), 4),
            "address": f"{random.randint(1,500)} {random.choice(['Main Road','Beach Road','MG Road','NH-48','Station Road','Temple Street'])}, {city}",
            "image_url": random.choice(IMAGES),
        })

    df = pd.DataFrame(rows)
    df.to_csv("dataset/output/hotels.csv", index=False, encoding="utf-8")
    with open("dataset/output/hotels.json","w",encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"✅ Generated {len(rows)} hotels → dataset/output/hotels.csv + .json")

if __name__ == "__main__":
    generate()

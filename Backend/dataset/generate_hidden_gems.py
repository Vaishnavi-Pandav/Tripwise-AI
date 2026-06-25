"""
Generate 5,000 hidden gems for TripWise AI.
Run: python dataset/generate_hidden_gems.py
Output: dataset/output/hidden_gems.csv + hidden_gems.json
"""
import uuid, json, random, os
import pandas as pd

os.makedirs("dataset/output", exist_ok=True)

CATEGORIES = ["beach","waterfall","trek","cafe","viewpoint","nature","adventure","historical"]
TRAVELER_TYPES = ["solo","couple","family","friends","backpacker"]
CROWD_LEVELS = ["low","medium"]

GEM_TEMPLATES = {
    "beach": [
        "{name} Secret Beach","Hidden Cove of {name}","{name} Secluded Shore",
        "{name} Virgin Beach","The Quiet Beach at {name}","Untouched Sands of {name}",
    ],
    "waterfall": [
        "{name} Hidden Falls","The Secret Waterfall near {name}","{name} Cascade",
        "Misty Falls of {name}","Jungle Waterfall near {name}",
    ],
    "trek": [
        "{name} Ridge Trail","Hidden Pass near {name}","{name} Valley Trek",
        "Secret Summit Trail of {name}","Offbeat Trek to {name}",
    ],
    "cafe": [
        "The Little Cafe in {name}","Hidden Brew of {name}","{name} Rooftop Cafe",
        "Secret Garden Cafe near {name}","The Bohemian Cup in {name}",
    ],
    "viewpoint": [
        "{name} Sunrise Point","Hidden Viewpoint at {name}","Secret Vista of {name}",
        "The Forgotten Lookout in {name}","{name} Panorama Point",
    ],
    "nature": [
        "{name} Sacred Grove","Hidden Valley of {name}","The Lost Lake near {name}",
        "Secret Garden of {name}","Enchanted Forest of {name}",
    ],
    "adventure": [
        "{name} Cliff Jump","Hidden Rappelling at {name}","Secret Zip Line near {name}",
        "Offbeat Kayaking in {name}","The Wild Camp at {name}",
    ],
    "historical": [
        "Forgotten Fort of {name}","Hidden Temple in {name}","Ancient Ruins near {name}",
        "The Lost Stepwell of {name}","Hidden Cave Monastery at {name}",
    ],
}

DESCRIPTIONS = {
    "beach":      "A secluded beach hidden from mainstream tourists — crystal waters, untouched sands, and peaceful surroundings.",
    "waterfall":  "A stunning hidden waterfall tucked deep in the forest, accessible via a short trek.",
    "trek":       "An offbeat trekking trail offering panoramic views with very few other hikers.",
    "cafe":       "A charming tucked-away cafe loved by locals — great coffee, food, and ambiance.",
    "viewpoint":  "A hidden hilltop viewpoint offering breathtaking panoramic vistas most tourists miss.",
    "nature":     "A pristine natural spot rarely visited — pure air, lush greenery, and tranquility.",
    "adventure":  "A hidden adventure spot offering thrills without the tourist rush.",
    "historical": "A forgotten historical site with rich stories and minimal crowds.",
}

CITIES_BY_REGION = {
    "India": [
        ("Goa","Goa"),("Manali","Himachal Pradesh"),("Shimla","Himachal Pradesh"),
        ("Kasol","Himachal Pradesh"),("Rishikesh","Uttarakhand"),("Nainital","Uttarakhand"),
        ("Spiti","Himachal Pradesh"),("Coorg","Karnataka"),("Munnar","Kerala"),
        ("Alleppey","Kerala"),("Wayanad","Kerala"),("Hampi","Karnataka"),
        ("Ooty","Tamil Nadu"),("Kodaikanal","Tamil Nadu"),("Jaipur","Rajasthan"),
        ("Jodhpur","Rajasthan"),("Udaipur","Rajasthan"),("Jaisalmer","Rajasthan"),
        ("Varanasi","Uttar Pradesh"),("Darjeeling","West Bengal"),("Gangtok","Sikkim"),
        ("Shillong","Meghalaya"),("Cherrapunji","Meghalaya"),("Leh","Ladakh"),
        ("Andaman","Andaman"),("Pune","Maharashtra"),("Nashik","Maharashtra"),
        ("Lonavala","Maharashtra"),("Mahabaleshwar","Maharashtra"),("Puri","Odisha"),
        ("Visakhapatnam","Andhra Pradesh"),("Chikmagalur","Karnataka"),
        ("Badami","Karnataka"),("Gokarna","Karnataka"),("Varkala","Kerala"),
    ],
    "Global": [
        ("Ubud","Bali"),("Canggu","Bali"),("Pai","Thailand"),("Chiang Rai","Thailand"),
        ("Kampot","Cambodia"),("Hoi An","Vietnam"),("Ninh Binh","Vietnam"),
        ("Ghent","Belgium"),("Sintra","Portugal"),("Kotor","Montenegro"),
        ("Plovdiv","Bulgaria"),("Tbilisi","Georgia"),("Luang Prabang","Laos"),
        ("Pokhara","Nepal"),("Bandipur","Nepal"),("Ella","Sri Lanka"),
        ("Sigiriya","Sri Lanka"),("Wadi Rum","Jordan"),("Chefchaouen","Morocco"),
        ("Essaouira","Morocco"),("Swakopmund","Namibia"),("Zanzibar","Tanzania"),
        ("Matera","Italy"),("Civita di Bagnoregio","Italy"),("Ronda","Spain"),
        ("Hallstatt","Austria"),("Positano","Italy"),("Delphi","Greece"),
        ("Queenstown","New Zealand"),("Franz Josef","New Zealand"),
    ],
}

IMAGES_BY_CATEGORY = {
    "beach":      "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800",
    "waterfall":  "https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=800",
    "trek":       "https://images.unsplash.com/photo-1551632811-561732d1e306?w=800",
    "cafe":       "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800",
    "viewpoint":  "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
    "nature":     "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800",
    "adventure":  "https://images.unsplash.com/photo-1564769625905-50e93615e769?w=800",
    "historical": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800",
}

def generate():
    rows = []
    all_cities = [(c,s,"India") for c,s in CITIES_BY_REGION["India"]] + \
                 [(c,s,"Global") for c,s in CITIES_BY_REGION["Global"]]

    for i in range(5000):
        city, state, region = random.choice(all_cities)
        cat = random.choice(CATEGORIES)
        template = random.choice(GEM_TEMPLATES[cat])
        place_name = template.format(name=city)
        t_types = random.sample(TRAVELER_TYPES, k=random.randint(1,3))
        best_times = random.choice(["Oct–Mar","Nov–Feb","Apr–Jun","Jul–Sep","Year-round",
                                    "Early Morning","Monsoon","Post-Monsoon","Sunrise","Sunset"])
        cost = random.choice([0, 50, 100, 150, 200, 300, 400, 500, 750, 1000, 1500, 2000])

        lat = random.uniform(8, 35) if region == "India" else random.uniform(-45, 65)
        lng = random.uniform(68, 98) if region == "India" else random.uniform(-130, 160)

        rows.append({
            "id": str(uuid.uuid4()),
            "place_name": place_name,
            "city": city,
            "state": state,
            "country": "India" if region == "India" else random.choice(
                ["Indonesia","Thailand","Vietnam","Nepal","Sri Lanka","France","Italy","Spain",
                 "Morocco","Jordan","New Zealand","Australia","Japan","Portugal","Greece"]),
            "category": cat,
            "description": DESCRIPTIONS[cat],
            "estimated_cost": cost,
            "crowd_level": random.choice(CROWD_LEVELS),
            "best_time_to_visit": best_times,
            "traveler_type": ",".join(t_types),
            "latitude": round(lat + random.uniform(-1,1), 4),
            "longitude": round(lng + random.uniform(-1,1), 4),
            "image_url": IMAGES_BY_CATEGORY[cat],
        })

    df = pd.DataFrame(rows)
    df.to_csv("dataset/output/hidden_gems.csv", index=False, encoding="utf-8")
    with open("dataset/output/hidden_gems.json","w",encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"✅ Generated {len(rows)} hidden gems → dataset/output/hidden_gems.csv + .json")

if __name__ == "__main__":
    generate()

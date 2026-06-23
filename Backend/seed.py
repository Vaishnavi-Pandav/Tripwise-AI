"""
TripWise AI — Database Seeder
Populates initial data: hotels, packages, destinations, attractions, hidden gems, weather cache.
Run: python seed.py
"""
import json
import uuid
from datetime import date, datetime

from app.db.session import SessionLocal
from app.models.hotel import Hotel
from app.models.package import TravelPackage
from app.models.destination import Destination
from app.models.attraction import Attraction
from app.models.hidden_gem import HiddenGem
from app.models.weather import WeatherDataCache

db = SessionLocal()

def seed_hotels():
    if db.query(Hotel).count() > 0:
        print("Hotels already seeded — skipping")
        return
    hotels = [
        Hotel(city="Goa", hotel_name="Taj Exotica Resort & Spa", description="Luxury beachfront resort",
              price_per_night=12000, rating=4.8, hotel_category="luxury", address="Benaulim Beach, South Goa",
              amenities=json.dumps(["Pool","Spa","WiFi","Fine Dining","Beach Access","Gym","Concierge"]),
              image_url="https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800"),
        Hotel(city="Goa", hotel_name="Park Hyatt Goa Resort", description="Sprawling resort with water park",
              price_per_night=8500, rating=4.6, hotel_category="luxury", address="Arossim Beach, Cansaulim",
              amenities=json.dumps(["Pool","Water Park","WiFi","Restaurant","Bar","Spa","Gym"]),
              image_url="https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800"),
        Hotel(city="Goa", hotel_name="The Emerald Bay", description="Boutique hotel near Calangute",
              price_per_night=3500, rating=4.2, hotel_category="premium", address="Calangute, North Goa",
              amenities=json.dumps(["Pool","WiFi","Restaurant","AC","Room Service"]),
              image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800"),
        Hotel(city="Goa", hotel_name="Zostel Goa", description="Trendy hostel for backpackers",
              price_per_night=700, rating=4.0, hotel_category="budget", address="Anjuna, North Goa",
              amenities=json.dumps(["WiFi","Common Area","Lockers","Breakfast"]),
              image_url="https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800"),
        Hotel(city="Manali", hotel_name="The Himalayan", description="Mountain luxury hotel with valley views",
              price_per_night=6500, rating=4.7, hotel_category="luxury", address="Log Huts Area, Old Manali",
              amenities=json.dumps(["Mountain View","Restaurant","Fireplace","WiFi","Spa","Bonfire"]),
              image_url="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"),
        Hotel(city="Manali", hotel_name="Snow Valley Resorts", description="Mid-range cosy resort",
              price_per_night=2800, rating=4.1, hotel_category="standard", address="Hadimba Road, Manali",
              amenities=json.dumps(["WiFi","Restaurant","Parking","Room Heater","Valley View"]),
              image_url="https://images.unsplash.com/photo-1574268852955-1f1e66b26c19?w=800"),
        Hotel(city="Mumbai", hotel_name="The Taj Mahal Palace", description="Iconic heritage luxury hotel",
              price_per_night=20000, rating=4.9, hotel_category="luxury", address="Apollo Bunder, Colaba",
              amenities=json.dumps(["Pool","Spa","Fine Dining","Concierge","WiFi","Heritage Tour","Bar"]),
              image_url="https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800"),
        Hotel(city="Kerala", hotel_name="Kumarakom Lake Resort", description="Luxury backwater resort",
              price_per_night=9500, rating=4.8, hotel_category="luxury", address="Kumarakom, Kottayam",
              amenities=json.dumps(["Houseboat","Ayurveda","Pool","WiFi","Restaurant","Kayaking","Bird Watching"]),
              image_url="https://images.unsplash.com/photo-1602002418082-a4443e081dd1?w=800"),
        Hotel(city="Jaipur", hotel_name="Rambagh Palace", description="Former royal palace converted to hotel",
              price_per_night=25000, rating=4.9, hotel_category="luxury", address="Bhawani Singh Road",
              amenities=json.dumps(["Heritage","Pool","Polo","Spa","Fine Dining","Elephant Ride","WiFi"]),
              image_url="https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?w=800"),
        Hotel(city="Bali", hotel_name="Four Seasons Bali at Sayan", description="Iconic jungle resort",
              price_per_night=45000, rating=4.9, hotel_category="luxury", address="Sayan, Ubud, Bali",
              amenities=json.dumps(["Infinity Pool","Jungle View","Spa","Fine Dining","Yoga","WiFi","Butler"]),
              image_url="https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800"),
    ]
    db.bulk_save_objects(hotels)
    db.commit()
    print(f"✅ {len(hotels)} hotels seeded")

def seed_packages():
    if db.query(TravelPackage).count() > 0:
        print("Packages already seeded — skipping")
        return
    packages = [
        TravelPackage(destination="Goa", agency_name="TripWise Tours", package_name="Goa Beach Bliss 4N/5D",
              duration_days=5, price=12999, package_type="standard", rating=4.3,
              package_description="Complete Goa experience — beaches, forts, nightlife, and seafood.",
              inclusions=json.dumps(["Return Flights","Hotel (3★)","Breakfast","Airport Transfer","Guided Tour"]),
              exclusions=json.dumps(["Lunch/Dinner","Water Sports","Personal Expenses"]),
              image_url="https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800"),
        TravelPackage(destination="Goa", agency_name="SunSea Holidays", package_name="Goa Luxury Escape 3N/4D",
              duration_days=4, price=28999, package_type="luxury", rating=4.7,
              package_description="Luxury resort stay with private beach, spa, and fine dining.",
              inclusions=json.dumps(["Flights","5★ Hotel","All Meals","Spa Session","Yacht Ride","Airport Transfer"]),
              exclusions=json.dumps(["Casino","Personal Shopping"]),
              image_url="https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800"),
        TravelPackage(destination="Manali", agency_name="Hill Adventures", package_name="Manali Snow Adventure 5N/6D",
              duration_days=6, price=18500, package_type="premium", rating=4.5,
              package_description="Skiing, trekking, river rafting in the Himalayas.",
              inclusions=json.dumps(["Volvo Bus","Hotel (3★)","Breakfast & Dinner","Skiing","River Rafting","Guide"]),
              exclusions=json.dumps(["Flights","Paragliding","Personal Expenses"]),
              image_url="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"),
        TravelPackage(destination="Kerala", agency_name="Kerala Dreams", package_name="Kerala Backwaters & Hills 6N/7D",
              duration_days=7, price=24999, package_type="premium", rating=4.6,
              package_description="Houseboat, hill stations, Ayurveda, and wildlife in God's Own Country.",
              inclusions=json.dumps(["Flights","Hotels","Houseboat Night","Ayurveda Session","All Meals","Guide"]),
              exclusions=json.dumps(["Elephant Ride","Personal Expenses"]),
              image_url="https://images.unsplash.com/photo-1602002418082-a4443e081dd1?w=800"),
        TravelPackage(destination="Rajasthan", agency_name="Royal Rajasthan Tours", package_name="Golden Triangle 7N/8D",
              duration_days=8, price=32999, package_type="premium", rating=4.4,
              package_description="Delhi, Agra, Jaipur — India's most iconic triangle.",
              inclusions=json.dumps(["AC Car","Hotels","Breakfast","Taj Mahal Entry","Guide","Airport Pickup"]),
              exclusions=json.dumps(["Flights","Lunch/Dinner","Monument Extras"]),
              image_url="https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800"),
        TravelPackage(destination="Bali", agency_name="Bali Escapes", package_name="Bali Tropical Paradise 5N/6D",
              duration_days=6, price=45999, package_type="luxury", rating=4.8,
              package_description="Ubud jungle, Seminyak beach, temples, and Balinese spa.",
              inclusions=json.dumps(["Int. Flights","Villa Stay","Breakfast","Spa","Temple Tour","Cooking Class"]),
              exclusions=json.dumps(["Visa","Travel Insurance","Personal Expenses"]),
              image_url="https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800"),
        TravelPackage(destination="Goa", agency_name="Budget Bees", package_name="Goa Budget Backpacker 3N/4D",
              duration_days=4, price=5999, package_type="budget", rating=4.0,
              package_description="Affordable Goa trip — perfect for backpackers and students.",
              inclusions=json.dumps(["Bus Travel","Hostel Stay","1 Meal/Day"]),
              exclusions=json.dumps(["Flights","Activities","Other Meals"]),
              image_url="https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800"),
    ]
    db.bulk_save_objects(packages)
    db.commit()
    print(f"✅ {len(packages)} packages seeded")

def seed_destinations():
    if db.query(Destination).count() > 0:
        print("Destinations already seeded — skipping")
        return
    destinations = [
        Destination(city_name="Goa", state="Goa", country="India",
              avg_budget_score=7.5, safety_score=7.0, weather_score=8.0, crowd_score=5.5,
              nightlife_score=9.5, food_score=8.5, adventure_score=7.0, family_friendly_score=6.5,
              description="India's beach capital — sun, sand, seafood, and nightlife.",
              best_season="Nov–Feb", known_for="Beaches, Nightlife, Water Sports, Seafood, Portuguese Heritage",
              image_url="https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800"),
        Destination(city_name="Manali", state="Himachal Pradesh", country="India",
              avg_budget_score=7.0, safety_score=7.5, weather_score=6.5, crowd_score=6.0,
              nightlife_score=5.0, food_score=7.5, adventure_score=9.5, family_friendly_score=7.0,
              description="Himalayan paradise for trekking, skiing, and river adventures.",
              best_season="Mar–Jun, Oct–Nov", known_for="Trekking, Skiing, River Rafting, Snow, Rohtang Pass",
              image_url="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"),
        Destination(city_name="Kerala", state="Kerala", country="India",
              avg_budget_score=7.0, safety_score=8.5, weather_score=7.5, crowd_score=7.0,
              nightlife_score=4.0, food_score=9.5, adventure_score=7.0, family_friendly_score=9.0,
              description="God's Own Country — backwaters, hills, wildlife, and Ayurveda.",
              best_season="Sep–Mar", known_for="Backwaters, Ayurveda, Cuisine, Wildlife, Houseboats",
              image_url="https://images.unsplash.com/photo-1602002418082-a4443e081dd1?w=800"),
        Destination(city_name="Jaipur", state="Rajasthan", country="India",
              avg_budget_score=7.5, safety_score=7.0, weather_score=6.0, crowd_score=6.5,
              nightlife_score=5.0, food_score=8.5, adventure_score=7.0, family_friendly_score=8.5,
              description="The Pink City — royal forts, palaces, and Rajputana heritage.",
              best_season="Oct–Mar", known_for="Forts, Palaces, Desert Safari, Cuisine, Elephants",
              image_url="https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800"),
        Destination(city_name="Mumbai", state="Maharashtra", country="India",
              avg_budget_score=5.5, safety_score=7.0, weather_score=7.0, crowd_score=3.5,
              nightlife_score=9.0, food_score=9.0, adventure_score=5.0, family_friendly_score=7.0,
              description="City of dreams — Bollywood, street food, and infinite energy.",
              best_season="Nov–Feb", known_for="Bollywood, Gateway of India, Street Food, Marine Drive",
              image_url="https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800"),
        Destination(city_name="Bali", state="Bali", country="Indonesia",
              avg_budget_score=7.0, safety_score=7.5, weather_score=8.5, crowd_score=6.0,
              nightlife_score=8.5, food_score=8.5, adventure_score=8.5, family_friendly_score=7.5,
              description="Island paradise of temples, rice terraces, surf, and spiritual retreats.",
              best_season="Apr–Oct", known_for="Temples, Rice Terraces, Surfing, Nightlife, Yoga",
              image_url="https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800"),
        Destination(city_name="Gokarna", state="Karnataka", country="India",
              avg_budget_score=8.5, safety_score=8.5, weather_score=8.0, crowd_score=8.5,
              nightlife_score=4.5, food_score=7.0, adventure_score=7.5, family_friendly_score=7.5,
              description="Serene coastal town with secluded beaches and ancient temples.",
              best_season="Oct–Mar", known_for="Secluded Beaches, Temples, Hippie Culture, Trekking",
              image_url="https://images.unsplash.com/photo-1590077428593-a55bb07c4665?w=800"),
        Destination(city_name="Shimla", state="Himachal Pradesh", country="India",
              avg_budget_score=7.0, safety_score=8.0, weather_score=7.5, crowd_score=6.0,
              nightlife_score=4.0, food_score=7.0, adventure_score=7.0, family_friendly_score=8.5,
              description="Colonial hill station with snow, toy trains, and apple orchards.",
              best_season="Mar–Jun, Dec–Jan", known_for="Colonial Architecture, Snow, Toy Train, Mall Road",
              image_url="https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800"),
    ]
    db.bulk_save_objects(destinations)
    db.commit()
    print(f"✅ {len(destinations)} destinations seeded")

def seed_attractions():
    if db.query(Attraction).count() > 0:
        print("Attractions already seeded — skipping")
        return
    attractions = [
        Attraction(city="Goa", attraction_name="Calangute Beach", category="beach",
              description="The most popular beach in Goa — golden sands and water sports.",
              entry_fee=0, rating=4.2,
              location_coordinates={"lat": 15.5491, "lng": 73.7552}),
        Attraction(city="Goa", attraction_name="Fort Aguada", category="historical",
              description="17th-century Portuguese fort with a lighthouse and panoramic views.",
              entry_fee=0, rating=4.4,
              location_coordinates={"lat": 15.4936, "lng": 73.7739}),
        Attraction(city="Goa", attraction_name="Dudhsagar Falls", category="waterfall",
              description="One of India's tallest waterfalls — a spectacular four-tiered cascade.",
              entry_fee=400, rating=4.7,
              location_coordinates={"lat": 15.3143, "lng": 74.3142}),
        Attraction(city="Manali", attraction_name="Rohtang Pass", category="viewpoint",
              description="Stunning mountain pass at 3978m with snow even in summer.",
              entry_fee=550, rating=4.5,
              location_coordinates={"lat": 32.3742, "lng": 77.2520}),
        Attraction(city="Manali", attraction_name="Hadimba Temple", category="historical",
              description="Ancient wooden temple dedicated to Hadimba Devi, surrounded by cedar forest.",
              entry_fee=0, rating=4.4,
              location_coordinates={"lat": 32.2450, "lng": 77.1779}),
        Attraction(city="Jaipur", attraction_name="Amber Fort", category="historical",
              description="Majestic hilltop fort palace with intricate mirror work and elephant rides.",
              entry_fee=500, rating=4.7,
              location_coordinates={"lat": 26.9855, "lng": 75.8513}),
        Attraction(city="Jaipur", attraction_name="Hawa Mahal", category="historical",
              description="The iconic Palace of Winds — 953 small windows and pink sandstone.",
              entry_fee=50, rating=4.5,
              location_coordinates={"lat": 26.9239, "lng": 75.8267}),
        Attraction(city="Mumbai", attraction_name="Gateway of India", category="historical",
              description="Iconic arch monument overlooking the Arabian Sea.", entry_fee=0, rating=4.4,
              location_coordinates={"lat": 18.9220, "lng": 72.8347}),
        Attraction(city="Kerala", attraction_name="Alleppey Backwaters", category="nature",
              description="Serene network of canals, lakes, and lagoons best explored on a houseboat.",
              entry_fee=0, rating=4.8,
              location_coordinates={"lat": 9.4981, "lng": 76.3388}),
    ]
    db.bulk_save_objects(attractions)
    db.commit()
    print(f"✅ {len(attractions)} attractions seeded")

def seed_hidden_gems():
    if db.query(HiddenGem).count() > 0:
        print("Hidden gems already seeded — skipping")
        return
    gems = [
        HiddenGem(city="Goa", place_name="Butterfly Beach", category="beach",
              description="Secluded beach accessible only by boat — crystal water, zero crowds.",
              estimated_cost=500, crowd_level="low", best_time_to_visit="Oct–Apr, Morning",
              traveler_type="couples,solo,friends", latitude=15.0183, longitude=74.0183),
        HiddenGem(city="Goa", place_name="Divar Island", category="nature",
              description="Quiet island connected by ferry — old Portuguese houses and paddy fields.",
              estimated_cost=200, crowd_level="low", best_time_to_visit="Nov–Feb",
              traveler_type="solo,couples,backpacker", latitude=15.5063, longitude=73.9188),
        HiddenGem(city="Goa", place_name="Chapora Fort Sunrise", category="viewpoint",
              description="The Dil Chahta Hai fort — sunrise views over Vagator beach.",
              estimated_cost=0, crowd_level="medium", best_time_to_visit="6–7 AM",
              traveler_type="solo,couples,friends", latitude=15.6058, longitude=73.7390),
        HiddenGem(city="Manali", place_name="Chandrakhani Pass", category="trek",
              description="High-altitude pass at 3660m — stunning views, far fewer tourists than Rohtang.",
              estimated_cost=1500, crowd_level="low", best_time_to_visit="Jun–Sep",
              traveler_type="adventure,solo,friends", latitude=32.1756, longitude=77.1756),
        HiddenGem(city="Kerala", place_name="Thenmala Rope Bridge", category="adventure",
              description="India's first eco-tourism destination with a 100m rope bridge.",
              estimated_cost=200, crowd_level="low", best_time_to_visit="Oct–Mar",
              traveler_type="adventure,friends,family", latitude=8.9703, longitude=77.0195),
        HiddenGem(city="Jaipur", place_name="Kheechan Crane Village", category="nature",
              description="Thousands of Demoiselle cranes land here every winter — magical bird watching.",
              estimated_cost=0, crowd_level="low", best_time_to_visit="Oct–Mar",
              traveler_type="solo,couples,family", latitude=27.0453, longitude=72.3789),
    ]
    db.bulk_save_objects(gems)
    db.commit()
    print(f"✅ {len(gems)} hidden gems seeded")

def seed_weather():
    if db.query(WeatherDataCache).count() > 0:
        print("Weather cache already seeded — skipping")
        return
    today = date.today()
    weather = [
        WeatherDataCache(city="Goa", temperature=31, feels_like=34, humidity=72,
              wind_speed=18, weather_condition="Partly Cloudy", weather_icon="02d",
              rain_probability=15, forecast_date=today),
        WeatherDataCache(city="Manali", temperature=12, feels_like=8, humidity=65,
              wind_speed=22, weather_condition="Clear Sky", weather_icon="01d",
              rain_probability=5, forecast_date=today),
        WeatherDataCache(city="Mumbai", temperature=33, feels_like=37, humidity=80,
              wind_speed=25, weather_condition="Humid", weather_icon="02d",
              rain_probability=20, forecast_date=today),
        WeatherDataCache(city="Kerala", temperature=28, feels_like=31, humidity=85,
              wind_speed=15, weather_condition="Light Showers", weather_icon="10d",
              rain_probability=60, forecast_date=today),
        WeatherDataCache(city="Jaipur", temperature=38, feels_like=42, humidity=30,
              wind_speed=12, weather_condition="Sunny", weather_icon="01d",
              rain_probability=2, forecast_date=today),
        WeatherDataCache(city="Bali", temperature=29, feels_like=33, humidity=78,
              wind_speed=20, weather_condition="Tropical", weather_icon="02d",
              rain_probability=25, forecast_date=today),
    ]
    db.bulk_save_objects(weather)
    db.commit()
    print(f"✅ {len(weather)} weather records seeded")

if __name__ == "__main__":
    print("\n🌱 TripWise AI — Database Seeder\n")
    seed_destinations()
    seed_hotels()
    seed_packages()
    seed_attractions()
    seed_hidden_gems()
    seed_weather()
    db.close()
    print("\n✅ All seed data inserted successfully!\n")

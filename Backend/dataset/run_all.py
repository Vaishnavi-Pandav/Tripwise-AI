"""
Master runner — generates all datasets and loads into PostgreSQL.
Run: python dataset/run_all.py [--generate-only] [--load-only]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

GENERATE_ONLY = "--generate-only" in sys.argv
LOAD_ONLY     = "--load-only" in sys.argv

if not LOAD_ONLY:
    print("\n📊 STEP 1: Generating datasets...\n")
    from dataset.generate_destinations import generate as gen_dest
    from dataset.generate_hotels       import generate as gen_hotels
    from dataset.generate_packages     import generate as gen_packages
    from dataset.generate_hidden_gems  import generate as gen_gems
    gen_dest()
    gen_hotels()
    gen_packages()
    gen_gems()

if not GENERATE_ONLY:
    print("\n🗄️  STEP 2: Loading into PostgreSQL...\n")
    import json, pandas as pd
    from sqlalchemy.orm import Session
    from app.db.session import SessionLocal, engine
    import app.models

    from app.models.destination import Destination
    from app.models.hotel       import Hotel
    from app.models.package     import TravelPackage
    from app.models.hidden_gem  import HiddenGem

    db: Session = SessionLocal()

    def load_destinations():
        df = pd.read_csv("dataset/output/destinations.csv")
        existing = db.query(Destination).count()
        if existing > 100:
            print(f"  Destinations: {existing} already in DB — skipping")
            return
        objs = [Destination(
            city_name=r["destination_name"], state=r["state_region"], country=r["country"],
            description=r["description"], best_season=r["best_time_to_visit"],
            avg_budget_score=round(min(r["average_budget"]/5000,10),1),
            safety_score=r["safety_score"], weather_score=round(r["popularity_score"]*0.9,1),
            crowd_score=round(10-r["popularity_score"]*0.5,1), nightlife_score=round(r["popularity_score"]*0.7,1),
            food_score=round(r["popularity_score"]*0.85,1), adventure_score=round(r["safety_score"]*0.8,1),
            family_friendly_score=round(r["safety_score"]*0.9,1),
            known_for=r["category"].replace("_"," ").title(), image_url=r["image_url"],
        ) for _, r in df.iterrows()]
        db.bulk_save_objects(objs); db.commit()
        print(f"  ✅ Loaded {len(objs)} destinations")

    def load_hotels():
        df = pd.read_csv("dataset/output/hotels.csv")
        existing = db.query(Hotel).count()
        if existing > 100:
            print(f"  Hotels: {existing} already in DB — skipping")
            return
        objs = [Hotel(
            city=r["city"], hotel_name=r["hotel_name"], description=r["description"],
            price_per_night=r["price_per_night"], rating=r["rating"],
            hotel_category=r["category"], amenities=r["amenities"],
            address=r["address"], image_url=r["image_url"],
            latitude=r["latitude"], longitude=r["longitude"],
        ) for _, r in df.iterrows()]
        db.bulk_save_objects(objs); db.commit()
        print(f"  ✅ Loaded {len(objs)} hotels")

    def load_packages():
        df = pd.read_csv("dataset/output/travel_packages.csv")
        existing = db.query(TravelPackage).count()
        if existing > 100:
            print(f"  Packages: {existing} already in DB — skipping")
            return
        objs = [TravelPackage(
            agency_name=r["agency_name"], package_name=r["package_name"],
            destination=r["destination"], duration_days=int(r["duration_days"]),
            price=r["price"], rating=r["rating"], package_type=r["package_type"],
            inclusions=r["inclusions"], exclusions=r["exclusions"],
            package_description=r["description"],
        ) for _, r in df.iterrows()]
        db.bulk_save_objects(objs); db.commit()
        print(f"  ✅ Loaded {len(objs)} packages")

    def load_hidden_gems():
        df = pd.read_csv("dataset/output/hidden_gems.csv")
        existing = db.query(HiddenGem).count()
        if existing > 100:
            print(f"  Hidden Gems: {existing} already in DB — skipping")
            return
        objs = [HiddenGem(
            city=r["city"], place_name=r["place_name"], category=r["category"],
            description=r["description"], estimated_cost=r["estimated_cost"],
            crowd_level=r["crowd_level"], best_time_to_visit=r["best_time_to_visit"],
            traveler_type=r["traveler_type"], latitude=r["latitude"], longitude=r["longitude"],
            image_url=r["image_url"],
        ) for _, r in df.iterrows()]
        db.bulk_save_objects(objs); db.commit()
        print(f"  ✅ Loaded {len(objs)} hidden gems")

    load_destinations()
    load_hotels()
    load_packages()
    load_hidden_gems()
    db.close()

print("\n🎉 Complete! All datasets ready.\n")

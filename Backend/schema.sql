-- ============================================================
-- TripWise AI — PostgreSQL Database Schema
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- for gen_random_uuid()

-- ─────────────────────────────────────────
-- 1. USERS
-- ─────────────────────────────────────────
CREATE TABLE users (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name        VARCHAR(150) NOT NULL,
    email            VARCHAR(255) NOT NULL UNIQUE,
    password_hash    VARCHAR(255) NOT NULL,
    profile_image    TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);

-- ─────────────────────────────────────────
-- 2. TRIPS
-- ─────────────────────────────────────────
CREATE TABLE trips (
    id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id               UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_location       VARCHAR(255) NOT NULL,
    destination_location  VARCHAR(255) NOT NULL,
    budget                NUMERIC(12,2) NOT NULL,
    number_of_days        INTEGER NOT NULL CHECK (number_of_days > 0),
    number_of_travelers   INTEGER NOT NULL CHECK (number_of_travelers > 0),
    travel_mode           VARCHAR(50),          -- 'flight' | 'train' | 'road' | 'mixed'
    total_estimated_cost  NUMERIC(12,2),
    trip_status           VARCHAR(30) NOT NULL DEFAULT 'draft',  -- draft | planned | ongoing | completed
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_trips_user_id          ON trips(user_id);
CREATE INDEX idx_trips_destination      ON trips(destination_location);
CREATE INDEX idx_trips_status           ON trips(trip_status);

-- ─────────────────────────────────────────
-- 3. HOTELS
-- ─────────────────────────────────────────
CREATE TABLE hotels (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    city             VARCHAR(150) NOT NULL,
    hotel_name       VARCHAR(255) NOT NULL,
    description      TEXT,
    price_per_night  NUMERIC(10,2) NOT NULL,
    rating           NUMERIC(3,1) CHECK (rating >= 0 AND rating <= 5),
    address          TEXT,
    image_url        TEXT,
    amenities        JSONB,       -- e.g. ["WiFi", "Pool", "Spa"]
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_hotels_city   ON hotels(city);
CREATE INDEX idx_hotels_rating ON hotels(rating);

-- ─────────────────────────────────────────
-- 4. HOTEL RECOMMENDATIONS
-- ─────────────────────────────────────────
CREATE TABLE hotel_recommendations (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id              UUID        NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    hotel_id             UUID        NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    recommendation_score NUMERIC(4,2) CHECK (recommendation_score >= 0 AND recommendation_score <= 10),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (trip_id, hotel_id)
);
CREATE INDEX idx_hotel_rec_trip_id  ON hotel_recommendations(trip_id);
CREATE INDEX idx_hotel_rec_hotel_id ON hotel_recommendations(hotel_id);

-- ─────────────────────────────────────────
-- 5. TRAVEL PACKAGES
-- ─────────────────────────────────────────
CREATE TABLE travel_packages (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    destination         VARCHAR(255) NOT NULL,
    agency_name         VARCHAR(255),
    package_name        VARCHAR(255) NOT NULL,
    duration_days       INTEGER NOT NULL CHECK (duration_days > 0),
    price               NUMERIC(12,2) NOT NULL,
    package_description TEXT,
    inclusions          JSONB,       -- ["Flights", "Hotel", "Meals"]
    exclusions          JSONB,       -- ["Visa", "Travel Insurance"]
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_packages_destination ON travel_packages(destination);
CREATE INDEX idx_packages_price       ON travel_packages(price);

-- ─────────────────────────────────────────
-- 6. TRIP EXPENSES
-- ─────────────────────────────────────────
CREATE TABLE trip_expenses (
    id                 UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id            UUID        NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    transport_cost     NUMERIC(12,2) NOT NULL DEFAULT 0,
    hotel_cost         NUMERIC(12,2) NOT NULL DEFAULT 0,
    food_cost          NUMERIC(12,2) NOT NULL DEFAULT 0,
    activity_cost      NUMERIC(12,2) NOT NULL DEFAULT 0,
    miscellaneous_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_cost         NUMERIC(12,2) GENERATED ALWAYS AS (
                           transport_cost + hotel_cost + food_cost +
                           activity_cost + miscellaneous_cost
                       ) STORED,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (trip_id)
);
CREATE INDEX idx_expenses_trip_id ON trip_expenses(trip_id);

-- ─────────────────────────────────────────
-- 7. ITINERARIES
-- ─────────────────────────────────────────
CREATE TABLE itineraries (
    id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id        UUID        NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    day_number     INTEGER NOT NULL CHECK (day_number > 0),
    title          VARCHAR(255),
    activities     JSONB,          -- structured activity list
    estimated_cost NUMERIC(10,2),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (trip_id, day_number)
);
CREATE INDEX idx_itineraries_trip_id ON itineraries(trip_id);

-- ─────────────────────────────────────────
-- 8. ATTRACTIONS
-- ─────────────────────────────────────────
CREATE TABLE attractions (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    city                 VARCHAR(150) NOT NULL,
    attraction_name      VARCHAR(255) NOT NULL,
    category             VARCHAR(100),   -- 'temple' | 'museum' | 'park' | 'beach' etc.
    description          TEXT,
    entry_fee            NUMERIC(10,2),
    rating               NUMERIC(3,1) CHECK (rating >= 0 AND rating <= 5),
    location_coordinates JSONB,          -- {"lat": 12.97, "lng": 77.59}
    image_url            TEXT
);
CREATE INDEX idx_attractions_city     ON attractions(city);
CREATE INDEX idx_attractions_category ON attractions(category);

-- ─────────────────────────────────────────
-- 9. HIDDEN GEMS
-- ─────────────────────────────────────────
CREATE TABLE hidden_gems (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    city             VARCHAR(150) NOT NULL,
    place_name       VARCHAR(255) NOT NULL,
    description      TEXT,
    recommended_for  VARCHAR(255),   -- 'solo' | 'couples' | 'families' | 'adventure'
    image_url        TEXT
);
CREATE INDEX idx_hidden_gems_city ON hidden_gems(city);

-- ─────────────────────────────────────────
-- 10. DESTINATION COMPARISONS
-- ─────────────────────────────────────────
CREATE TABLE destination_comparisons (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    destination_one  VARCHAR(255) NOT NULL,
    destination_two  VARCHAR(255) NOT NULL,
    budget_score     NUMERIC(4,2) CHECK (budget_score   >= 0 AND budget_score   <= 10),
    safety_score     NUMERIC(4,2) CHECK (safety_score   >= 0 AND safety_score   <= 10),
    weather_score    NUMERIC(4,2) CHECK (weather_score  >= 0 AND weather_score  <= 10),
    crowd_score      NUMERIC(4,2) CHECK (crowd_score    >= 0 AND crowd_score    <= 10),
    nightlife_score  NUMERIC(4,2) CHECK (nightlife_score>= 0 AND nightlife_score<= 10),
    overall_score    NUMERIC(4,2) GENERATED ALWAYS AS (
                         ROUND((budget_score + safety_score + weather_score +
                                crowd_score + nightlife_score) / 5.0, 2)
                     ) STORED
);
CREATE INDEX idx_dest_compare_one ON destination_comparisons(destination_one);
CREATE INDEX idx_dest_compare_two ON destination_comparisons(destination_two);

-- ─────────────────────────────────────────
-- 11. SAVED TRIPS
-- ─────────────────────────────────────────
CREATE TABLE saved_trips (
    id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    trip_id    UUID        NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, trip_id)
);
CREATE INDEX idx_saved_trips_user_id ON saved_trips(user_id);

-- ─────────────────────────────────────────
-- 12. AI CHAT HISTORY
-- ─────────────────────────────────────────
CREATE TABLE ai_chat_history (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_message TEXT        NOT NULL,
    ai_response  TEXT        NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_chat_user_id    ON ai_chat_history(user_id);
CREATE INDEX idx_chat_created_at ON ai_chat_history(created_at DESC);

-- ─────────────────────────────────────────
-- 13. REVIEWS
-- ─────────────────────────────────────────
CREATE TABLE reviews (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    hotel_id    UUID        REFERENCES hotels(id) ON DELETE SET NULL,
    package_id  UUID        REFERENCES travel_packages(id) ON DELETE SET NULL,
    rating      NUMERIC(3,1) NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (hotel_id IS NOT NULL OR package_id IS NOT NULL)
);
CREATE INDEX idx_reviews_user_id    ON reviews(user_id);
CREATE INDEX idx_reviews_hotel_id   ON reviews(hotel_id);
CREATE INDEX idx_reviews_package_id ON reviews(package_id);

-- ─────────────────────────────────────────
-- 14. WEATHER DATA CACHE
-- ─────────────────────────────────────────
CREATE TABLE weather_data_cache (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    city              VARCHAR(150) NOT NULL,
    temperature       NUMERIC(5,2),
    weather_condition VARCHAR(100),
    humidity          NUMERIC(5,2),
    forecast_date     DATE        NOT NULL,
    fetched_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (city, forecast_date)
);
CREATE INDEX idx_weather_city          ON weather_data_cache(city);
CREATE INDEX idx_weather_forecast_date ON weather_data_cache(forecast_date);

-- ─────────────────────────────────────────
-- BONUS: USER PREFERENCES (AI personalisation)
-- ─────────────────────────────────────────
CREATE TABLE user_preferences (
    id                UUID     PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID     NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    preferred_budget  VARCHAR(50),        -- 'budget' | 'mid-range' | 'luxury'
    travel_styles     JSONB,              -- ["adventure", "cultural", "beach"]
    preferred_climates JSONB,             -- ["tropical", "cold"]
    dietary_needs     JSONB,              -- ["vegetarian", "halal"]
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- BONUS: AI TRIP SUGGESTIONS (feed / discovery)
-- ─────────────────────────────────────────
CREATE TABLE ai_trip_suggestions (
    id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id        UUID        REFERENCES users(id) ON DELETE CASCADE,
    destination    VARCHAR(255) NOT NULL,
    reason         TEXT,
    suggested_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_dismissed   BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX idx_suggestions_user_id ON ai_trip_suggestions(user_id);

import axios from 'axios';
import { auth } from './firebase';

// ── Types ──────────────────────────────────────────────────────────────────────

export interface TripGenerationRequest {
  source: string;
  destination: string;
  days: number;
  travelers: number;
  budget: number;
}

export interface TripGenerationResponse {
  itinerary: string;
}

export interface Trip {
  id: string;
  user_id: string;
  source_location: string;
  destination_location: string;
  budget: number;
  number_of_days: number;
  number_of_travelers: number;
  travel_mode: string | null;
  total_estimated_cost: number | null;
  trip_status: string;
  created_at: string;
  updated_at: string;
}

export interface TripCreate {
  source_location: string;
  destination_location: string;
  budget: number;
  number_of_days: number;
  number_of_travelers: number;
  travel_mode?: string;
}

export interface AnalyticsDashboard {
  total_trips: number;
  completed_trips: number;
  planned_trips: number;
  cancelled_trips: number;
  draft_trips: number;
  favorite_destination: string | null;
  total_budget_spent: number;
  average_trip_cost: number;
  total_days_travelled: number;
  top_destinations: { destination: string; count: number }[];
  most_used_travel_mode: string | null;
}

export interface RouteRequest {
  source: string;
  destination: string;
  travelers?: number;
  budget?: number;
}

export interface WeatherData {
  city: string;
  temperature: number | null;
  feels_like: number | null;
  weather_condition: string | null;
  humidity: number | null;
  wind_speed: number | null;
  rain_probability: number | null;
  travel_recommendation: string;
  source: string;
}

export interface SearchResult {
  id: string;
  name: string;
  type: string;
  city: string | null;
  description: string | null;
  price: number | null;
  rating: number | null;
  image_url: string | null;
}

// ── Axios instance ─────────────────────────────────────────────────────────────

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach Firebase token to every request if user is logged in
api.interceptors.request.use(async (config) => {
  const { auth } = await import('./firebase');
  // Wait for auth to be ready, then get token
  const currentUser = auth.currentUser;
  if (currentUser) {
    try {
      const token = await currentUser.getIdToken(/* forceRefresh */ false);
      config.headers.Authorization = `Bearer ${token}`;
    } catch (err) {
      console.warn('Could not get Firebase token:', err);
    }
  }
  return config;
});

// ── Auth endpoints ─────────────────────────────────────────────────────────────

export async function generateTripPlan(tripData: TripGenerationRequest): Promise<TripGenerationResponse> {
  const { data } = await api.post<TripGenerationResponse>('/api/v1/ai/generate', tripData);
  return data;
}

// ── Trip endpoints ─────────────────────────────────────────────────────────────

export async function createTrip(tripData: TripCreate): Promise<Trip> {
  const { data } = await api.post<Trip>('/api/v1/trips/', tripData);
  return data;
}

export async function getTrips(): Promise<{ trips: Trip[]; total: number }> {
  const { data } = await api.get('/api/v1/trips/');
  return data;
}

export async function getTrip(tripId: string): Promise<Trip> {
  const { data } = await api.get<Trip>(`/api/v1/trips/${tripId}`);
  return data;
}

export async function deleteTrip(tripId: string): Promise<void> {
  await api.delete(`/api/v1/trips/${tripId}`);
}

// ── Analytics ──────────────────────────────────────────────────────────────────

export async function getAnalytics(): Promise<AnalyticsDashboard> {
  const { data } = await api.get<AnalyticsDashboard>('/api/v1/dashboard/analytics');
  return data;
}

// ── Weather ────────────────────────────────────────────────────────────────────

export async function getWeather(city: string): Promise<WeatherData> {
  const { data } = await api.get<WeatherData>(`/api/v1/weather/${city}`);
  return data;
}

// ── Route ──────────────────────────────────────────────────────────────────────

export async function calculateRoute(payload: RouteRequest) {
  const { data } = await api.post('/api/v1/routes/calculate', payload);
  return data;
}

// ── Search ─────────────────────────────────────────────────────────────────────

export async function globalSearch(q: string, type?: string): Promise<{ results: SearchResult[]; total: number }> {
  const { data } = await api.get('/api/v1/search/', { params: { q, type } });
  return data;
}

// ── Favorites ─────────────────────────────────────────────────────────────────

export async function addFavorite(entityType: string, entityId: string) {
  const { data } = await api.post(`/api/v1/favorites/${entityType}`, { entity_id: entityId });
  return data;
}

export async function getFavorites(entityType?: string) {
  const { data } = await api.get('/api/v1/favorites/', { params: { entity_type: entityType } });
  return data;
}

export async function removeFavorite(favoriteId: string) {
  await api.delete(`/api/v1/favorites/${favoriteId}`);
}

// ── Public Axios instance (no auth) for chat ─────────────────────────────────

const publicApi = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// ── AI Chat ────────────────────────────────────────────────────────────────────

export async function aiChat(message: string, tripId?: string) {
  // Use publicApi — no auth token needed for chat
  const { data } = await publicApi.post('/api/v1/ai/chat', { message, trip_id: tripId });
  return data;
}

export default api;

import axios from 'axios';

// ── Types ─────────────────────────────────────────────────────────────────────

// Matches backend app/schemas/ai.py → TripGenerationRequest
export interface TripGenerationRequest {
  source: string;           // maps to source_location in the AI endpoint prompt
  destination: string;
  days: number;
  travelers: number;
  budget: number;
}

export interface TripGenerationResponse {
  itinerary: string;
}

// ── Axios instance ────────────────────────────────────────────────────────────

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── API functions ─────────────────────────────────────────────────────────────

export async function generateTripPlan(
  tripData: TripGenerationRequest
): Promise<TripGenerationResponse> {
  const { data } = await api.post<TripGenerationResponse>(
    '/api/v1/ai/generate',
    tripData
  );
  return data;
}

export default api;

/* ------------------------------------------------------------------ */
/*  User & Auth                                                       */
/* ------------------------------------------------------------------ */

export interface UserResponse {
  id: string;
  email: string;
  name: string;
  picture?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
}

/* ------------------------------------------------------------------ */
/*  Search                                                            */
/* ------------------------------------------------------------------ */

export type SearchType = "flight" | "hotel";

export type TripType = "one_way" | "roundtrip";

export interface SearchParams {
  type: SearchType;
  origin?: string;
  destination: string;
  departure_date: string;
  return_date?: string;
  adults: number;
  children?: number;
  cabin_class?: "economy" | "premium_economy" | "business" | "first";
  check_in?: string;
  check_out?: string;
  rooms?: number;
  currency?: string;
}

export interface FlightSegment {
  airline: string;
  airline_logo?: string;
  flight_number: string;
  departure_airport: string;
  arrival_airport: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  cabin_class: string;
}

export interface FlightResult {
  id: string;
  provider: string;
  price: number;
  currency: string;
  outbound_segments: FlightSegment[];
  return_segments?: FlightSegment[];
  total_duration_minutes: number;
  stops: number;
  booking_url?: string;
  expires_at?: string;
}

export interface HotelResult {
  id: string;
  provider: string;
  name: string;
  address: string;
  latitude?: number;
  longitude?: number;
  star_rating: number;
  user_rating?: number;
  review_count?: number;
  price_per_night: number;
  total_price: number;
  currency: string;
  amenities: string[];
  images: string[];
  booking_url?: string;
  cancellation_policy?: string;
  expires_at?: string;
}

export interface SearchResponse {
  search_id: string;
  type: SearchType;
  flights?: FlightResult[];
  hotels?: HotelResult[];
  total_results: number;
  search_params: SearchParams;
  created_at: string;
}

/* ------------------------------------------------------------------ */
/*  Price Comparison                                                   */
/* ------------------------------------------------------------------ */

export interface PricePoint {
  provider: string;
  price: number;
  currency: string;
  url?: string;
  fetched_at: string;
}

export interface CompareResult {
  item_id: string;
  item_type: SearchType;
  label: string;
  prices: PricePoint[];
  lowest_price: number;
  highest_price: number;
  average_price: number;
}

/* ------------------------------------------------------------------ */
/*  Trips & Itinerary                                                 */
/* ------------------------------------------------------------------ */

export interface ItineraryItem {
  id: string;
  day: number;
  time?: string;
  type: "flight" | "hotel" | "activity" | "transfer" | "note";
  title: string;
  description?: string;
  location?: string;
  cost?: number;
  currency?: string;
  booking_ref?: string;
  metadata?: Record<string, unknown>;
}

export interface TripResponse {
  id: string;
  user_id: string;
  title: string;
  destination: string;
  start_date: string;
  end_date: string;
  status: "planning" | "booked" | "in_progress" | "completed" | "cancelled";
  itinerary: ItineraryItem[];
  total_budget?: number;
  currency?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTripPayload {
  title: string;
  destination: string;
  start_date: string;
  end_date: string;
  notes?: string;
  total_budget?: number;
  currency?: string;
}

export interface UpdateTripPayload extends Partial<CreateTripPayload> {
  status?: TripResponse["status"];
  itinerary?: ItineraryItem[];
}

/* ------------------------------------------------------------------ */
/*  Chat                                                              */
/* ------------------------------------------------------------------ */

export type ChatRole = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface ChatRequest {
  message: string;
  trip_id?: string;
  context?: Record<string, unknown>;
}

/* ------------------------------------------------------------------ */
/*  SSE Events                                                        */
/* ------------------------------------------------------------------ */

export type SSEEventType = "text" | "data" | "done" | "error";

export interface SSEEvent {
  type: SSEEventType;
  data: string;
}

/* ------------------------------------------------------------------ */
/*  API Error                                                         */
/* ------------------------------------------------------------------ */

export interface ApiError {
  detail: string;
  status_code: number;
}

/* ------------------------------------------------------------------ */
/*  Subscriptions                                                      */
/* ------------------------------------------------------------------ */

export type SubscriptionType = "bug_fare" | "price_drop" | "deal_digest";

export interface SubscriptionEmail {
  id: string;
  email: string;
  is_verified: boolean;
  verified_at: string | null;
  created_at: string;
}

export interface Subscription {
  id: string;
  email_id: string;
  type: SubscriptionType;
  config: Record<string, unknown>;
  is_active: boolean;
  last_sent_at: string | null;
  created_at: string;
}

/* ------------------------------------------------------------------ */
/*  User Preferences                                                   */
/* ------------------------------------------------------------------ */

export interface UserPreferences {
  preferred_airlines: string[] | null;
  excluded_airlines: string[] | null;
  preferred_alliances: string[] | null;
  cabin_classes: string[] | null;
  max_stops: number | null;
  home_airports: string[] | null;
}

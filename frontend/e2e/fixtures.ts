/**
 * Shared mock data for E2E tests.
 * Centralizes all fixtures to avoid duplication across spec files.
 */

export const MOCK_USER = {
  id: "user-1",
  email: "test@example.com",
  name: "Test User",
  picture: null,
  tier: "basic",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

export const MOCK_PREMIUM_USER = {
  ...MOCK_USER,
  tier: "premium",
};

export const MOCK_FLIGHT_RESULTS = {
  search_id: "search-1",
  type: "flight",
  flights: [
    {
      id: "flight-1",
      provider: "amadeus",
      price: 15000,
      currency: "TWD",
      outbound_segments: [
        {
          airline: "China Airlines",
          flight_number: "CI100",
          departure_airport: "TPE",
          arrival_airport: "NRT",
          departure_time: "2026-04-01T08:30:00",
          arrival_time: "2026-04-01T12:30:00",
          duration_minutes: 180,
          cabin_class: "economy",
        },
      ],
      total_duration_minutes: 180,
      stops: 0,
    },
    {
      id: "flight-2",
      provider: "skyscanner",
      price: 14500,
      currency: "TWD",
      outbound_segments: [
        {
          airline: "EVA Air",
          flight_number: "BR198",
          departure_airport: "TPE",
          arrival_airport: "NRT",
          departure_time: "2026-04-01T10:00:00",
          arrival_time: "2026-04-01T14:00:00",
          duration_minutes: 180,
          cabin_class: "economy",
        },
      ],
      total_duration_minutes: 180,
      stops: 0,
    },
  ],
  hotels: null,
  total_results: 2,
  search_params: {
    type: "flight",
    origin: "TPE",
    destination: "NRT",
    departure_date: "2026-04-01",
    adults: 1,
    currency: "TWD",
  },
  created_at: "2026-04-01T00:00:00Z",
};

export const MOCK_FLIGHT_RESULTS_EMPTY = {
  ...MOCK_FLIGHT_RESULTS,
  flights: [],
  total_results: 0,
};

export const MOCK_ROUNDTRIP_FLIGHT_RESULTS = {
  search_id: "search-rt-1",
  type: "flight",
  flights: [
    {
      id: "flight-rt-1",
      provider: "amadeus",
      price: 28000,
      currency: "TWD",
      outbound_segments: [
        {
          airline: "China Airlines",
          flight_number: "CI100",
          departure_airport: "TPE",
          arrival_airport: "NRT",
          departure_time: "2026-04-01T08:30:00",
          arrival_time: "2026-04-01T12:30:00",
          duration_minutes: 180,
          cabin_class: "economy",
        },
      ],
      return_segments: [
        {
          airline: "China Airlines",
          flight_number: "CI101",
          departure_airport: "NRT",
          arrival_airport: "TPE",
          departure_time: "2026-04-08T14:00:00",
          arrival_time: "2026-04-08T17:30:00",
          duration_minutes: 210,
          cabin_class: "economy",
        },
      ],
      total_duration_minutes: 180,
      stops: 0,
    },
  ],
  hotels: null,
  total_results: 1,
  search_params: {
    type: "flight",
    origin: "TPE",
    destination: "NRT",
    departure_date: "2026-04-01",
    return_date: "2026-04-08",
    adults: 1,
    currency: "TWD",
  },
  created_at: "2026-04-01T00:00:00Z",
};

export const MOCK_HOTEL_RESULTS = {
  search_id: "search-h1",
  type: "hotel",
  flights: null,
  hotels: [
    {
      id: "hotel-1",
      provider: "skyscanner",
      name: "Grand Tokyo Hotel",
      address: "Chiyoda-ku, Tokyo",
      star_rating: 4,
      user_rating: 8.5,
      review_count: 500,
      price_per_night: 5000,
      total_price: 20000,
      currency: "TWD",
      amenities: ["WiFi", "Pool"],
      images: [],
    },
    {
      id: "hotel-2",
      provider: "kiwi",
      name: "Shinjuku Inn",
      address: "Shinjuku-ku, Tokyo",
      star_rating: 3,
      user_rating: 7.2,
      review_count: 200,
      price_per_night: 3000,
      total_price: 12000,
      currency: "TWD",
      amenities: ["WiFi"],
      images: [],
    },
  ],
  total_results: 2,
  search_params: {
    type: "hotel",
    destination: "Tokyo",
    departure_date: "2026-04-01",
    adults: 2,
    currency: "TWD",
    check_in: "2026-04-01",
    check_out: "2026-04-05",
    rooms: 1,
  },
  created_at: "2026-04-01T00:00:00Z",
};

export const MOCK_HOTEL_RESULTS_EMPTY = {
  ...MOCK_HOTEL_RESULTS,
  hotels: [],
  total_results: 0,
};

export const MOCK_COMPARE_RESULTS = [
  {
    item_id: "flight-1",
    item_type: "flight",
    label: "TPE → NRT (CI100)",
    prices: [
      { provider: "amadeus", price: 15000, currency: "TWD", fetched_at: "2026-04-01T00:00:00Z" },
    ],
    lowest_price: 15000,
    highest_price: 15000,
    average_price: 15000,
  },
  {
    item_id: "flight-2",
    item_type: "flight",
    label: "TPE → NRT (BR198)",
    prices: [
      { provider: "skyscanner", price: 14500, currency: "TWD", fetched_at: "2026-04-01T00:00:00Z" },
    ],
    lowest_price: 14500,
    highest_price: 14500,
    average_price: 14500,
  },
];

export const MOCK_HOTEL_COMPARE_RESULTS = [
  {
    item_id: "hotel-1",
    item_type: "hotel",
    label: "Grand Tokyo Hotel",
    prices: [
      { provider: "skyscanner", price: 5000, currency: "TWD", fetched_at: "2026-04-01T00:00:00Z" },
    ],
    lowest_price: 5000,
    highest_price: 5000,
    average_price: 5000,
  },
  {
    item_id: "hotel-2",
    item_type: "hotel",
    label: "Shinjuku Inn",
    prices: [
      { provider: "kiwi", price: 3000, currency: "TWD", fetched_at: "2026-04-01T00:00:00Z" },
    ],
    lowest_price: 3000,
    highest_price: 3000,
    average_price: 3000,
  },
];

export const MOCK_TRIPS = [
  {
    id: "trip-1",
    title: "Tokyo Spring Trip",
    destination: "Tokyo, Japan",
    start_date: "2026-04-01",
    end_date: "2026-04-07",
    status: "planning" as const,
    itinerary: [
      {
        id: "it-1",
        day: 1,
        type: "flight" as const,
        title: "Flight to Tokyo",
        time: "08:30",
        description: "CI100 TPE → NRT",
        location: "Narita Airport",
        cost: 15000,
        currency: "TWD",
      },
    ],
    created_at: "2026-03-01T00:00:00Z",
    updated_at: "2026-03-01T00:00:00Z",
  },
  {
    id: "trip-2",
    title: "Osaka Summer",
    destination: "Osaka, Japan",
    start_date: "2026-07-15",
    end_date: "2026-07-22",
    status: "booked" as const,
    itinerary: [],
    created_at: "2026-03-10T00:00:00Z",
    updated_at: "2026-03-10T00:00:00Z",
  },
  {
    id: "trip-3",
    title: "Bangkok Weekend",
    destination: "Bangkok, Thailand",
    start_date: "2026-02-01",
    end_date: "2026-02-03",
    status: "completed" as const,
    itinerary: [],
    created_at: "2026-01-15T00:00:00Z",
    updated_at: "2026-02-03T00:00:00Z",
  },
];

export const MOCK_TRIP_WITH_ITINERARY = {
  id: "trip-full",
  title: "Tokyo Adventure",
  destination: "Tokyo, Japan",
  start_date: "2026-04-01",
  end_date: "2026-04-03",
  status: "planning" as const,
  itinerary: [
    {
      id: "it-1",
      day: 1,
      type: "flight" as const,
      title: "Flight to Tokyo",
      time: "08:30",
      description: "CI100 TPE → NRT",
      location: "Narita Airport",
      cost: 15000,
      currency: "TWD",
    },
    {
      id: "it-2",
      day: 1,
      type: "hotel" as const,
      title: "Check-in Grand Tokyo Hotel",
      time: "15:00",
      description: "Deluxe room",
      location: "Chiyoda-ku",
      cost: 5000,
      currency: "TWD",
    },
    {
      id: "it-3",
      day: 2,
      type: "activity" as const,
      title: "Visit Senso-ji Temple",
      time: "09:00",
      description: "Historic Buddhist temple",
      location: "Asakusa",
    },
    {
      id: "it-4",
      day: 2,
      type: "transfer" as const,
      title: "Train to Shibuya",
      time: "14:00",
      description: "JR Yamanote Line",
      cost: 200,
      currency: "TWD",
    },
    {
      id: "it-5",
      day: 3,
      type: "note" as const,
      title: "Check-out & departure",
      time: "10:00",
      description: "Pack and head to airport",
    },
  ],
  created_at: "2026-03-01T00:00:00Z",
  updated_at: "2026-03-01T00:00:00Z",
};

export const MOCK_EMAILS = [
  {
    id: "email-1",
    email: "test@example.com",
    is_verified: true,
    verified_at: "2026-01-01T00:00:00Z",
    created_at: "2026-01-01T00:00:00Z",
  },
  {
    id: "email-2",
    email: "pending@example.com",
    is_verified: false,
    verified_at: null,
    created_at: "2026-03-15T00:00:00Z",
  },
];

export const MOCK_SUBSCRIPTIONS = [
  {
    id: "sub-1",
    email_id: "email-1",
    type: "bug_fare",
    config: { origin: "TPE", destination: "NRT" },
    is_active: true,
    last_sent_at: null,
    created_at: "2026-01-01T00:00:00Z",
  },
  {
    id: "sub-2",
    email_id: "email-1",
    type: "price_drop",
    config: { origin: "TPE", destination: "KIX" },
    is_active: false,
    last_sent_at: "2026-03-10T00:00:00Z",
    created_at: "2026-02-01T00:00:00Z",
  },
];

export const MOCK_PRICE_HISTORY = {
  origin: "TPE",
  destination: "NRT",
  days: 30,
  points: [
    {
      id: "ph-1",
      origin: "TPE",
      destination: "NRT",
      departure_date: "2026-04-01",
      price_amount: 8500,
      price_currency: "TWD",
      source: "amadeus",
      airline: "CI",
      cabin_class: null,
      stops: 0,
      created_at: "2026-03-10T08:00:00Z",
    },
    {
      id: "ph-2",
      origin: "TPE",
      destination: "NRT",
      departure_date: "2026-04-01",
      price_amount: 9200,
      price_currency: "TWD",
      source: "skyscanner",
      airline: "BR",
      cabin_class: null,
      stops: 0,
      created_at: "2026-03-11T08:00:00Z",
    },
    {
      id: "ph-3",
      origin: "TPE",
      destination: "NRT",
      departure_date: "2026-04-01",
      price_amount: 7800,
      price_currency: "TWD",
      source: "google_flights",
      airline: "CI",
      cabin_class: null,
      stops: 1,
      created_at: "2026-03-12T08:00:00Z",
    },
  ],
};

export const MOCK_NOTIFICATIONS = [
  {
    id: "notif-1",
    subscription_id: "sub-1",
    email: "test@example.com",
    subject: "Bug Fare Alert: TPE → NRT",
    sent_at: "2026-03-15T10:00:00Z",
    status: "sent",
  },
  {
    id: "notif-2",
    subscription_id: "sub-1",
    email: "test@example.com",
    subject: "Price Drop: TPE → NRT",
    sent_at: "2026-03-14T08:00:00Z",
    status: "failed",
  },
];

export const MOCK_PREFERENCES = {
  home_airports: ["TPE"],
  preferred_airlines: ["BR", "CI"],
  excluded_airlines: null,
  preferred_alliances: ["Star Alliance"],
  cabin_classes: ["economy", "business"],
  max_stops: 1,
};

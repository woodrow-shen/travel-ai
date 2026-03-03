# Kiwi Flights Scraper API (RapidAPI)

- **Host**: `flights-scraper-real-time.p.rapidapi.com`
- **Protocol**: HTTPS
- **Auth Headers**:
  - `x-rapidapi-key`: API key
  - `x-rapidapi-host`: `flights-scraper-real-time.p.rapidapi.com`

---

## Endpoints

### 1. `GET /flights/search-return` — Round-trip flight search

Returns round-trip itineraries. Response sample: `response_sample.json`

#### Required Params

| Param | Type | Description |
|---|---|---|
| `originSkyId` | String | Airport code (e.g. `JFK`) or City ID (e.g. `City:new-york-city_ny_us`). Get from `/flights/auto-complete` |
| `destinationSkyId` | String | Same format as originSkyId |

#### Optional Params

| Param | Type | Default | Description |
|---|---|---|---|
| `departureDate` | Date (YYYY-MM-DD) | current date | Earliest departure date |
| `departureDateEnd` | Date (YYYY-MM-DD) | — | Latest departure date (range search) |
| `returnDate` | Date (YYYY-MM-DD) | current + 10 days | Earliest return date |
| `returnDateEnd` | Date (YYYY-MM-DD) | — | Latest return date (range search) |
| `limit` | Number | 20 | Max results |
| `stops` | Number | 0 | 0=Direct, 1=Up to 1 stop, 2=Up to 2 stops |
| `adults` | Number | 1 | Adult passengers |
| `children` | Number | 0 | Child passengers |
| `infants` | Number | 0 | Infant passengers |
| `currency` | String | USD | Currency code (from `/configs`) |
| `locale` | String | en-US | Locale (from `/configs`) |
| `market` | String | US | Market (from `/configs`) |
| `sort` | String | QUALITY | `QUALITY` (Best), `PRICE` (Cheapest), `DURATION` (Fastest), `SOURCE_TAKEOFF` (Earliest departure), `DESTINATION_LANDING` (Earliest arrival) |
| `cabinBaggage` | Number | 0 | Max = passengers x 1 |
| `checkedBaggage` | Number | 0 | Max = passengers x 2 |
| `allowOvernightStopovers` | Boolean | true | — |
| `minPrice` | Number | 0 | Min price filter |
| `maxPrice` | Number | 0 | Max price filter |
| `inboundDepartureTimes` | String | — | Min,max hours (e.g. `1, 24`) |
| `inboundArrivalTimes` | String | — | Min,max hours (e.g. `1, 24`) |
| `outboundDepartureTimes` | String | — | Min,max hours (e.g. `1, 24`) |
| `outboundArrivalTimes` | String | — | Min,max hours (e.g. `1, 24`) |
| `maxDuration` | Number | 0 | Max flight duration |
| `stopoverTime` | String | — | Min,max hours (e.g. `1, 24`) |
| `carriers` | String | — | IATA codes comma-separated (from `/airlines`) |
| `selfTransferToDifferentStationOrAirport` | Boolean | true | — |
| `allowReturnFromDifferentStationOrAirport` | Boolean | true | — |
| `allowReturnToDifferentStationOrAirport` | Boolean | true | — |
| `selfTransfer` | Boolean | true | — |
| `throwAwayTicketing` | Boolean | true | — |
| `hiddenCity` | Boolean | true | — |
| `cabinClass` | String | ECONOMY | `ECONOMY`, `PREMIUM_ECONOMY`, `BUSINESS`, `FIRST_CLASS` |
| `applyMixedClasses` | Boolean | — | — |

---

### 2. `GET /flights/search-oneway` — One-way flight search

Same response structure as search-return but without `inbound`.

#### Required Params

| Param | Type | Description |
|---|---|---|
| `originSkyId` | String | Airport code or City ID |
| `destinationSkyId` | String | Airport code or City ID |

#### Optional Params

| Param | Type | Default | Description |
|---|---|---|---|
| `departureDate` | Date (YYYY-MM-DD) | current date | Earliest departure date |
| `departureDateEnd` | Date (YYYY-MM-DD) | — | Latest departure date (range search) |
| `stops` | Number | 0 | 0=Direct, 1=Up to 1 stop, 2=Up to 2 stops |
| `limit` | Number | 20 | Max results |
| `adults` | Number | 1 | — |
| `children` | Number | 0 | — |
| `infants` | Number | 0 | — |
| `currency` | String | USD | — |
| `locale` | String | en-US | — |
| `market` | String | US | — |
| `sort` | String | QUALITY | Same options as search-return |
| `cabinBaggage` | Number | 0 | — |
| `checkedBaggage` | Number | 0 | — |
| `allowOvernightStopovers` | Boolean | true | — |
| `minPrice` | Number | 0 | — |
| `maxPrice` | Number | 0 | — |
| `outboundDepartureTimes` | String | — | Min,max hours |
| `outboundArrivalTimes` | String | — | Min,max hours |
| `maxDuration` | Number | 0 | — |
| `stopoverTime` | String | — | Min,max hours |
| `carriers` | String | — | IATA codes comma-separated |
| `selfTransferToDifferentStationOrAirport` | Boolean | true | — |
| `selfTransfer` | Boolean | true | — |
| `throwAwayTicketing` | Boolean | true | — |
| `hiddenCity` | Boolean | true | — |
| `cabinClass` | String | ECONOMY | Same options as search-return |
| `applyMixedClasses` | Boolean | — | — |

**Differences from search-return**: No `returnDate`, `returnDateEnd`, `inboundDepartureTimes`, `inboundArrivalTimes`, `allowReturnFromDifferentStationOrAirport`, `allowReturnToDifferentStationOrAirport`.

---

### 3. `GET /flights/auto-complete` — Airport/city autocomplete

#### Params

| Param | Type | Description |
|---|---|---|
| `query` | String | Search text (e.g. `new york`) |

#### Response

Returns matching airports/cities with `code` and `id` fields used as `originSkyId`/`destinationSkyId`.

---

### 4. `GET /flights/price-table` — Price calendar table

#### Params

| Param | Type | Description |
|---|---|---|
| `originSkyId` | String | Airport code or City ID |
| `destinationSkyId` | String | Airport code or City ID |

---

### 5. `GET /flights/price-trends` — Price trend history

#### Params

| Param | Type | Description |
|---|---|---|
| `originSkyId` | String | Airport code or City ID |
| `destinationSkyId` | String | Airport code or City ID |

---

### 6. `GET /flights/seat-info` — Seat information

#### Params

| Param | Type | Description |
|---|---|---|
| `originSkyId` | String | Airport code |
| `destinationSkyId` | String | Airport code |
| `carrier` | String | Carrier code (e.g. `Z0`) |
| `code` | String | Flight code (e.g. `702`) |

---

### 7. `GET /airlines` — List all airlines

No params. Returns airline data with IATA codes.

---

### 8. `GET /airports` — List all airports

No params. Returns airport data.

---

### 9. `GET /configs` — Country/locale configuration

#### Params

| Param | Type | Description |
|---|---|---|
| `name` | String | Country name (e.g. `Andorra`) |

Returns `currency`, `locale`, `market` values for use in search params.

---

## Response Structure (search-return)

See `response_sample.json` for full example. Key structure:

```json
{
  "status": true,
  "status_code": 200,
  "totalResultCount": 18,
  "data": {
    "itineraries": [
      {
        "__typename": "ItineraryReturn",
        "outbound": {
          "sectorSegments": [
            {
              "segment": {
                "source": {
                  "station": { "code": "JFK", "name": "...", "city": { "name": "New York" }, "country": { "code": "US" }, "gps": { "lat": ..., "lng": ... } },
                  "localTime": "2026-03-02T19:25:00",
                  "utcTimeIso": "2026-03-03T00:25:00Z"
                },
                "destination": { "station": { ... }, "localTime": "...", "utcTimeIso": "..." },
                "duration": 20700,         // seconds
                "type": "FLIGHT",
                "code": "614",             // flight number
                "carrier": { "name": "Icelandair", "code": "FI" },
                "operatingCarrier": { "name": "Icelandair", "code": "FI" },
                "cabinClass": "ECONOMY"
              },
              "layover": {
                "duration": 5400,          // seconds
                "isBaggageRecheck": false,
                "isWalkingDistance": true
              }
            }
          ],
          "duration": 37800                // total sector duration in seconds
        },
        "inbound": { /* same structure as outbound */ },
        "price": { "amount": "778", "priceBeforeDiscount": "778" },
        "priceEur": { "amount": "658.32" },
        "provider": { "name": "Kiwi.com", "code": "KIWI-BASIC" },
        "bagsInfo": {
          "includedCheckedBags": 0,
          "includedHandBags": 1,
          "checkedBagTiers": [{ "tierPrice": { "amount": "241.09" }, "bags": [{ "weight": { "value": 23 } }] }],
          "handBagTiers": [...],
          "includedPersonalItem": 1,
          "personalItemTiers": [...]
        },
        "bookingOptions": {
          "edges": [{ "node": { "token": "...", "bookingUrl": "...", "price": { "amount": "778" }, "kiwiProduct": "KIWI_BASIC" } }]
        },
        "travelHack": { "isTrueHiddenCity": false, "isVirtualInterlining": false, "isThrowawayTicket": false },
        "stopover": { "nightsCount": 9, "arrival": { "city": { "name": "London" } }, "departure": { ... } },
        "lastAvailable": { "seatsLeft": 5 },
        "duration": 77700,                 // total itinerary duration in seconds
        "isVanilla": true,
        "pnrCount": 1
      }
    ]
  }
}
```

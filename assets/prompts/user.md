# travelprep-mcp User Tutorial

## Introduction

Welcome to travelprep-mcp. This tutorial walks you through planning a complete trip using the MCP tools available in this server. By the end of this tutorial you will know how to search for accommodation on both Airbnb and Booking.com, compare different hotels side by side, check availability and read reviews for specific properties, explore price calendars to find the cheapest dates, look up destination information including weather forecasts and practical travel facts, and access your Booking.com account to view saved properties and past trips.

The example scenario throughout this tutorial is planning a trip to Barcelona, Spain. We will assume a travel window of September 2026 for approximately seven nights.

## Getting Started

Before using any of the account tools, you will need to establish a Booking.com login session if you want to view your trips, wishlist, or rewards. This is a one-time setup step. The account tool's login operation opens a headed Playwright browser window at Booking.com's sign-in page. You log in using your Booking.com credentials through the normal browser interface. The session is then persisted to a local Playwright profile directory at ~/.travelprep-mcp/booking-profile/. Once this profile exists, all subsequent account operations run in headless mode using the saved cookies.

You can check whether a profile exists by calling account(operation="status"). This returns a simple boolean indicating whether the profile directory is present and non-empty. It does not confirm that the session is still valid on Booking.com's side, but it tells you whether you have a session to work with.

If you do not need account features, you can skip this setup entirely. All accommodation search and destination tools work without any authentication.

## Step 1: Searching for Accommodation

The first thing you will want to do is find places to stay. The stays tool handles this with its search operation. You need to specify which provider to search: either airbnb or booking. Each provider has different strengths and weaknesses.

For an initial broad search on Airbnb, you would call stays with operation="search", provider="airbnb", and the location set to "Barcelona, Spain". You can optionally include check-in and check-out dates, number of adults, and any children. The Airbnb provider also accepts min_price and max_price parameters for filtering by nightly rate.

The Airbnb provider uses Photon geocoding with a Nominatim fallback. This means the location matching is approximate rather than precise. A search for "Barcelona, Spain" will return results from a broad geographic area around Barcelona, not just the city centre. You should always inspect the coordinates returned with each listing to determine whether the property is actually where you want to be. Some results may be from suburbs, neighbouring towns, or even areas outside the metropolitan region.

For Booking.com searches, the check-in and check-out dates are required. The booking provider delegates to the hotelzero Playwright-based scraper, which is more fragile than the Airbnb provider. Booking.com actively fingerprints and blocks automated browsers. In testing, the first two search attempts were blocked before a third succeeded. The provider has built-in retry and backoff, but this means a search may sometimes return an error instead of results. If this happens, wait a minute and try again.

A typical Booking.com search looks like stays(operation="search", provider="booking", location="Barcelona, Spain", checkin="2026-09-01", checkout="2026-09-08", adults=2). This searches for two adults staying in Barcelona for one week starting September 1st.

## Step 2: Getting Detailed Information

Once you have search results and have identified a few promising listings, you can retrieve detailed information about each one using the stays tool's details operation. You need the listing ID, which varies by provider. For Airbnb listings, the listing ID is the numeric property ID that appears in search results and in the Airbnb URL. For Booking.com properties, the listing ID is the full hotel URL from booking.com, typically something like https://www.booking.com/hotel/es/barcelona-marriott-example.

For Airbnb, calling stays(operation="details", provider="airbnb", listing_id="12345678", checkin="2026-09-01", checkout="2026-09-08", adults=2) returns detailed information about property 12345678 including the full description, amenity list, host details, exact location, pricing breakdown, and house rules.

For Booking.com, calling stays(operation="details", provider="booking", listing_id="https://www.booking.com/hotel/es/barcelona-marriott-example") returns hotel details including star rating, property overview, key amenities, location map, and policies.

The details response structure varies by provider because each underlying scraper returns different data shapes. There is no unified schema across providers. You should read the actual response fields rather than assuming a consistent format.

## Step 3: Using Hotel Extras

The hotel_extras tool provides Booking.com-specific operations that go beyond basic search and details. These are all powered by the same hotelzero subprocess.

If you want a filtered search with specific criteria, use hotel_extras with operation="find_hotels". This accepts location, checkin, checkout, adults, rooms, and an optional filters dictionary. The filters dictionary is passed through directly to hotelzero's find_hotels tool, which supports over 80 filter codes. For example, you could filter by property type, star rating, guest rating score, free cancellation, breakfast included, and many other criteria. The specific filter keys are documented in hotelzero's README on GitHub.

If you have found two or three hotels and want to compare them directly, use hotel_extras with operation="compare" and provide a list of 2-3 Booking.com hotel URLs. This returns a side-by-side comparison showing rates, amenities, policies, and ratings for all properties at once. This is much faster than manually switching between detail views.

Before booking, you should check that the hotel actually has rooms available for your dates. Use hotel_extras with operation="check_availability", providing the hotel URL, check-in date, and check-out date. This returns whether rooms are available and what rates apply. You can also specify the number of adults and rooms.

To read what other guests have said about a property, use hotel_extras with operation="reviews". You need the hotel URL. You can optionally sort reviews by criteria such as "recent" or "highest score", and filter by reviewer type or language. This is useful for checking whether recent guests have had experiences consistent with the overall rating.

To find the cheapest time to visit a specific hotel, use hotel_extras with operation="price_calendar". This requires the hotel URL and a start date. The optional price_calendar_nights parameter (default 14) controls how many nights of pricing to scan. The tool returns nightly rates across the window so you can identify the cheapest dates. For example, hotel_extras(operation="price_calendar", hotel_url="https://www.booking.com/hotel/es/barcelona-marriott-example", price_calendar_start="2026-09-01", price_calendar_nights=21) would show rates from September 1st through September 21st, helping you pick the most affordable nights within that period.

Every hotel_extras result includes a budget_caps section echoing the hardcoded spend limits of 300 EUR per night and 1500 EUR per total trip. These are informative reference values, not automated enforcement. Use them as a quick sanity check when reviewing results.

## Step 4: Destination Information

Beyond just where to sleep, you need to know what a place is like, what the weather will be, and practical details like currency and language. The destination tool provides all of this from free, keyless sources.

For a general overview of Barcelona, use destination(operation="overview", place="Barcelona"). This fetches a Wikipedia summary including the city's description, notable landmarks, population statistics, and the desktop Wikipedia URL for further reading. The result also includes a thumbnail URL when available.

To check the weather for your travel dates, use destination(operation="weather", place="Barcelona", forecast_days=7). This geocodes the place name through Open-Meteo and returns a multi-day forecast. The weather data includes daily high and low temperatures in Celsius, precipitation probability as a percentage, and a weather code. Open-Meteo provides forecasts up to 16 days out, but accuracy decreases for longer ranges, so requesting more than 7-10 days may return increasingly unreliable data.

For practical travel information, use destination(operation="practical", place="Barcelona"). This looks up the Wikivoyage travel guide page for the city, which contains practical tips about getting around, safety, costs, and neighbourhoods. It also resolves the country through geocoding and queries REST Countries for Spain's currency (EUR), official languages (Spanish, Catalan), calling code (+34), capital (Madrid), region (Europe), and timezones.

If you want everything at once, use destination(operation="full", place="Barcelona", forecast_days=7). This combines the overview, weather, and practical sections into a single response. The tool runs all three fetches concurrently within a single httpx client session for efficiency, so response time is close to the slowest individual lookup rather than the sum of all three.

The destination tool is honest about missing data. If you were planning a trip to an extremely small village, Wikivoyage may not have a travel guide page for it. In that case, the practical section returns available: false with a reason explaining that no Wikivoyage page was found. The overview may still work if Wikipedia has an article about the village, and the weather will work as long as Open-Meteo can geocode the name. No data is ever fabricated. Every section independently reports its own availability.

## Step 5: Account Management

If you have an existing Booking.com account with saved properties or past trips, you can access them through the account tool.

First-time setup requires running account(operation="login"). This opens a headed Chromium window through Playwright at Booking.com's sign-in page. You complete the login process in that window just as you would in any browser. The session cookies are saved to the local Playwright profile directory. The tool waits up to 300 seconds for the login to complete. Once you have logged in successfully and the tool detects the logged-in state, the session is persisted for future use.

After the session is established, you can run account(operation="status") to confirm the profile exists. This does not verify that the session is still valid on Booking.com's server side, but it confirms there is a session to attempt to use.

Your past and upcoming bookings are accessible via account(operation="trips"). This navigates to Booking.com's mytrips.html page within the persisted Playwright session. The response includes raw page data from the Booking.com account page. Please note that this parsing logic is a first pass based on expected markup conventions and has not been verified against a real account. The response includes the raw HTML excerpt for debugging if the structured parsing fails.

Your saved properties are accessible via account(operation="wishlist"). This navigates to Booking.com's mywishlist.html page. The same caveat applies -- the parsing is unverified against real markup.

Your Genius loyalty level, wallet balance, and other rewards information is accessible via account(operation="rewards"). This navigates to Booking.com's rewards_and_wallet.html page.

## Step 6: Putting It All Together

Here is a complete workflow for planning a Barcelona trip using all four tools in sequence.

Start by getting destination information to understand the city. Call destination(operation="full", place="Barcelona", forecast_days=7) to get the overview, weather for the next week, and practical information about Spain's currency, language, and calling code. Read the overview to learn about Barcelona's districts and which neighbourhoods might suit your trip.

Next, search for accommodation on both providers. Call stays(operation="search", provider="airbnb", location="Barcelona, Spain", checkin="2026-09-01", checkout="2026-09-08", adults=2) for Airbnb results. Then call stays(operation="search", provider="booking", location="Barcelona, Spain", checkin="2026-09-01", checkout="2026-09-08", adults=2) for Booking.com results. Compare the results from both providers to get a broad view of what is available.

Shortlist the most promising options. For each one, get details using the appropriate provider. For Airbnb properties, call stays(operation="details", provider="airbnb", listing_id="12345678"). For Booking.com properties, call stays(operation="details", provider="booking", listing_id="https://www.booking.com/hotel/es/property-url").

If you are considering Booking.com hotels, use hotel_extras to go deeper. Read reviews with hotel_extras(operation="reviews", hotel_url="https://www.booking.com/hotel/es/property-url"). Check availability with hotel_extras(operation="check_availability", hotel_url="https://www.booking.com/hotel/es/property-url", checkin="2026-09-01", checkout="2026-09-08"). Find the cheapest dates with hotel_extras(operation="price_calendar", hotel_url="https://www.booking.com/hotel/es/property-url", price_calendar_start="2026-09-01"). Compare two or three hotels side by side with hotel_extras(operation="compare", hotel_urls=["https://www.booking.com/hotel/es/hotel-a", "https://www.booking.com/hotel/es/hotel-b"]).

If you have a Booking.com account, check your saved wishlist for any Barcelona properties you may have bookmarked previously using account(operation="wishlist"). Check your past trips to Barcelona for any hotels you have stayed at before using account(operation="trips").

Finally, use the budget module's logic independently by calling budget.within_budget(nightly_rate=250.0, nights=7) to verify that a candidate property falls within the hardcoded caps of 300 EUR per night and 1500 EUR total. Note that the server itself does not enforce these caps -- they are informational reference values.

## Error Handling and Recovery

The server is designed to fail transparently rather than fabricate data. You may encounter several categories of errors.

Validation errors occur when you call a tool with missing required parameters. For example, calling hotel_extras with operation="find_hotels" but without location returns a ValueError explaining that find_hotels requires location, checkin, and checkout. Always check that you have provided all required parameters for your chosen operation.

Provider errors occur when the underlying scraper encounters an issue. Booking.com search may fail with a bot-detection error. In this case, wait at least thirty seconds and retry. The underlying hotelzero provider has its own retry logic, but it may exhaust its retries. If the error persists, try the Airbnb provider instead for the same location.

Source errors occur when a destination data source is unavailable. If Open-Meteo's free API is rate-limited or temporarily down, the weather section returns available: false. If Wikivoyage does not have a page for a specific location, the practical section returns available: false. The server never guesses or synthesizes data. If a section reports unavailable, either try a different query or accept that the data source does not cover that particular location.

Account errors occur when the Booking.com session has expired or is invalid. The trips, wishlist, and rewards operations will detect a redirect to the sign-in page and return an error with detail not_logged_in. In this case, rerun account(operation="login") to establish a fresh session. Note that Booking.com may expire sessions more aggressively than regular websites due to their fraud detection measures.

## Limitations and Known Issues

Airbnb location matching is approximate. The underlying geocoder uses Photon with Nominatim fallback and applies a 25% bounding box padding. A search for "Barcelona" may include results from nearby towns such as L'Hospitalet de Llobregat or Badalona. Always check the coordinates of returned listings to confirm the actual location.

Booking.com bot detection is aggressive. The Playwright-based scraper behind hotelzero is actively fingerprinted and blocked. Expect occasional failures and plan for retries. Do not make rapid repeated calls to booking provider tools.

Account parsing is unverified. The trips, wishlist, and rewards operations were written without access to a real logged-in Booking.com account. All CSS selectors and JSON extraction patterns are informed guesses based on Booking.com's known UI conventions and the booking-com-pp-cli documentation. These have not been confirmed against live markup. Treat the structured output from these operations as provisional until confirmed with a real session.

The server has no booking-execution capability. This is intentional. You can search, inspect, compare, view price calendars, check availability, and read reviews, but you cannot complete a purchase through this server. Booking must be done manually through the Airbnb or Booking.com website.

Budget caps are informational only. The hardcoded caps of 300 EUR per night and 1500 EUR per trip are echoed in every hotel_extras result for your reference, but no tool enforces them. You are responsible for deciding whether a price is acceptable.

The web interface is a scaffold only. A Vite React webapp exists in the webapp directory but has zero pages. All interaction is through the MCP tool interface. The webapp is not yet functional for user-facing use.

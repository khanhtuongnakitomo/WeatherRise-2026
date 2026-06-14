import json
from agents.context_agents.tourism_agent.trip_context_planner import build_trip_plan
from agents.context_agents.context_assembler import assemble_context
from agents.context_agents.context_gap_report import ContextGapReport
from apps.api.app.schemas.context_schema import ParserOutput, MCPContext, TripRequest, TimeRange

def run_antigravity_validation_pass(payload: dict) -> bool:
    """
    Enforces systemic validation over AntiGravity optimization parameters.
    Returns True if the output payload matches strict scheduling requirements.
    """
    days = payload.get("mcp_context", {}).get("trip_plan_context", {}).get("days", [])
    if not days:
        raise AssertionError("Validation Failure: Itinerary data is empty or missing.")

    for day in days:
        stops = day.get("stops", [])
        
        # 1. Enforce Triple-Meal Rule Constancy
        meals = [s for s in stops if s.get("category") == "restaurant"]
        if len(meals) != 3:
            raise AssertionError(f"Biological Breach on Day {day['day']}: Found {len(meals)} meals instead of 3. Stops: {stops}")
            
        # 2. Verify Meal Block Sequences
        if meals[0]["time_block"] != "breakfast" or meals[1]["time_block"] != "lunch" or meals[2]["time_block"] != "dinner":
            raise AssertionError(f"Meal Sequencing Failure on Day {day['day']}: Dining blocks are out of order.")

        # 3. Verify Late-Night Eviction Constraints
        for stop in stops:
            if stop.get("time_block") == "evening_relaxation" and not stop.get("is_indoor", False):
                raise AssertionError(f"Safety Hazard Exception: Outdoor attraction scheduled during late-night relaxation window.")
                
            # 4. Confirm Absolute Token Compressions
            corrupted_keys = {"reviews", "description", "long_tags", "cosmetic_metadata", "vibe_tags", "duration_minutes"}
            if any(key in stop for key in corrupted_keys):
                raise AssertionError(f"Token Bloat Failure: Cosmetic metadata fields leaked into optimized schema layout. Found in: {stop.keys()}")

    return True

if __name__ == "__main__":
    attractions = [
        {"place_id": "a1", "name": "Beach", "latitude": 16.0, "longitude": 108.2, "is_indoor": False, "category": "attraction"},
        {"place_id": "a2", "name": "Museum", "latitude": 16.0, "longitude": 108.2, "is_indoor": True, "category": "attraction"},
        {"place_id": "a3", "name": "Night Market", "latitude": 16.0, "longitude": 108.2, "is_indoor": False, "category": "attraction"},
        {"place_id": "a4", "name": "Park", "latitude": 16.0, "longitude": 108.2, "is_indoor": False, "category": "attraction"},
        {"place_id": "a5", "name": "Bridge", "latitude": 16.0, "longitude": 108.2, "is_indoor": False, "category": "attraction"},
    ]
    restaurants = [
        {"place_id": f"r{i}", "name": f"Rest {i}", "latitude": 16.0, "longitude": 108.2, "is_indoor": True, "category": "restaurant"} for i in range(15)
    ]
    
    trip_plan = build_trip_plan(attractions, restaurants, 2)
    
    parsed = ParserOutput(
        domain="tourism",
        intent="general",
        intent_subtype="multi_day_trip_planning",
        raw_user_input="Test",
        time_range=TimeRange(start="2026-07-01", end="2026-07-02"),
        trip_request=TripRequest(duration_days=2)
    )
    mcp_ctx = MCPContext(trip_plan_context=trip_plan, places=attractions, restaurants=restaurants)
    mcp_ctx.weather_forecast = {
        "output": {
            "daily_forecasts": [
                {"date": "2026-07-01", "max_rain_prob_pct": 10, "min_temp_c": 25, "max_temp_c": 30, "hourly": [{"hour": "08:00", "temp_c": 26, "rain_prob_pct": 5, "weather_label": "Sunny"}]},
                {"date": "2026-07-02", "max_rain_prob_pct": 80, "min_temp_c": 24, "max_temp_c": 28, "hourly": [{"hour": "08:00", "temp_c": 25, "rain_prob_pct": 80, "weather_label": "Rainy"}]},
            ]
        }
    }
    
    gap = ContextGapReport(domain="tourism", location="Da Nang", required_context=[], found_context={}, missing_context=[])
    payload = assemble_context(parsed, mcp_ctx, gap)
    
    payload_dict = payload.model_dump()
    
    print("Testing payload...")
    if run_antigravity_validation_pass(payload_dict):
        print("Success! Validation passed.")
    else:
        print("Validation failed.")

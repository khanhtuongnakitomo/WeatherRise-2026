import asyncio
from apps.api.app.schemas.context_schema import FullyProcessedPayload
from agents.intelligence_layer.intelligence_service import IntelligenceService
import json

payload = {
  "domain": "tourism",
  "intent": "travel_planning",
  "location": "Hoi An",
  "geographical_location": {"coordinates": {"latitude": 15.88, "longitude": 108.33}},
  "time_range": {"start": "2026-06-14", "end": "2026-06-14"},
  "involved_context": ["weather_forecast"],
  "mcp_context": {
      "weather_forecast": {
          "output": {
              "daily_forecasts": [
                  {"date": "2026-06-14", "temperature": {"max_c": 35, "min_c": 27}, "rain_probability": 80, "precipitation_mm": 15}
              ]
          }
      }
  },
  "intelligence_requirements": {"realtime_weather_needed": True, "weather_variables": ["rain_probability", "temperature"]}
}

async def main():
    service = IntelligenceService()
    parsed_payload = FullyProcessedPayload(**payload)
    output = await service.process(parsed_payload)
    print("=== NIM OUTPUT ===")
    print(output.metadata.get("llm_source"))
    print(output.metadata.get("llm_error"))
    print("=== QWEN OUTPUT ===")
    print(output.metadata.get("localization_source"))
    print(output.metadata.get("localization_error"))
    print("=== EXPLANATION ===")
    print(output.explanation)

asyncio.run(main())

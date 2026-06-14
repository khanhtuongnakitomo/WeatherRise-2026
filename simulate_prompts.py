import json
import os
from pathlib import Path
from agents.intelligence_layer.prompt_builder import NIMPromptBuilder

# ... (rest of imports remain the same in the file but I need to replace the specific line)
from agents.intelligence_layer.schemas import FullyProcessedJSON, CanonicalWeatherData, PredictionResult
from apps.api.app.schemas.context_schema import ParserOutput, MCPContext, TripRequest, TimeRange
from agents.context_agents.context_gap_report import ContextGapReport
from agents.context_agents.tourism_agent.trip_context_planner import build_trip_plan

def main():
    repo_root = Path(__file__).parent
    benchmark_dir = repo_root / "agents" / "intelligence_layer" / "benchmark"
    cases_path = benchmark_dir / "benchmark_cases" / "path_a_cases.json"
    
    with open(cases_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    attractions = [
        {"place_id": "a1", "name": "Beach", "latitude": 16.0, "longitude": 108.2, "is_indoor": False, "category": "attraction"},
        {"place_id": "a2", "name": "Museum", "latitude": 16.0, "longitude": 108.2, "is_indoor": True, "category": "attraction"},
    ]
    restaurants = [
        {"place_id": f"r{i}", "name": f"Rest {i}", "latitude": 16.0, "longitude": 108.2, "is_indoor": True, "category": "restaurant"} for i in range(5)
    ]
    trip_plan = build_trip_plan(attractions, restaurants, 1)
    
    parsed = ParserOutput(
        domain="tourism",
        intent="general",
        intent_subtype="multi_day_trip_planning",
        raw_user_input="Test",
        time_range=TimeRange(start="2026-07-01", end="2026-07-02"),
        trip_request=TripRequest(duration_days=1)
    )
    mcp_ctx = MCPContext(trip_plan_context=trip_plan, places=attractions, restaurants=restaurants)
    gap = ContextGapReport(domain="tourism", location="Da Nang", required_context=[], found_context={}, missing_context=[])
    from agents.context_agents.context_assembler import assemble_context
    payload = assemble_context(parsed, mcp_ctx, gap)
    trip_plan_context = payload.model_dump().get("mcp_context", {})

    output_lines = []
    
    for case in cases:
        fp_path = benchmark_dir / case["fully_processed_json_path"]
        with open(fp_path, "r", encoding="utf-8") as f:
            fp_data = json.load(f)
            
        # INJECT the missing realistic itinerary
        fp_data["mcp_context"] = trip_plan_context
        
        cw_path = benchmark_dir / case["canonical_weather_json_path"]
        with open(cw_path, "r", encoding="utf-8") as f:
            cw_data = json.load(f)
            
        # We need a dummy prediction result
        pr_dict = {
            "domain": case["domain"],
            "prediction_summary": "Simulated prediction summary",
            "recommendation_summary": "Simulated recommendation summary",
            "risk_assessment": {"overall_risk": "low"},
            "evidence": ["Evidence 1"]
        }
        
        fp_obj = FullyProcessedJSON(**fp_data)
        cw_obj = CanonicalWeatherData(**cw_data)
        pr_obj = PredictionResult(**pr_dict)
        
        builder = NIMPromptBuilder()
        prompt_messages = builder.build_path_a_prompt(fp_obj, cw_obj, pr_obj)
        
        # The prompt messages list contains {"role": "system", ...} and {"role": "user", "content": <json string>}
        user_message_content = json.loads(prompt_messages[1]["content"])
        
        output_lines.append(f"=== Case: {case['case_id']} ===")
        output_lines.append(json.dumps(user_message_content, indent=2))
        output_lines.append("\n")
        
    out_file = repo_root / "simulated_prompts_output.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        
    print(f"Simulated prompts saved to {out_file}")

if __name__ == "__main__":
    main()

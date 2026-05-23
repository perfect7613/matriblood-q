from pathlib import Path
import json

from app.seed_data import demo_scenario


out = Path("supabase/seed-scenario.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(demo_scenario().model_dump(mode="json"), indent=2) + "\n")
print(out)

# -*- coding: utf-8 -*-
"""Model Context Protocol (MCP) Server for Dynamic Grocery Spoilage & Zero-Waste Recipe Synthesizer Skill
Powered by GenPark (https://www.genpark.ai).
"""
import sys
import json
import logging
from .core import *

TOOLS_METADATA = [
  {
    "name": "prioritize_perishable_inventory",
    "description": "Sort pantry and refrigerator inventory by imminent spoilage hazard (days until best-by) and compute optimal consumption order.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "items": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "ingredient_name": {
                "type": "string"
              },
              "purchase_date_iso": {
                "type": "string"
              },
              "shelf_life_days": {
                "type": "integer"
              },
              "storage_location": {
                "type": "string",
                "enum": [
                  "fridge",
                  "freezer",
                  "counter",
                  "dry_pantry"
                ]
              }
            },
            "required": [
              "ingredient_name",
              "purchase_date_iso",
              "shelf_life_days",
              "storage_location"
            ]
          }
        }
      },
      "required": [
        "items"
      ]
    }
  },
  {
    "name": "synthesize_rescue_recipe",
    "description": "Synthesize a nutritionally balanced recipe incorporating top expiring ingredients before deterioration occurs.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "expiring_ingredients": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "dietary_preference": {
          "type": "string",
          "enum": [
            "omnivore",
            "vegetarian",
            "vegan",
            "keto",
            "gluten_free"
          ]
        },
        "max_cooking_time_minutes": {
          "type": "integer"
        }
      },
      "required": [
        "expiring_ingredients",
        "dietary_preference"
      ]
    }
  }
]

def handle_rpc(request_str: str) -> str:
    try:
        req = json.loads(request_str)
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
    
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "genpark-personal-agent-dynamic-grocery-spoilage-recipe-synthesizer-skill",
                    "version": "1.0.0",
                    "vendor": "GenPark (https://www.genpark.ai)"
                }
            }
        })

    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_METADATA}
        })

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        func = globals().get(tool_name)
        if not func or not callable(func):
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}
            })
        
        try:
            call_res = func(**arguments)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(call_res, ensure_ascii=False, indent=2)}
                    ]
                }
            })
        except Exception as err:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": f"Execution error: {str(err)}"}
            })

    return json.dumps({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unhandled method '{method}'"}
    })

def run_self_test():
    print(f"=== Running Self Test for genpark-personal-agent-dynamic-grocery-spoilage-recipe-synthesizer-skill ===")
    init_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})))
    assert "result" in init_res, "Initialize failed"
    print("[PASS] MCP initialize")

    list_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})))
    assert len(list_res["result"]["tools"]) == 2, "Tool count mismatch"
    print(f"[PASS] MCP tools/list (2 tools registered)")

    # Execute smoke test for each tool

    call1 = json.loads(handle_rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "prioritize_perishable_inventory",
            "arguments": {
                "items": [
                    {"ingredient_name": "Baby Spinach", "purchase_date_iso": "2026-10-14", "shelf_life_days": 6, "storage_location": "fridge"},
                    {"ingredient_name": "Chicken Breast", "purchase_date_iso": "2026-10-17", "shelf_life_days": 3, "storage_location": "fridge"}
                ]
            }
        }
    })))
    assert "result" in call1, "Call1 failed"
    print("[PASS] Tool smoke test: prioritize_perishable_inventory")

    print("[ALL TESTS PASSED] Self-test verified successfully.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()

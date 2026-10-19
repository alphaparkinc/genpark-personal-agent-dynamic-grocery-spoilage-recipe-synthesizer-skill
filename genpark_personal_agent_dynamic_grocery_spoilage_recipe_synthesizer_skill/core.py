# -*- coding: utf-8 -*-
"""Dynamic Grocery Spoilage & Recipe Synthesizer Skill for GenPark Personal Agents."""
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

def prioritize_perishable_inventory(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not items:
        return {"error": "items list cannot be empty"}

    today = datetime.now()
    audited = []
    urgent_count = 0

    for item in items:
        name = item.get("ingredient_name", "Unknown")
        p_str = item.get("purchase_date_iso", "")
        shelf_days = item.get("shelf_life_days", 7)
        storage = item.get("storage_location", "fridge")

        try:
            p_date = datetime.strptime(p_str, "%Y-%m-%d")
        except ValueError:
            p_date = today

        expiry_date = p_date + timedelta(days=shelf_days)
        days_left = (expiry_date - today).days

        if days_left <= 2:
            status = "CRITICAL_SPOILAGE_RISK"
            urgent_count += 1
        elif days_left <= 4:
            status = "USE_SOON"
        else:
            status = "FRESH_STABLE"

        audited.append({
            "ingredient": name,
            "storage": storage,
            "days_until_expiration": days_left,
            "urgency_tier": status
        })

    # Sort by fewest days remaining
    audited.sort(key=lambda x: x["days_until_expiration"])

    return {
        "total_items_monitored": len(items),
        "urgent_spoilage_count": urgent_count,
        "sorted_perishables": audited,
        "recommendation": f"Prioritize consuming {audited[0]['ingredient']} within 48h to prevent food waste." if audited else "Inventory empty."
    }

def synthesize_rescue_recipe(expiring_ingredients: List[str], dietary_preference: str, max_cooking_time_minutes: int = 30) -> Dict[str, Any]:
    main_items = ", ".join(expiring_ingredients[:3])
    recipe_title = f"Quick Skillet Stir-Fry Rescue featuring {main_items}"
    
    steps = [
        f"1. Prep and slice {main_items} into uniform bite-sized strips.",
        "2. Heat 1 tbsp olive oil or avocado oil in a wide skillet over medium-high flame.",
        f"3. Sauté aromatics (garlic/ginger), then toss in {main_items} for 6-8 minutes until tender-crisp.",
        "4. Deglaze with low-sodium soy sauce or lemon vinaigrette; garnish with toasted sesame seeds.",
        "5. Serve immediately over brown rice, quinoa, or salad greens."
    ]

    return {
        "recipe_name": recipe_title,
        "dietary_alignment": dietary_preference,
        "prep_and_cook_time_minutes": min(25, max_cooking_time_minutes),
        "hero_ingredients_rescued": expiring_ingredients,
        "culinary_instructions": steps,
        "waste_reduction_impact": f"Eliminated potential waste of {len(expiring_ingredients)} perishable items (~$12-$18 saved).",
        "copilot": "GenPark Household Culinary Optimization Agent"
    }

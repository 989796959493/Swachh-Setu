"""Waste knowledge base: maps a classifier label to bin guidance and circular-economy tips.

Bin colours follow the common Indian 3-bin system: green = wet/biodegradable,
blue = dry, black = domestic hazardous. Edit freely to match your model's labels.
"""

CATEGORY_META = {
    "wet": {"label": "Wet waste", "bin": "Green bin", "color": "#2e9e5b"},
    "dry": {"label": "Dry waste", "bin": "Blue bin", "color": "#2f6fdb"},
    "hazardous": {"label": "Hazardous", "bin": "Black bin (hand over separately)", "color": "#3a3a3a"},
    "ewaste": {"label": "E-waste", "bin": "Authorised e-waste collection point", "color": "#8a4fd3"},
    "reject": {"label": "Non-recyclable", "bin": "Dry-waste reject stream", "color": "#8c8c8c"},
}

WASTE_INFO = {
    "cardboard": {
        "category": "dry", "recyclable": True,
        "tip": "Flatten it and keep it dry. Wet cardboard loses its recycling value.",
        "reuse": "Reuse as packing material, drawer dividers or a compost layer.",
    },
    "paper": {
        "category": "dry", "recyclable": True,
        "tip": "Keep it clean and dry; greasy or food-stained paper is not recyclable.",
        "reuse": "Use the blank side for rough work or sell it to a local kabadiwala.",
    },
    "plastic": {
        "category": "dry", "recyclable": True,
        "tip": "Rinse bottles and containers, crush them and cap them before binning.",
        "reuse": "Reuse bottles and tubs for storage or planters before recycling.",
    },
    "metal": {
        "category": "dry", "recyclable": True,
        "tip": "Rinse cans. Metal is infinitely recyclable and has good scrap value.",
        "reuse": "Tins make good pen stands and seed pots.",
    },
    "glass": {
        "category": "dry", "recyclable": True,
        "tip": "Wrap broken glass in newspaper and label it to protect waste workers.",
        "reuse": "Jars are ideal for pantry storage or candle holders.",
    },
    "organic": {
        "category": "wet", "recyclable": True,
        "tip": "Put it in the green bin or a home compost pit.",
        "reuse": "Compost it to make manure for plants; fruit peels can become bio-enzyme cleaner.",
    },
    "biological": {
        "category": "wet", "recyclable": True,
        "tip": "Put it in the green bin or a home compost pit.",
        "reuse": "Compost it to make manure for plants.",
    },
    "battery": {
        "category": "hazardous", "recyclable": True,
        "tip": "Never put batteries in regular bins. They leak toxic metals and can start fires.",
        "reuse": "Hand them to a battery take-back point or an authorised recycler.",
    },
    "e-waste": {
        "category": "ewaste", "recyclable": True,
        "tip": "Do not burn or dump electronics. They contain lead, mercury and valuable metals.",
        "reuse": "Donate working devices; give broken ones to an authorised e-waste recycler.",
    },
    "clothes": {
        "category": "dry", "recyclable": True,
        "tip": "Donate wearable clothes; the rest can go to textile recyclers.",
        "reuse": "Old cotton clothes make cleaning rags, bags and cushion fillers.",
    },
    "shoes": {
        "category": "dry", "recyclable": True,
        "tip": "Donate wearable pairs; worn-out ones go in the dry-waste stream.",
        "reuse": "Old shoes can be turned into planters.",
    },
    "trash": {
        "category": "reject", "recyclable": False,
        "tip": "This item is not easily recyclable. Keep it away from wet waste.",
        "reuse": "Reduce at the source: pick refillable or reusable alternatives next time.",
    },
}

DEFAULT_INFO = {
    "category": "reject", "recyclable": False,
    "tip": "Not sure about this item. Keep it separate and check with your local waste collector.",
    "reuse": "Try to reuse it before discarding.",
}


def describe(label: str) -> dict:
    """Return guidance for a label, merged with category metadata."""
    info = dict(WASTE_INFO.get(label.lower(), DEFAULT_INFO))
    meta = CATEGORY_META[info["category"]]
    info.update({
        "label": label,
        "category_label": meta["label"],
        "bin": meta["bin"],
        "color": meta["color"],
    })
    return info

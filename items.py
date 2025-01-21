import random

# Update sacred artifact abilities with specific names
sacred_artifact_abilities = [
    {
        "name": "Warrior's Medallion",
        "description": "An ancient medallion pulsing with martial energy",
        "type": "stat_boost",
        "stat": "Strength",
        "boost": 2
    },
    {
        "name": "Fertile Earth Charm",
        "description": "A mystical charm that resonates with natural energy",
        "type": "farming",
        "growth_reduction": 2
    },
    {
        "name": "Ancient Warrior's Weapon",
        "description": "A perfectly preserved weapon of mysterious origin",
        "type": "weapon",
        "damage": random.randint(3, 7),
        "weapon_type": random.choice(['melee', 'ranged'])
    }
]

treasure_types = [
    {"name": "Golden Idol", "value": 2000},
    {"name": "Ancient Coins", "value": 1500},
    {"name": "Jeweled Crown", "value": 3000},
    {"name": "Sacred Artifact", "value": 2500, "ability": random.choice(sacred_artifact_abilities)},
    {"name": "Royal Scepter", "value": 1800}
]

# Weapons available in the smithy
weapons = {
    'Cutlass': {
        'price': 200,
        'damage': 3,
        'type': 'melee'
    },
    'Pistol': {
        'price': 300,
        'damage': 4,
        'type': 'ranged'
    },
    'Musket': {
        'price': 400,
        'damage': 5,
        'type': 'ranged'
    },
    'Boarding Axe': {
        'price': 150,
        'damage': 2,
        'type': 'melee'
    },
    'Ship Cannon': {
        'price': 800,
        'damage': 8,
        'type': 'ship',
        'cargo_space': 2,
        'description': 'Heavy cannon for ship combat'
    },
    'Swivel Gun': {
        'price': 500,
        'damage': 6,
        'type': 'ship',
        'cargo_space': 1,
        'description': 'Light, maneuverable ship cannon'
    }
}

# Trade goods available in the market
trade_goods = {
    'Food': {
        'price': 50,
        'barrels': 1,
        'description': '1 barrel of preserved food'
    },
    'Seeds': {
        'price': 30,
        'barrels': 1,
        'description': '1 barrel of planting seeds'
    },
    'Spices': {
        'price': 100,
        'barrels': 1,
        'description': '1 barrel of exotic spices'
    },
    'Cloth': {
        'price': 80,
        'barrels': 1,
        'description': '1 barrel of fine cloth'
    },
    'Rum': {
        'price': 120,
        'barrels': 1,
        'description': '1 barrel of Caribbean rum'
    },
    'Wood': {
        'price': 60,
        'barrels': 1,
        'description': '1 barrel of processed wood'
    },
    'Iron': {
        'price': 90,
        'barrels': 1,
        'description': '1 barrel of iron ingots'
    },
    'Gold': {
        'price': 150,
        'barrels': 1,
        'description': '1 barrel of gold bars'
    }
}

# Ship types and their stats
ship_types = {
    'Sloop': {
        'price': 1000,
        'crew_max': 10,
        'speed': 2,
        'cargo': 10,
        'hull_max': 30
    },
    'Brigantine': {
        'price': 2000,
        'crew_max': 15,
        'speed': 2,
        'cargo': 16,
        'hull_max': 45
    },
    'Galleon': {
        'price': 3000,
        'crew_max': 25,
        'speed': 1,
        'cargo': 24,
        'hull_max': 60
    }
} 
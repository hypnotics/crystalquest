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
    }
}

# Trade goods available in the market
trade_goods = {
    'Food': 50,
    'Seeds': 30,
    'Spices': 100,
    'Cloth': 80,
    'Rum': 120,
    'Wood': 60,
    'Iron': 90,
    'Gold': 150
}

# Ship types and their stats
ship_types = {
    'Sloop': {
        'price': 1000,
        'crew_max': 10,
        'speed': 2,
        'cargo': 5
    },
    'Brigantine': {
        'price': 2000,
        'crew_max': 15,
        'speed': 2,
        'cargo': 8
    },
    'Galleon': {
        'price': 3000,
        'crew_max': 25,
        'speed': 1,
        'cargo': 12
    }
} 
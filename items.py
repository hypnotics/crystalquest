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
"""
Constantes astrologiques pour Astrolog Python
Traduction complète des constantes d'Astrolog 7.80
"""

import math
from enum import Enum
from typing import Dict, List, Tuple

# Constantes mathématiques
PI = math.pi
DEGTORAD = PI / 180.0
RADTODEG = 180.0 / PI

# Planètes (correspondance avec Astrolog)
class Planet(Enum):
    SUN = 0
    MOON = 1
    MERCURY = 2
    VENUS = 3
    MARS = 4
    JUPITER = 5
    SATURN = 6
    URANUS = 7
    NEPTUNE = 8
    PLUTO = 9
    NODE = 10
    SOUTH_NODE = 11
    LILITH = 12
    CHIRON = 15
    CERES = 17
    PALLAS = 18
    JUNO = 19
    VESTA = 20

# Signes zodiacaux
ZODIAC_SIGNS = [
    "Bélier", "Taureau", "Gémeaux", "Cancer", "Lion", "Vierge",
    "Balance", "Scorpion", "Sagittaire", "Capricorne", "Verseau", "Poissons"
]

ZODIAC_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

# Éléments et modalités
ELEMENTS = {
    "Feu": [0, 4, 8],      # Bélier, Lion, Sagittaire
    "Terre": [1, 5, 9],    # Taureau, Vierge, Capricorne
    "Air": [2, 6, 10],     # Gémeaux, Balance, Verseau
    "Eau": [3, 7, 11]      # Cancer, Scorpion, Poissons
}

MODALITIES = {
    "Cardinal": [0, 3, 6, 9],    # Bélier, Cancer, Balance, Capricorne
    "Fixe": [1, 4, 7, 10],       # Taureau, Lion, Scorpion, Verseau
    "Mutable": [2, 5, 8, 11]     # Gémeaux, Vierge, Sagittaire, Poissons
}

# Aspects
ASPECTS = [
    {"name": "Conjonction", "angle": 0, "orb": 8, "type": "majeur", "score": 10},
    {"name": "Opposition", "angle": 180, "orb": 8, "type": "majeur", "score": -5},
    {"name": "Trigone", "angle": 120, "orb": 8, "type": "majeur", "score": 8},
    {"name": "Carré", "angle": 90, "orb": 8, "type": "majeur", "score": -6},
    {"name": "Sextile", "angle": 60, "orb": 6, "type": "majeur", "score": 6},
    {"name": "Quintile", "angle": 72, "orb": 2, "type": "mineur", "score": 3},
    {"name": "Biquintile", "angle": 144, "orb": 2, "type": "mineur", "score": 3},
    {"name": "Quincunce", "angle": 150, "orb": 3, "type": "mineur", "score": -2}
]

# Symboles planétaires
PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
    "Neptune": "♆", "Pluto": "♇", "Node": "☊", "Chiron": "⚷"
}

# Systèmes de maisons
HOUSE_SYSTEMS = {
    "Placidus": "P",
    "Koch": "K", 
    "Campanus": "C",
    "Regiomontanus": "R",
    "Equal": "E",
    "Porphyry": "O"
}

# Vitesses moyennes des planètes (degrés par jour)
PLANET_SPEEDS = {
    "Sun": 0.9856,
    "Moon": 13.1764,
    "Mercury": 1.3690,
    "Venus": 1.2019,
    "Mars": 0.5240,
    "Jupiter": 0.0831,
    "Saturn": 0.0335,
    "Uranus": 0.0117,
    "Neptune": 0.0060,
    "Pluto": 0.0040
}
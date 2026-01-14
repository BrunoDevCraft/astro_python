"""
Utilitaires mathématiques pour les calculs astrologiques
Traduction des fonctions utilitaires d'Astrolog
"""

import math
from typing import Tuple, List
from .constants import *

def normalize_angle(angle: float) -> float:
    """Normalise un angle entre 0 et 360 degrés"""
    while angle < 0:
        angle += 360
    while angle >= 360:
        angle -= 360
    return angle

def deg_to_dms(degrees: float) -> Tuple[int, int, float]:
    """Convertit degrés en degrés-minutes-secondes"""
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = ((degrees - d) * 60 - m) * 60
    return d, m, s

def dms_to_deg(d: int, m: int, s: float) -> float:
    """Convertit degrés-minutes-secondes en degrés"""
    return d + m/60 + s/3600

def get_zodiac_sign(longitude: float) -> Tuple[int, str, str]:
    """Retourne le signe zodiacal pour une longitude donnée"""
    sign_index = int(longitude // 30)
    degrees_in_sign = longitude % 30
    
    if sign_index >= 12:
        sign_index = 11
    elif sign_index < 0:
        sign_index = 0
    
    return sign_index, ZODIAC_SIGNS[sign_index], ZODIAC_SYMBOLS[sign_index]

def calculate_distance(angle1: float, angle2: float) -> float:
    """Calcule la distance angulaire minimum entre deux angles"""
    diff = abs(angle1 - angle2)
    return min(diff, 360 - diff)

def is_retrograde(speed: float) -> bool:
    """Détermine si une planète est rétrograde selon sa vitesse"""
    return speed < 0

def get_element(sign_index: int) -> str:
    """Retourne l'élément d'un signe"""
    for element, signs in ELEMENTS.items():
        if sign_index in signs:
            return element
    return ""

def get_modality(sign_index: int) -> str:
    """Retourne la modalité d'un signe"""
    for modality, signs in MODALITIES.items():
        if sign_index in signs:
            return modality
    return ""

def julian_day(year: int, month: int, day: int, hour: float = 0.0) -> float:
    """
    Calcule le jour julien (algorithme identique à Astrolog)
    """
    if month <= 2:
        year -= 1
        month += 12
    
    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)
    
    jd = (math.floor(365.25 * (year + 4716)) + 
          math.floor(30.6001 * (month + 1)) + 
          day + b - 1524.5)
    
    jd += hour / 24.0
    
    return jd

def gregorian_from_jd(jd: float) -> Tuple[int, int, int, float]:
    """
    Convertit un jour julien en date grégorienne
    """
    jd += 0.5
    z = math.floor(jd)
    w = math.floor((z - 1867216.25) / 36524.25)
    x = math.floor(w / 4)
    a = z + 1 + w - x
    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d = math.floor(365.25 * c)
    e = math.floor((b - d) / 30.6001)
    
    day = b - d - math.floor(30.6001 * e)
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    
    hour = (jd - math.floor(jd)) * 24
    
    return year, month, day, hour

def interpolate(x1: float, y1: float, x2: float, y2: float, x: float) -> float:
    """Interpolation linéaire"""
    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)

def quadratic_interpolate(x0: float, y0: float, x1: float, y1: float, 
                         x2: float, y2: float, x: float) -> float:
    """Interpolation quadratique"""
    # Formule de Lagrange
    term1 = y0 * (x - x1) * (x - x2) / ((x0 - x1) * (x0 - x2))
    term2 = y1 * (x - x0) * (x - x2) / ((x1 - x0) * (x1 - x2))
    term3 = y2 * (x - x0) * (x - x1) / ((x2 - x0) * (x2 - x1))
    
    return term1 + term2 + term3
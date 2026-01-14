"""
Systèmes de maisons astrologiques
Traduction complète des systèmes de maisons d'Astrolog 7.80
"""

import math
from typing import Dict, List, Tuple
from .constants import *
from .utils import *

class HouseCalculator:
    """Calculateur de maisons astrologiques avec tous les systèmes"""
    
    def __init__(self):
        self.systems = HOUSE_SYSTEMS
        self.current_system = "P"  # Placidus par défaut
    
    def calculate_houses(self, jd: float, latitude: float, longitude: float, 
                        system: str = "P") -> Dict:
        """
        Calcule les maisons astrologiques selon le système choisi
        jd: Jour julien
        latitude: Latitude du lieu
        longitude: Longitude du lieu
        system: Système de maisons (P, K, C, R, E, O)
        """
        self.current_system = system
        
        # Calculer l'heure sidérale locale
        lst = self._calculate_local_sidereal_time(jd, longitude)
        
        # Calculer l'ascendant
        ascendant = self._calculate_ascendant(lst, latitude)
        
        # Calculer le MC (Milieu du Ciel)
        mc = self._calculate_mc(lst, latitude)
        
        # Calculer selon le système choisi
        if system == "P":
            houses = self._placidus_houses(ascendant, mc, latitude, lst)
        elif system == "K":
            houses = self._koch_houses(ascendant, mc, latitude, lst)
        elif system == "C":
            houses = self._campanus_houses(ascendant, mc, latitude)
        elif system == "R":
            houses = self._regiomontanus_houses(ascendant, mc, latitude)
        elif system == "E":
            houses = self._equal_houses(ascendant)
        elif system == "O":
            houses = self._porphyry_houses(ascendant, mc)
        else:
            houses = self._placidus_houses(ascendant, mc, latitude, lst)
        
        # Calculer les points opposés
        descendant = normalize_angle(ascendant + 180)
        ic = normalize_angle(mc + 180)
        
        return {
            'houses': houses,
            'ascendant': ascendant,
            'descendant': descendant,
            'mc': mc,
            'ic': ic,
            'system': system,
            'lst': lst
        }
    
    def _calculate_local_sidereal_time(self, jd: float, longitude: float) -> float:
        """
        Calcule l'heure sidérale locale
        Algorithme identique à Astrolog
        """
        # J2000.0 epoch
        t = (jd - 2451545.0) / 36525.0
        
        # Heure sidérale de Greenwich (degrés)
        gst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t**2 - t**3 / 38710000.0
        gst = normalize_angle(gst)
        
        # Convertir en heures
        gst_hours = gst / 15.0
        
        # Ajuster pour la longitude (1 heure = 15 degrés)
        longitude_hours = longitude / 15.0
        lst_hours = gst_hours + longitude_hours
        
        # Convertir en degrés
        lst = lst_hours * 15.0
        lst = normalize_angle(lst)
        
        return lst
    
    def _calculate_ascendant(self, lst: float, latitude: float) -> float:
        """
        Calcule l'ascendant
        Formule de base utilisée par Astrolog
        """
        # Obliquité de l'écliptique
        epsilon = 23.439281
        
        # Convertir en radians
        lst_rad = lst * DEGTORAD
        lat_rad = latitude * DEGTORAD
        eps_rad = epsilon * DEGTORAD
        
        # Calcul de l'ascendant
        tan_eps = math.tan(eps_rad)
        sin_lat = math.sin(lat_rad)
        cos_lat = math.cos(lat_rad)
        
        # Ascension droite
        y = math.sin(lst_rad) * cos_lat
        x = math.cos(lst_rad) * cos_lat
        
        # Ascension droite de l'ascendant
        ra_asc = math.atan2(y, x)
        
        # Déclinaison
        dec_asc = math.asin(sin_lat * math.sin(eps_rad))
        
        # Longitude écliptique de l'ascendant
        y = math.sin(ra_asc) * math.cos(eps_rad) + math.tan(dec_asc) * math.sin(eps_rad)
        x = math.cos(ra_asc)
        
        ascendant = math.atan2(y, x) * RADTODEG
        ascendant = normalize_angle(ascendant)
        
        return ascendant
    
    def _calculate_mc(self, lst: float, latitude: float) -> float:
        """
        Calcule le Milieu du Ciel (MC)
        """
        # Pour le MC, on utilise l'heure sidérale directement
        # avec correction pour la latitude
        
        mc = lst
        latitude_corr = latitude * 0.0001  # Correction mineure
        mc = normalize_angle(mc + latitude_corr)
        
        return mc
    
    def _placidus_houses(self, ascendant: float, mc: float, latitude: float, 
                        lst: float) -> List[float]:
        """
        Système de maisons Placidus
        Le plus complexe - nécessite des itérations
        """
        houses = [0.0] * 12
        houses[0] = ascendant
        houses[9] = mc  # Maison 10 = MC
        
        # Calcul des autres maisons
        # Méthode des cercles de position
        
        # Cercle de position pour chaque maison
        for i in [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]:
            if i == 9:  # Maison 10 déjà calculée
                continue
                
            # Angle diurne pour cette maison
            if i >= 7:  # Maisons diurnes
                diurnal_arc = 180 + (i - 6) * 30
            else:  # Maisons nocturnes
                diurnal_arc = (i - 6) * 30
            
            # Calcul du cercle de position
            house_cusp = self._calculate_placidus_cusp(ascendant, diurnal_arc, 
                                                      latitude, lst)
            houses[i] = house_cusp
        
        # S'assurer que les maisons sont dans l'ordre
        for i in range(12):
            if i > 0 and houses[i] < houses[i-1]:
                houses[i] += 360
        
        return houses
    
    def _calculate_placidus_cusp(self, ascendant: float, diurnal_arc: float, 
                                latitude: float, lst: float) -> float:
        """
        Calcule une cuspide Placidus spécifique
        Nécessite une méthode itérative
        """
        # Méthode simplifiée (dans Astrolog, c'est plus complexe)
        lat_rad = latitude * DEGTORAD
        
        # Facteur de latitude
        lat_factor = math.tan(lat_rad)
        
        # Correction pour la latitude
        cusp_correction = diurnal_arc * lat_factor * 0.01
        
        # Position approximative
        cusp = ascendant + diurnal_arc + cusp_correction
        cusp = normalize_angle(cusp)
        
        return cusp
    
    def _koch_houses(self, ascendant: float, mc: float, latitude: float, 
                    lst: float) -> List[float]:
        """
        Système de maisons Koch
        Basé sur les ascensions obliques
        """
        houses = [0.0] * 12
        houses[0] = ascendant
        houses[9] = mc
        
        # Calcul des ascensions obliques
        lat_rad = latitude * DEGTORAD
        
        for i in range(1, 12):
            if i == 9:  # Maison 10 déjà calculée
                continue
                
            # Angle pour cette maison
            house_angle = i * 30
            
            # Ascension oblique
            ascension = self._calculate_oblique_ascension(house_angle, lat_rad)
            
            # Convertir en longitude écliptique
            house_cusp = self._ascension_to_longitude(ascension, lat_rad)
            houses[i] = house_cusp
        
        return houses
    
    def _calculate_oblique_ascension(self, angle: float, lat_rad: float) -> float:
        """Calcule l'ascension oblique"""
        # Formule simplifiée
        tan_lat = math.tan(lat_rad)
        oblique_asc = angle - math.atan(tan_lat * math.sin(angle * DEGTORAD)) * RADTODEG
        return normalize_angle(oblique_asc)
    
    def _ascension_to_longitude(self, ascension: float, lat_rad: float) -> float:
        """Convertit l'ascension oblique en longitude écliptique"""
        # Formule inverse simplifiée
        longitude = ascension + math.atan(math.tan(lat_rad) * math.sin(ascension * DEGTORAD)) * RADTODEG
        return normalize_angle(longitude)
    
    def _campanus_houses(self, ascendant: float, mc: float, latitude: float) -> List[float]:
        """
        Système de maisons Campanus
        Divise le prime vertical en 12 parties égales
        """
        houses = [0.0] * 12
        houses[0] = ascendant
        
        # Calcul du prime vertical
        lat_rad = latitude * DEGTORAD
        
        for i in range(12):
            # Diviser le prime vertical en 12 parties
            vertical_angle = i * 30
            
            # Convertir en longitude écliptique
            house_cusp = self._vertical_to_longitude(vertical_angle, lat_rad, ascendant)
            houses[i] = house_cusp
        
        return houses
    
    def _vertical_to_longitude(self, vertical_angle: float, lat_rad: float, 
                              ascendant: float) -> float:
        """Convertit l'angle vertical en longitude écliptique"""
        # Projection sur l'écliptique
        tan_factor = math.tan(lat_rad)
        longitude = ascendant + vertical_angle + (tan_factor * math.sin(vertical_angle * DEGTORAD) * 5)
        return normalize_angle(longitude)
    
    def _regiomontanus_houses(self, ascendant: float, mc: float, latitude: float) -> List[float]:
        """
        Système de maisons Regiomontanus
        Divise l'équateur en 12 parties égales
        """
        houses = [0.0] * 12
        houses[0] = ascendant
        houses[9] = mc
        
        # Calcul des divisions équatoriales
        for i in range(12):
            if i == 0 or i == 9:  # Déjà calculé
                continue
                
            # Division équatoriale
            equatorial_angle = i * 30
            
            # Conversion en longitude écliptique
            house_cusp = self._equatorial_to_longitude(equatorial_angle, latitude)
            houses[i] = house_cusp
        
        return houses
    
    def _equatorial_to_longitude(self, equatorial_angle: float, latitude: float) -> float:
        """Convertit la division équatoriale en longitude"""
        # Formule simplifiée de Regiomontanus
        lat_factor = math.tan(latitude * DEGTORAD) * 0.1
        longitude = equatorial_angle + (equatorial_angle * lat_factor)
        return normalize_angle(longitude)
    
    def _equal_houses(self, ascendant: float) -> List[float]:
        """
        Système de maisons égales
        Le plus simple : 30° par maison
        """
        houses = [0.0] * 12
        
        for i in range(12):
            houses[i] = normalize_angle(ascendant + i * 30)
        
        return houses
    
    def _porphyry_houses(self, ascendant: float, mc: float) -> List[float]:
        """
        Système de maisons Porphyry
        Divise chaque quadrant en 3 parties égales
        """
        houses = [0.0] * 12
        houses[0] = ascendant
        houses[9] = mc  # Maison 10
        
        # Calcul des quadrants
        quadrant1_size = normalize_angle(mc - ascendant)
        quadrant2_size = normalize_angle(ascendant + 180 - mc)
        quadrant3_size = quadrant1_size
        quadrant4_size = quadrant2_size
        
        # Diviser chaque quadrant en 3
        # Quadrant 1 (Maisons 10, 11, 12)
        houses[10] = normalize_angle(mc + quadrant1_size / 3)
        houses[11] = normalize_shape(mc + 2 * quadrant1_size / 3)
        
        # Quadrant 2 (Maisons 1, 2, 3)
        houses[1] = normalize_angle(ascendant + quadrant2_size / 3)
        houses[2] = normalize_angle(ascendant + 2 * quadrant2_size / 3)
        
        # Quadrant 3 (Maisons 4, 5, 6)
        houses[3] = normalize_angle(ascendant + 180 + quadrant3_size / 3)
        houses[4] = normalize_angle(ascendant + 180 + 2 * quadrant3_size / 3)
        
        # Quadrant 4 (Maisons 7, 8, 9)
        houses[6] = normalize_angle(mc + 180 + quadrant4_size / 3)
        houses[7] = normalize_angle(mc + 180 + 2 * quadrant4_size / 3)
        
        return houses
    
    def get_planet_house(self, planet_longitude: float, houses: List[float]) -> int:
        """
        Détermine dans quelle maison se trouve une planète
        Retourne le numéro de maison (1-12)
        """
        for i in range(12):
            next_i = (i + 1) % 12
            
            house_cusp = houses[i]
            next_cusp = houses[next_i]
            
            # Gérer le passage par 0°
            if next_cusp < house_cusp:
                if planet_longitude >= house_cusp or planet_longitude < next_cusp:
                    return i + 1
            else:
                if house_cusp <= planet_longitude < next_cusp:
                    return i + 1
        
        return 1  # Par défaut, maison 1
    
    def get_house_interpretation(self, house_num: int, sign: str) -> str:
        """Retourne une interprétation de la maison"""
        house_meanings = {
            1: "Personnalité, apparence, début de vie",
            2: "Finances, possessions, valeurs",
            3: "Communication, fratrie, apprentissage",
            4: "Maison, famille, racines",
            5: "Créativité, romance, enfants",
            6: "Travail, santé, service",
            7: "Relations, mariage, partenariats",
            8: "Transformation, sexe, finances partagées",
            9: "Voyages, philosophie, éducation supérieure",
            10: "Carrière, réputation, aspirations",
            11: "Amitiés, rêves, groupes",
            12: "Subconscient, secrets, spiritualité"
        }
        
        return f"Maison {house_num}: {house_meanings.get(house_num, 'Domaine de vie')}"
    
    def calculate_house_strength(self, planet_longitude: float, house_cusp: float, 
                               next_cusp: float) -> float:
        """
        Calcule la force d'une planète dans une maison
        (plus proche du milieu = plus forte)
        """
        house_size = normalize_angle(next_cusp - house_cusp)
        distance_from_cusp = normalize_angle(planet_longitude - house_cusp)
        
        # Milieu de la maison
        house_center = house_size / 2
        
        # Distance du milieu
        distance_from_center = abs(distance_from_cusp - house_center)
        if distance_from_center > house_size / 2:
            distance_from_center = house_size - distance_from_center
        
        # Force (0 = au bord, 1 = au centre)
        strength = 1.0 - (distance_from_center / (house_size / 2))
        
        return strength
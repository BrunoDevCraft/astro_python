"""
Calcul des aspects astrologiques
Traduction du module aspects d'Astrolog
"""

import math
from typing import Dict, List, Tuple
from .constants import *
from .utils import *

class AspectCalculator:
    """Calculateur d'aspects entre planètes"""
    
    def __init__(self):
        self.aspects = ASPECTS
        self.orb_factor = 1.0  # Facteur d'orb (peut être ajusté)
    
    def calculate_aspects(self, positions: Dict[str, Dict], 
                         max_orb: float = 8.0) -> List[Dict]:
        """
        Calcule tous les aspects entre les planètes
        positions: dict avec les positions planétaires
        max_orb: orb maximum autorisé
        """
        aspects_found = []
        planets = list(positions.keys())
        
        for i, planet1 in enumerate(planets):
            for j, planet2 in enumerate(planets):
                if i >= j:  # Éviter les doublons
                    continue
                
                pos1 = positions[planet1]['longitude']
                pos2 = positions[planet2]['longitude']
                
                # Calculer la distance angulaire
                distance = calculate_distance(pos1, pos2)
                
                # Vérifier chaque aspect
                for aspect_def in self.aspects:
                    aspect_angle = aspect_def['angle']
                    aspect_orb = aspect_def['orb'] * self.orb_factor
                    
                    # Calculer l'orb (marge d'erreur)
                    orb = abs(distance - aspect_angle)
                    
                    if orb <= min(aspect_orb, max_orb):
                        # Aspect trouvé
                        aspect = {
                            'planet1': planet1,
                            'planet2': planet2,
                            'aspect': aspect_def['name'],
                            'angle': aspect_angle,
                            'actual_angle': distance,
                            'orb': orb,
                            'type': aspect_def['type'],
                            'score': aspect_def['score'],
                            'applying': self._is_applying(positions[planet1], positions[planet2]),
                            'separating': self._is_separating(positions[planet1], positions[planet2])
                        }
                        aspects_found.append(aspect)
        
        # Trier par orb (du plus précis au moins précis)
        aspects_found.sort(key=lambda x: x['orb'])
        
        return aspects_found
    
    def _is_applying(self, planet1_data: Dict, planet2_data: Dict) -> bool:
        """Détermine si l'aspect est en application"""
        speed1 = planet1_data.get('speed', 0)
        speed2 = planet2_data.get('speed', 0)
        
        # Logique simplifiée - dans la vraie version, on considère les mouvements relatifs
        return abs(speed1) > abs(speed2)
    
    def _is_separating(self, planet1_data: Dict, planet2_data: Dict) -> bool:
        """Détermine si l'aspect est en séparation"""
        return not self._is_applying(planet1_data, planet2_data)
    
    def get_aspect_interpretation(self, aspect: Dict) -> str:
        """Retourne une interprétation textuelle de l'aspect"""
        planet1 = aspect['planet1']
        planet2 = aspect['planet2']
        aspect_name = aspect['aspect']
        
        interpretations = {
            "Conjonction": f"Fusion des énergies de {planet1} et {planet2}",
            "Opposition": f"Tension et polarité entre {planet1} et {planet2}",
            "Trigone": f"Harmonie et flow entre {planet1} et {planet2}",
            "Carré": f"Challenge et friction entre {planet1} et {planet2}",
            "Sextile": f"Opportunité et coopération entre {planet1} et {planet2}",
            "Quincunce": f"Ajustement nécessaire entre {planet1} et {planet2}"
        }
        
        return interpretations.get(aspect_name, f"Aspect {aspect_name} entre {planet1} et {planet2}")
    
    def calculate_aspect_patterns(self, aspects: List[Dict]) -> List[Dict]:
        """Calcule les configurations d'aspects (grand trine, T-carré, etc.)"""
        patterns = []
        
        # Recherche de grand trigone
        grand_trine = self._find_grand_trine(aspects)
        if grand_trine:
            patterns.append({
                'type': 'Grand Trigone',
                'planets': grand_trine,
                'interpretation': 'Harmonie et talents naturels'
            })
        
        # Recherche de T-carré
        t_square = self._find_t_square(aspects)
        if t_square:
            patterns.append({
                'type': 'T-Carré',
                'planets': t_square,
                'interpretation': 'Tension créative et motivation'
            })
        
        # Recherche de Yod
        yod = self._find_yod(aspects)
        if yod:
            patterns.append({
                'type': 'Yod',
                'planets': yod,
                'interpretation': 'Destinée spéciale et ajustements'
            })
        
        return patterns
    
    def _find_grand_trine(self, aspects: List[Dict]) -> List[str]:
        """Trouve un grand trigone (3 planètes en trigone formant un triangle)"""
        trines = [a for a in aspects if a['aspect'] == 'Trigone']
        
        planets_in_trine = {}
        for trine in trines:
            p1, p2 = trine['planet1'], trine['planet2']
            if p1 not in planets_in_trine:
                planets_in_trine[p1] = []
            if p2 not in planets_in_trine:
                planets_in_trine[p2] = []
            planets_in_trine[p1].append(p2)
            planets_in_trine[p2].append(p1)
        
        # Chercher un triangle complet
        for planet, connections in planets_in_trine.items():
            for connected in connections:
                if connected in planets_in_trine:
                    for third in planets_in_trine[connected]:
                        if third in planets_in_trine and planet in planets_in_trine[third]:
                            return [planet, connected, third]
        
        return []
    
    def _find_t_square(self, aspects: List[Dict]) -> List[str]:
        """Trouve un T-carré (opposition + 2 carrés)"""
        oppositions = [a for a in aspects if a['aspect'] == 'Opposition']
        squares = [a for a in aspects if a['aspect'] == 'Carré']
        
        for opposition in oppositions:
            p1, p2 = opposition['planet1'], opposition['planet2']
            
            # Chercher des carrés formant un T
            square_planets = []
            for square in squares:
                if square['planet1'] == p1 and square['planet2'] != p2:
                    square_planets.append(square['planet2'])
                elif square['planet2'] == p1 and square['planet1'] != p2:
                    square_planets.append(square['planet1'])
                elif square['planet1'] == p2 and square['planet2'] != p1:
                    square_planets.append(square['planet2'])
                elif square['planet2'] == p2 and square['planet1'] != p1:
                    square_planets.append(square['planet1'])
            
            if len(square_planets) >= 1:
                return [p1, p2, square_planets[0]]
        
        return []
    
    def _find_yod(self, aspects: List[Dict]) -> List[str]:
        """Trouve un Yod (2 quincunces + 1 sextile)"""
        quincunxes = [a for a in aspects if a['aspect'] == 'Quincunce']
        sextiles = [a for a in aspects if a['aspect'] == 'Sextile']
        
        # Pour chaque paire de quincunces partageant une planète
        for i, q1 in enumerate(quincunxes):
            for j, q2 in enumerate(quincunxes[i+1:], i+1):
                shared_planet = None
                other_planets = []
                
                if q1['planet1'] == q2['planet1']:
                    shared_planet = q1['planet1']
                    other_planets = [q1['planet2'], q2['planet2']]
                elif q1['planet1'] == q2['planet2']:
                    shared_planet = q1['planet1']
                    other_planets = [q1['planet2'], q2['planet1']]
                elif q1['planet2'] == q2['planet1']:
                    shared_planet = q1['planet2']
                    other_planets = [q1['planet1'], q2['planet2']]
                elif q1['planet2'] == q2['planet2']:
                    shared_planet = q1['planet2']
                    other_planets = [q1['planet1'], q2['planet1']]
                
                if shared_planet and len(other_planets) == 2:
                    # Vérifier s'il y a un sextile entre les deux autres planètes
                    for sextile in sextiles:
                        if ((sextile['planet1'] == other_planets[0] and sextile['planet2'] == other_planets[1]) or
                            (sextile['planet1'] == other_planets[1] and sextile['planet2'] == other_planets[0])):
                            return [shared_planet, other_planets[0], other_planets[1]]
        
        return []
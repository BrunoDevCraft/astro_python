"""
Calculateur astrologique principal
Intègre tous les modules pour le calcul complet d'un thème natal
"""

from datetime import datetime
from typing import Dict, List, Optional
import pytz
import requests
from .constants import *
from .utils import *
from ..data.ephemeris import EphemerisCalculator
from .aspects import AspectCalculator
from .houses import HouseCalculator

class AstrologicalCalculator:
    """Calculateur principal - équivalent du core d'Astrolog"""
    
    def __init__(self):
        self.ephemeris = EphemerisCalculator()
        self.aspects = AspectCalculator()
        self.houses = HouseCalculator()
        self.current_config = self._default_config()
    
    def _default_config(self) -> Dict:
        """Configuration par défaut (comme Astrolog)"""
        return {
            'house_system': 'P',  # Placidus
            'aspects': ['Conjonction', 'Opposition', 'Trigone', 'Carré', 'Sextile'],
            'planets': ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                       'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'],
            'orbs': {'Conjonction': 8, 'Opposition': 8, 'Trigone': 8, 'Carré': 8, 'Sextile': 6},
            'use_ephemeris': True,
            'show_retrograde': True,
            'show_declinations': False,
            'zodiac': 'tropical'  # Tropical par défaut
        }
    
    def calculate_natal_chart(self, birth_date: datetime, latitude: float, 
                            longitude: float, timezone_str: str = 'UTC') -> Dict:
        """
        Calcule un thème natal complet
        Équivalent de la fonction principale d'Astrolog
        """
        # Convertir la date en jour julien
        jd = self._datetime_to_julian(birth_date, timezone_str)
        
        # Calculer les positions planétaires
        planet_positions = self.ephemeris.calculate_all_planets(jd)
        
        # Calculer les maisons
        house_data = self.houses.calculate_houses(jd, latitude, longitude, 
                                                 self.current_config['house_system'])
        
        # Assigner les planètes aux maisons
        planet_houses = self._assign_planets_to_houses(planet_positions, house_data['houses'])
        
        # Calculer les aspects
        aspects = self.aspects.calculate_aspects(planet_positions)
        
        # Calculer les configurations d'aspects
        aspect_patterns = self.aspects.calculate_aspect_patterns(aspects)
        
        # Calculer les éléments et modalités
        element_counts = self._calculate_elements(planet_positions)
        modality_counts = self._calculate_modalities(planet_positions)
        
        # Générer les interprétations
        interpretations = self._generate_interpretations(planet_positions, aspects, 
                                                        house_data, planet_houses)
        
        return {
            'birth_data': {
                'date': birth_date,
                'latitude': latitude,
                'longitude': longitude,
                'timezone': timezone_str,
                'julian_day': jd
            },
            'planet_positions': planet_positions,
            'house_data': house_data,
            'planet_houses': planet_houses,
            'aspects': aspects,
            'aspect_patterns': aspect_patterns,
            'element_counts': element_counts,
            'modality_counts': modality_counts,
            'interpretations': interpretations,
            'config': self.current_config.copy()
        }
    
    def calculate_transits(self, natal_chart: Dict, transit_date: datetime) -> Dict:
        """
        Calcule les transits par rapport à un thème natal
        """
        # Calculer les positions de transit
        transit_jd = self._datetime_to_julian(transit_date, natal_chart['birth_data']['timezone'])
        transit_positions = self.ephemeris.calculate_all_planets(transit_jd)
        
        # Calculer les aspects entre transits et natal
        transit_aspects = []
        
        for transit_planet, transit_data in transit_positions.items():
            for natal_planet, natal_data in natal_chart['planet_positions'].items():
                if transit_planet == natal_planet:
                    continue
                
                # Calculer l'aspect
                distance = calculate_distance(transit_data['longitude'], 
                                            natal_data['longitude'])
                
                for aspect_def in ASPECTS:
                    orb = abs(distance - aspect_def['angle'])
                    if orb <= aspect_def['orb']:
                        transit_aspects.append({
                            'transit_planet': transit_planet,
                            'natal_planet': natal_planet,
                            'aspect': aspect_def['name'],
                            'orb': orb,
                            'applying': self._is_transit_applying(transit_data, natal_data),
                            'interpretation': self._interpret_transit(transit_planet, 
                                                                    natal_planet, 
                                                                    aspect_def['name'])
                        })
        
        # Trier par orb
        transit_aspects.sort(key=lambda x: x['orb'])
        
        return {
            'transit_date': transit_date,
            'transit_positions': transit_positions,
            'transit_aspects': transit_aspects,
            'significant_transits': self._filter_significant_transits(transit_aspects)
        }
    
    def calculate_progressions(self, natal_chart: Dict, progression_date: datetime) -> Dict:
        """
        Calcule les progressions (méthode symbolique : 1 jour = 1 an)
        """
        birth_date = natal_chart['birth_data']['date']
        
        # Calculer l'âge en jours
        age_days = (progression_date - birth_date).days
        
        # Calculer la date de progression (jour de naissance + age en jours)
        progression_birth_date = birth_date.replace(
            year=birth_date.year + age_days // 365
        )
        
        # Calculer le thème progressé
        progressed_chart = self.calculate_natal_chart(
            progression_birth_date,
            natal_chart['birth_data']['latitude'],
            natal_chart['birth_data']['longitude'],
            natal_chart['birth_data']['timezone']
        )
        
        # Calculer les aspects entre progressé et natal
        progression_aspects = []
        
        for prog_planet, prog_data in progressed_chart['planet_positions'].items():
            for natal_planet, natal_data in natal_chart['planet_positions'].items():
                if prog_planet == natal_planet:
                    continue
                
                distance = calculate_distance(prog_data['longitude'], 
                                            natal_data['longitude'])
                
                for aspect_def in ASPECTS:
                    orb = abs(distance - aspect_def['angle'])
                    if orb <= aspect_def['orb'] * 0.5:  # Orb plus serré pour progressions
                        progression_aspects.append({
                            'progressed_planet': prog_planet,
                            'natal_planet': natal_planet,
                            'aspect': aspect_def['name'],
                            'orb': orb
                        })
        
        return {
            'progression_date': progression_date,
            'age_years': age_days / 365.25,
            'progressed_chart': progressed_chart,
            'progression_aspects': progression_aspects
        }
    
    def calculate_compatibility(self, chart1: Dict, chart2: Dict) -> Dict:
        """
        Calcule la compatibilité entre deux thèmes (synastrie)
        """
        # Aspects entre les deux thèmes
        synastry_aspects = []
        
        for planet1, data1 in chart1['planet_positions'].items():
            for planet2, data2 in chart2['planet_positions'].items():
                distance = calculate_distance(data1['longitude'], data2['longitude'])
                
                for aspect_def in ASPECTS:
                    orb = abs(distance - aspect_def['angle'])
                    if orb <= aspect_def['orb']:
                        synastry_aspects.append({
                            'planet1': planet1,
                            'planet2': planet2,
                            'aspect': aspect_def['name'],
                            'orb': orb,
                            'score': aspect_def['score']
                        })
        
        # Calculer le score de compatibilité
        total_score = sum(aspect['score'] for aspect in synastry_aspects)
        max_possible_score = len(synastry_aspects) * 10  # Score maximum théorique
        compatibility_percentage = max(0, min(100, (total_score + max_possible_score) / 
                                           (2 * max_possible_score) * 100))
        
        # Analyser les éléments en synastrie
        element_compatibility = self._analyze_element_compatibility(
            chart1['element_counts'], chart2['element_counts'])
        
        return {
            'synastry_aspects': synastry_aspects,
            'compatibility_score': total_score,
            'compatibility_percentage': compatibility_percentage,
            'element_compatibility': element_compatibility,
            'interpretation': self._interpret_compatibility(compatibility_percentage, 
                                                           synastry_aspects)
        }
    
    def _datetime_to_julian(self, dt: datetime, timezone_str: str) -> float:
        """Convertit datetime en jour julien avec timezone"""
        timezone = pytz.timezone(timezone_str)
        dt_tz = timezone.localize(dt)
        
        # Convertir en UTC
        dt_utc = dt_tz.astimezone(pytz.UTC)
        
        # Calculer le jour julien
        jd = julian_day(dt_utc.year, dt_utc.month, dt_utc.day, 
                       dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)
        
        return jd
    
    def _assign_planets_to_houses(self, planet_positions: Dict, houses: List[float]) -> Dict:
        """Assigne chaque planète à sa maison"""
        planet_houses = {}
        
        for planet, data in planet_positions.items():
            longitude = data['longitude']
            house_num = self.houses.get_planet_house(longitude, houses)
            planet_houses[planet] = house_num
        
        return planet_houses
    
    def _is_transit_applying(self, transit_data: Dict, natal_data: Dict) -> bool:
        """Détermine si le transit est en application"""
        # Logique simplifiée - vérifie si les planètes se rapprochent
        transit_speed = transit_data.get('speed', 0)
        return transit_speed > 0  # Simplification
    
    def _interpret_transit(self, transit_planet: str, natal_planet: str, aspect: str) -> str:
        """Interprète un transit"""
        interpretations = {
            "Sun": {
                "Conjonction": "Énergie renouvelée et focus sur {natal}",
                "Opposition": "Tension entre identité et {natal}",
                "Trigone": "Harmonie entre conscience et {natal}",
                "Carré": "Défi pour intégrer {natal}"
            },
            "Moon": {
                "Conjonction": "Émotions amplifiées concernant {natal}",
                "Opposition": "Conflit émotionnel avec {natal}",
                "Trigone": "Flux émotionnel harmonieux avec {natal}",
                "Carré": "Tension émotionnelle autour de {natal}"
            }
        }
        
        return interpretations.get(transit_planet, {}).get(aspect, 
               f"Influence de {transit_planet} sur {natal_planet}")
    
    def _calculate_elements(self, planet_positions: Dict) -> Dict[str, int]:
        """Calcule la répartition par éléments"""
        element_counts = {"Feu": 0, "Terre": 0, "Air": 0, "Eau": 0}
        
        for planet, data in planet_positions.items():
            longitude = data['longitude']
            sign_index = int(longitude // 30)
            
            for element, signs in ELEMENTS.items():
                if sign_index in signs:
                    element_counts[element] += 1
                    break
        
        return element_counts
    
    def _calculate_modalities(self, planet_positions: Dict) -> Dict[str, int]:
        """Calcule la répartition par modalités"""
        modality_counts = {"Cardinal": 0, "Fixe": 0, "Mutable": 0}
        
        for planet, data in planet_positions.items():
            longitude = data['longitude']
            sign_index = int(longitude // 30)
            
            for modality, signs in MODALITIES.items():
                if sign_index in signs:
                    modality_counts[modality] += 1
                    break
        
        return modality_counts
    
    def _analyze_element_compatibility(self, elements1: Dict, elements2: Dict) -> Dict:
        """Analyse la compatibilité élémentaire"""
        compatibility_scores = {
            "Feu": {"Feu": 8, "Terre": 6, "Air": 9, "Eau": 4},
            "Terre": {"Feu": 6, "Terre": 8, "Air": 5, "Eau": 9},
            "Air": {"Feu": 9, "Terre": 5, "Air": 7, "Eau": 6},
            "Eau": {"Feu": 4, "Terre": 9, "Air": 6, "Eau": 8}
        }
        
        total_score = 0
        element_analysis = {}
        
        for elem1 in elements1:
            for elem2 in elements2:
                score = compatibility_scores[elem1][elem2]
                total_score += score
                element_analysis[f"{elem1}-{elem2}"] = score
        
        return {
            'total_score': total_score,
            'element_analysis': element_analysis,
            'dominant_elements': self._get_dominant_elements(elements1, elements2)
        }
    
    def _get_dominant_elements(self, elements1: Dict, elements2: Dict) -> List[str]:
        """Retourne les éléments dominants dans les deux cartes"""
        dominant = []
        
        for element in elements1:
            if elements1[element] > 2 or elements2[element] > 2:
                dominant.append(element)
        
        return dominant
    
    def _interpret_compatibility(self, percentage: float, aspects: List[Dict]) -> str:
        """Interprète le score de compatibilité"""
        if percentage >= 80:
            return "Compatibilité exceptionnelle - Union harmonieuse et complète"
        elif percentage >= 60:
            return "Très bonne compatibilité - Relation équilibrée avec potentiel de croissance"
        elif percentage >= 40:
            return "Compatibilité moyenne - Travail et communication nécessaires"
        elif percentage >= 20:
            return "Difficultés importantes - Efforts conséquents requis pour la relation"
        else:
            return "Compatibilité très faible - Défis majeurs à surmonter"
    
    def _generate_interpretations(self, planet_positions: Dict, aspects: List[Dict], 
                                house_data: Dict, planet_houses: Dict) -> Dict:
        """Génère des interprétations pour le thème"""
        interpretations = {
            'planets': {},
            'aspects': {},
            'houses': {},
            'summary': ''
        }
        
        # Interprétations planétaires
        for planet, data in planet_positions.items():
            sign_index = int(data['longitude'] // 30)
            sign = ZODIAC_SIGNS[sign_index]
            house = planet_houses[planet]
            
            interpretations['planets'][planet] = {
                'sign': f"{planet} en {sign}",
                'house': f"{planet} en maison {house}",
                'retrograde': data.get('retrograde', False)
            }
        
        # Interprétations d'aspects
        for aspect in aspects[:5]:  # Top 5 aspects
            interpretations['aspects'][f"{aspect['planet1']}-{aspect['planet2']}"] = \
                aspect['interpretation']
        
        # Interprétations de maisons
        for i in range(12):
            house_sign = int(house_data['houses'][i] // 30)
            sign_name = ZODIAC_SIGNS[house_sign]
            interpretations['houses'][f"House_{i+1}"] = \
                f"Maison {i+1} en {sign_name}"
        
        # Résumé général
        interpretations['summary'] = self._generate_summary(
            planet_positions, aspects, house_data)
        
        return interpretations
    
    def _generate_summary(self, planet_positions: Dict, aspects: List[Dict], 
                         house_data: Dict) -> str:
        """Génère un résumé général du thème"""
        # Analyse très simplifiée
        planet_count = len(planet_positions)
        aspect_count = len(aspects)
        
        if aspect_count > planet_count * 2:
            return "Thème riche en aspects - vie complexe et intéressante"
        elif aspect_count < planet_count:
            return "Thème avec peu d'aspects - vie plus simple et directe"
        else:
            return "Thème équilibré - vie harmonieuse"
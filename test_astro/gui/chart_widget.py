"""
Widget de visualisation de la carte astrologique
Dessin vectoriel de la carte du ciel avec Qt
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF, QRectF, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import (
    QPainter, QPainterPath, QPen, QBrush, QColor, QFont, QPolygonF, QTransform,
    QRadialGradient, QLinearGradient, QConicalGradient
)
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..core.constants import *
from ..core.utils import normalize_angle, get_zodiac_sign


class AstrologicalChartWidget(QWidget):
    """Widget pour afficher la carte astrologique avec toutes ses composantes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart_data = None
        self.show_grid = True
        self.show_aspects = True
        self.show_planets = True
        self.show_houses = True
        self.show_zodiac = True
        self.animation_enabled = True
        
        # Paramètres de dessin
        self.center = QPointF(0, 0)
        self.radius = 200
        self.inner_radius = 120
        self.planet_radius = 160
        self.house_radius = 190
        self.zodiac_radius = 170
        
        # Animation
        self._rotation_angle = 0
        self.rotation_animation = QPropertyAnimation(self, b"rotation_angle")
        self.rotation_animation.setDuration(2000)
        self.rotation_animation.setEasingCurve(QEasingCurve.OutBack)
        
        self.setMinimumSize(400, 400)
        self.setMouseTracking(True)
        
    def set_chart(self, chart_data: Dict):
        """Définit les données du thème à afficher"""
        self.chart_data = chart_data
        self.update()
        
        # Lancer l'animation
        if self.animation_enabled:
            self.rotation_animation.setStartValue(0)
            self.rotation_animation.setEndValue(360)
            self.rotation_animation.start()
    
    def paintEvent(self, event):
        """Événement de dessin principal"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Calculer le centre et le rayon
        self.center = QPointF(self.width() / 2, self.height() / 2)
        self.radius = min(self.width(), self.height()) / 2 - 20
        
        # Adapter les rayons
        self.inner_radius = self.radius * 0.6
        self.planet_radius = self.radius * 0.8
        self.house_radius = self.radius * 0.95
        self.zodiac_radius = self.radius * 0.85
        
        # Effacer le fond
        painter.fillRect(self.rect(), QColor("#0f3460"))
        
        # Dessiner le fond avec dégradé
        self.draw_background(painter)
        
        if self.chart_data:
            # Rotation pour l'animation
            painter.save()
            painter.translate(self.center)
            painter.rotate(self._rotation_angle)
            painter.translate(-self.center)
            
            # Dessiner les composants
            if self.show_grid:
                self.draw_grid(painter)
            
            if self.show_zodiac:
                self.draw_zodiac(painter)
            
            if self.show_houses:
                self.draw_houses(painter)
            
            if self.show_planets:
                self.draw_planets(painter)
            
            if self.show_aspects:
                self.draw_aspects(painter)
            
            # Dessiner le centre
            self.draw_center(painter)
            
            painter.restore()
        
        # Dessiner les informations textuelles (non animées)
        self.draw_info_text(painter)
    
    def draw_background(self, painter: QPainter):
        """Dessine l'arrière-plan avec effets spéciaux"""
        # Créer un dégradé radial
        gradient = QRadialGradient(self.center, self.radius)
        gradient.setColorAt(0, QColor("#16213e"))
        gradient.setColorAt(0.7, QColor("#1a1a2e"))
        gradient.setColorAt(1, QColor("#0f3460"))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.center, int(self.radius), int(self.radius))
        
        # Ajouter des étoiles (effet cosmique)
        self.draw_stars(painter)
    
    def draw_stars(self, painter: QPainter):
        """Dessine des étoiles aléatoires pour l'effet cosmique"""
        painter.setPen(QPen(QColor("white"), 1))
        
        # Étoiles fixes (basées sur une graine pour la cohérence)
        import random
        random.seed(42)  # Graine fixe
        
        for i in range(50):
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            size = random.randint(1, 3)
            
            painter.drawEllipse(QPointF(x, y), size, size)
    
    def draw_grid(self, painter: QPainter):
        """Dessine la grille de référence"""
        painter.setPen(QPen(QColor("#4fbdba").lighter(150), 0.5, Qt.DotLine))
        
        # Cercles concentriques
        for r in [self.inner_radius, self.planet_radius, self.house_radius, self.zodiac_radius]:
            painter.drawEllipse(self.center, int(r), int(r))
        
        # Lignes radiales (tous les 30°)
        for angle in range(0, 360, 30):
            rad_angle = math.radians(angle)
            x1 = self.center.x() + self.inner_radius * math.cos(rad_angle)
            y1 = self.center.y() + self.inner_radius * math.sin(rad_angle)
            x2 = self.center.x() + self.radius * math.cos(rad_angle)
            y2 = self.center.y() + self.radius * math.sin(rad_angle)
            
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    
    def draw_zodiac(self, painter: QPainter):
        """Dessine les signes du zodiaque"""
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        
        for i, (sign, symbol) in enumerate(zip(ZODIAC_SIGNS, ZODIAC_SYMBOLS)):
            angle = i * 30 + 15  # Milieu du signe
            rad_angle = math.radians(angle)
            
            # Position du texte
            x = self.center.x() + (self.zodiac_radius + 15) * math.cos(rad_angle)
            y = self.center.y() + (self.zodiac_radius + 15) * math.sin(rad_angle)
            
            # Ajuster pour l'alignement du texte
            text = f"{symbol} {sign}"
            text_rect = painter.fontMetrics().boundingRect(text)
            
            # Dessiner le texte avec un fond semi-transparent
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor("#16213e").lighter(120)))
            text_rect.moveCenter(QPointF(x, y))
            painter.drawRect(text_rect)
            
            # Dessiner le texte
            painter.setPen(QPen(QColor("#4fbdba"), 2))
            painter.drawText(QPointF(x - text_rect.width()/2, y + text_rect.height()/4), text)
    
    def draw_houses(self, painter: QPainter):
        """Dessine les maisons astrologiques"""
        houses = self.chart_data['house_data']['houses']
        
        painter.setPen(QPen(QColor("#e94560"), 1.5))
        
        # Dessiner les cuspides des maisons
        for i, cusp in enumerate(houses):
            angle = cusp
            rad_angle = math.radians(angle)
            
            # Ligne de la maison
            x1 = self.center.x() + self.inner_radius * math.cos(rad_angle)
            y1 = self.center.y() + self.inner_radius * math.sin(rad_angle)
            x2 = self.center.x() + self.house_radius * math.cos(rad_angle)
            y2 = self.center.y() + self.house_radius * math.sin(rad_angle)
            
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
            # Numéro de la maison
            if i % 3 == 0:  # Afficher que certaines maisons pour éviter la surcharge
                house_x = self.center.x() + (self.house_radius + 10) * math.cos(rad_angle)
                house_y = self.center.y() + (self.house_radius + 10) * math.sin(rad_angle)
                
                painter.setPen(QPen(QColor("#e94560"), 2))
                painter.setFont(QFont("Arial", 8, QFont.Bold))
                painter.drawText(QPointF(house_x - 5, house_y + 5), str(i + 1))
                painter.setPen(QPen(QColor("#4fbdba"), 1.5))
        
        # Marquer l'ascendant et le MC spécialement
        self.draw_special_points(painter, houses)
    
    def draw_special_points(self, painter: QPainter, houses: List[float]):
        """Dessine les points spéciaux (Ascendant, MC, etc.)"""
        special_points = {
            'Asc': houses[0],
            'MC': houses[9],
            'Desc': houses[6],
            'IC': houses[3]
        }
        
        painter.setPen(QPen(QColor("#FFD700"), 3))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        
        for name, angle in special_points.items():
            rad_angle = math.radians(angle)
            
            # Position du symbole
            x = self.center.x() + (self.house_radius + 20) * math.cos(rad_angle)
            y = self.center.y() + (self.house_radius + 20) * math.sin(rad_angle)
            
            painter.drawText(QPointF(x - 10, y + 5), name)
    
    def draw_planets(self, painter: QPainter):
        """Dessine les planètes sur la carte"""
        positions = self.chart_data['planet_positions']
        planet_houses = self.chart_data['planet_houses']
        
        # Trier les planètes par distance du centre (pour l'overlap)
        sorted_planets = sorted(positions.items(), 
                              key=lambda x: self.get_planet_distance(x[0]))
        
        for planet, data in sorted_planets:
            longitude = data['longitude']
            retrograde = data.get('retrograde', False)
            
            # Position de la planète
            angle = longitude
            rad_angle = math.radians(angle)
            
            x = self.center.x() + self.planet_radius * math.cos(rad_angle)
            y = self.center.y() + self.planet_radius * math.sin(rad_angle)
            
            # Dessiner la planète
            self.draw_planet_symbol(painter, planet, QPointF(x, y), retrograde)
            
            # Dessiner les informations
            self.draw_planet_info(painter, planet, data, QPointF(x, y))
    
    def get_planet_distance(self, planet: str) -> float:
        """Retourne la distance moyenne de la planète (pour le tri)"""
        distances = {
            'Moon': 0.00257, 'Mercury': 0.387, 'Venus': 0.723,
            'Sun': 1.0, 'Mars': 1.524, 'Jupiter': 5.203,
            'Saturn': 9.537, 'Uranus': 19.19, 'Neptune': 30.07,
            'Pluto': 39.48, 'Node': 0, 'Chiron': 13.7
        }
        return distances.get(planet, 1.0)
    
    def draw_planet_symbol(self, painter: QPainter, planet: str, position: QPointF, 
                          retrograde: bool):
        """Dessine le symbole d'une planète"""
        # Couleur selon la planète
        colors = {
            'Sun': QColor("#FFD700"), 'Moon': QColor("#C0C0C0"),
            'Mercury': QColor("#8C7853"), 'Venus': QColor("#FFC649"),
            'Mars': QColor("#CD5C5C"), 'Jupiter': QColor("#DAA520"),
            'Saturn': QColor("#F4A460"), 'Uranus': QColor("#4FD0E7"),
            'Neptune': QColor("#4169E1"), 'Pluto': QColor("#9C27B0"),
            'Node': QColor("#795548"), 'Chiron': QColor("#FF9800")
        }
        
        color = colors.get(planet, QColor("#4fbdba"))
        
        # Cercle de la planète
        planet_size = 8
        painter.setPen(QPen(color, 2))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(position, planet_size, planet_size)
        
        # Symbole de la planète
        symbol = PLANET_SYMBOLS.get(planet, planet[0])
        painter.setPen(QPen(Qt.white, 2))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(QRectF(position.x() - 8, position.y() - 8, 16, 16), 
                        Qt.AlignCenter, symbol)
        
        # Marquer la rétrogradation
        if retrograde:
            painter.setPen(QPen(Qt.red, 1.5))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(position, planet_size + 3, planet_size + 3)
    
    def draw_planet_info(self, painter: QPainter, planet: str, data: Dict, 
                        position: QPointF):
        """Dessine les informations détaillées d'une planète"""
        longitude = data['longitude']
        sign_index, sign_name, sign_symbol = get_zodiac_sign(longitude)
        degrees = int(longitude % 30)
        minutes = int((longitude % 1) * 60)
        
        # Position du texte (éviter le chevauchement)
        text_angle = math.atan2(position.y() - self.center.y(), 
                                position.x() - self.center.x())
        text_distance = 25
        
        text_x = position.x() + text_distance * math.cos(text_angle)
        text_y = position.y() + text_distance * math.sin(text_angle)
        
        # Créer le texte
        info_text = f"{degrees}°{minutes:02d}' {sign_symbol}"
        
        # Dessiner le fond
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#16213e").lighter(150)))
        
        text_rect = painter.fontMetrics().boundingRect(info_text)
        text_rect.adjust(-5, -2, 5, 2)
        text_rect.moveCenter(QPointF(text_x, text_y))
        painter.drawRect(text_rect)
        
        # Dessiner le texte
        painter.setPen(QPen(Qt.white, 1))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(text_rect, Qt.AlignCenter, info_text)
    
    def draw_aspects(self, painter: QPainter):
        """Dessine les aspects entre planètes"""
        aspects = self.chart_data.get('aspects', [])
        
        # Limiter aux aspects majeurs et importants
        major_aspects = [a for a in aspects if a['type'] == 'majeur' and a['orb'] < 5]
        major_aspects = major_aspects[:8]  # Maximum 8 aspects à dessiner
        
        for aspect in major_aspects:
            planet1 = aspect['planet1']
            planet2 = aspect['planet2']
            aspect_name = aspect['aspect']
            
            if planet1 in self.chart_data['planet_positions'] and planet2 in self.chart_data['planet_positions']:
                pos1 = self.chart_data['planet_positions'][planet1]
                pos2 = self.chart_data['planet_positions'][planet2]
                
                self.draw_aspect_line(painter, pos1['longitude'], pos2['longitude'], aspect_name)
    
    def draw_aspect_line(self, painter: QPainter, longitude1: float, longitude2: float, 
                        aspect_name: str):
        """Dessine une ligne d'aspect entre deux planètes"""
        # Couleurs selon le type d'aspect
        aspect_colors = {
            'Conjonction': QColor("#FFD700"),     # Or
            'Opposition': QColor("#FF6B6B"),      # Rouge
            'Trigone': QColor("#4CAF50"),         # Vert
            'Carré': QColor("#FF9800"),           # Orange
            'Sextile': QColor("#2196F3")          # Bleu
        }
        
        color = aspect_colors.get(aspect_name, QColor("#4fbdba"))
        
        # Calculer les positions
        angle1 = longitude1
        angle2 = longitude2
        
        # Vérifier si c'est un aspect valide (distance < 180°)
        distance = abs(angle1 - angle2)
        if distance > 180:
            distance = 360 - distance
        
        # Ne dessiner que les aspects valides
        if distance > 180:
            return
        
        rad_angle1 = math.radians(angle1)
        rad_angle2 = math.radians(angle2)
        
        x1 = self.center.x() + self.planet_radius * math.cos(rad_angle1)
        y1 = self.center.y() + self.planet_radius * math.sin(rad_angle1)
        x2 = self.center.x() + self.planet_radius * math.cos(rad_angle2)
        y2 = self.center.y() + self.planet_radius * math.sin(rad_angle2)
        
        # Dessiner la ligne
        painter.setPen(QPen(color, 2, Qt.SolidLine))
        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        
        # Ajouter un petit symbole au milieu de la ligne
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.drawText(QPointF(mid_x - 10, mid_y + 5), aspect_name[0])
    
    def draw_center(self, painter: QPainter):
        """Dessine le centre de la carte"""
        # Cercle central
        gradient = QRadialGradient(self.center, 20)
        gradient.setColorAt(0, QColor("#4fbdba"))
        gradient.setColorAt(1, QColor("#16213e"))
        
        painter.setBrush(gradient)
        painter.setPen(QPen(QColor("#4fbdba"), 2))
        painter.drawEllipse(self.center, 15, 15)
        
        # Symbole au centre
        painter.setPen(QPen(Qt.white, 2))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(QRectF(self.center.x() - 10, self.center.y() - 10, 20, 20), 
                        Qt.AlignCenter, "✦")
    
    def draw_info_text(self, painter: QPainter):
        """Dessine les informations textuelles (non animées)"""
        if not self.chart_data:
            return
        
        # Informations du thème
        birth_data = self.chart_data['birth_data']
        
        painter.setPen(QPen(QColor("#4fbdba"), 1))
        painter.setFont(QFont("Arial", 10))
        
        # Date et heure
        date_text = birth_data['date'].strftime("%d %B %Y à %H:%M")
        date_rect = painter.fontMetrics().boundingRect(date_text)
        date_rect.moveTopLeft(QPointF(10, 20))
        painter.drawText(date_rect, date_text)
        
        # Coordonnées
        lat_text = f"Lat: {birth_data['latitude']:.4f}°"
        lon_text = f"Lon: {birth_data['longitude']:.4f}°"
        
        painter.drawText(QPointF(10, 40), lat_text)
        painter.drawText(QPointF(10, 55), lon_text)
        
        # Système de maisons
        house_system = self.chart_data['config']['house_system']
        system_name = [name for name, code in HOUSE_SYSTEMS.items() if code == house_system][0]
        painter.drawText(QPointF(10, 70), f"Maisons: {system_name}")
    
    def mousePressEvent(self, event):
        """Gestion des clics de souris"""
        if event.button() == Qt.LeftButton and self.chart_data:
            # Calculer l'angle du clic
            dx = event.pos().x() - self.center.x()
            dy = event.pos().y() - self.center.y()
            angle = math.degrees(math.atan2(dy, dx))
            
            # Trouver la planète la plus proche
            closest_planet = None
            min_distance = float('inf')
            
            for planet, data in self.chart_data['planet_positions'].items():
                planet_angle = data['longitude']
                distance = abs(angle - planet_angle)
                if distance > 180:
                    distance = 360 - distance
                
                if distance < min_distance:
                    min_distance = distance
                    closest_planet = planet
            
            # Si proche d'une planète, afficher les détails
            if min_distance < 10 and closest_planet:
                self.show_planet_details(closest_planet)
    
    def show_planet_details(self, planet: str):
        """Affiche les détails d'une planète"""
        if not self.chart_data:
            return
        
        data = self.chart_data['planet_positions'][planet]
        house = self.chart_data['planet_houses'][planet]
        
        # Créer un texte détaillé
        longitude = data['longitude']
        sign_index = int(longitude // 30)
        sign = ZODIAC_SIGNS[sign_index]
        degrees = int(longitude % 30)
        minutes = int((longitude % 1) * 60)
        
        details_text = f"""
        {planet} en {sign} {degrees}°{minutes:02d}'
        Maison {house}
        Vitesse: {data.get('speed', 0):.3f}°/jour
        Rétrograde: {'Oui' if data.get('retrograde', False) else 'Non'}
        """
        
        # Émettre un signal ou afficher une info-bulle
        print(f"Détails de {planet}: {details_text}")
    
    def resizeEvent(self, event):
        """Gestion du redimensionnement"""
        super().resizeEvent(event)
        self.update()
    
    def get_rotation_angle(self):
        return self._rotation_angle
    
    def set_rotation_angle(self, angle):
        self._rotation_angle = angle
        self.update()
    
    rotation_angle = Property(float, get_rotation_angle, set_rotation_angle)


class AstrologicalChartView(QGraphicsView):
    """Vue graphique pour la carte astrologique avec zoom et déplacement"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Configuration de la vue
        self.setRenderHint(QPainter.Antialiasing)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
        
        # Activer le déplacement avec la souris
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # Zoom
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        self.chart_widget = None
    
    def set_chart_widget(self, chart_widget: AstrologicalChartWidget):
        """Définit le widget de carte"""
        self.chart_widget = chart_widget
        self.scene.addWidget(chart_widget)
    
    def wheelEvent(self, event):
        """Zoom avec la molette"""
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)
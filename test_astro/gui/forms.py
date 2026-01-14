"""
Formulaires de saisie pour l'interface graphique
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QDateEdit, QTimeEdit, QComboBox, QPushButton,
    QLabel, QSpinBox, QDoubleSpinBox, QTextEdit, QCheckBox,
    QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QDate, QTime, Signal, Slot
from PySide6.QtGui import QIntValidator, QDoubleValidator
from datetime import datetime
from typing import Dict, Optional


class BirthDataForm(QWidget):
    """Formulaire de saisie des données de naissance"""
    
    calculate_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface du formulaire"""
        layout = QVBoxLayout(self)
        
        # Groupe données de naissance
        birth_group = QGroupBox("Données de Naissance")
        birth_layout = QFormLayout()
        
        # Date
        birth_layout.addRow("Date:", self.create_date_field())
        
        # Heure
        birth_layout.addRow("Heure:", self.create_time_field())
        
        # Fuseau horaire
        birth_layout.addRow("Fuseau horaire:", self.create_timezone_field())
        
        # Lieu
        location_group = QGroupBox("Lieu de Naissance")
        location_layout = QFormLayout()
        
        # Ville
        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("Entrez une ville...")
        location_layout.addRow("Ville:", self.city_edit)
        
        # Coordonnées
        coords_layout = QHBoxLayout()
        
        # Latitude
        lat_layout = QFormLayout()
        self.lat_spin = QDoubleSpinBox()
        self.lat_spin.setRange(-90, 90)
        self.lat_spin.setDecimals(4)
        self.lat_spin.setValue(48.8566)  # Paris par défaut
        self.lat_spin.setSuffix("°")
        lat_layout.addRow("Latitude:", self.lat_spin)
        
        # Longitude
        lon_layout = QFormLayout()
        self.lon_spin = QDoubleSpinBox()
        self.lon_spin.setRange(-180, 180)
        self.lon_spin.setDecimals(4)
        self.lon_spin.setValue(2.3522)  # Paris par défaut
        self.lon_spin.setSuffix("°")
        lon_layout.addRow("Longitude:", self.lon_spin)
        
        coords_layout.addLayout(lat_layout)
        coords_layout.addLayout(lon_layout)
        location_layout.addRow("Coordonnées:", coords_layout)
        
        location_group.setLayout(location_layout)
        
        # Système de maisons
        birth_layout.addRow("Système de maisons:", self.create_house_system_field())
        
        birth_group.setLayout(birth_layout)
        
        # Bouton calculer
        self.calculate_btn = QPushButton("🌟 Calculer le Thème")
        self.calculate_btn.clicked.connect(self.on_calculate)
        self.calculate_btn.setObjectName("calculateButton")
        
        layout.addWidget(birth_group)
        layout.addWidget(location_group)
        layout.addWidget(self.calculate_btn)
        layout.addStretch()
    
    def create_date_field(self) -> QWidget:
        """Crée le champ de date"""
        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setCalendarPopup(True)
        
        # Bouton "Aujourd'hui"
        today_btn = QPushButton("Aujourd'hui")
        today_btn.clicked.connect(lambda: self.date_edit.setDate(QDate.currentDate()))
        
        date_layout.addWidget(self.date_edit)
        date_layout.addWidget(today_btn)
        date_layout.addStretch()
        
        return date_widget
    
    def create_time_field(self) -> QWidget:
        """Crée le champ d'heure"""
        time_widget = QWidget()
        time_layout = QHBoxLayout(time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setDisplayFormat("HH:mm")
        
        # Boutons rapides
        noon_btn = QPushButton("12h00")
        noon_btn.clicked.connect(lambda: self.time_edit.setTime(QTime(12, 0)))
        
        unknown_btn = QPushButton("Heure inconnue")
        unknown_btn.clicked.connect(lambda: self.time_edit.setTime(QTime(12, 0)))
        
        time_layout.addWidget(self.time_edit)
        time_layout.addWidget(noon_btn)
        time_layout.addWidget(unknown_btn)
        time_layout.addStretch()
        
        return time_widget
    
    def create_timezone_field(self) -> QComboBox:
        """Crée le champ de fuseauJe vais continuer avec le reste du formulaire et les autres composants de l'interface :

### Suite de `gui/forms.py`

```python
    def create_timezone_field(self) -> QComboBox:
        """Crée le champ de fuseau horaire"""
        self.timezone_combo = QComboBox()
        
        # Fuseaux horaires courants
        common_timezones = [
            "Europe/Paris", "Europe/London", "Europe/Berlin", "Europe/Rome",
            "America/New_York", "America/Los_Angeles", "America/Chicago", "America/Toronto",
            "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata", "Asia/Dubai",
            "Australia/Sydney", "Australia/Melbourne",
            "UTC"
        ]
        
        self.timezone_combo.addItems(common_timezones)
        self.timezone_combo.setCurrentText("Europe/Paris")
        
        return self.timezone_combo
    
    def create_house_system_field(self) -> QComboBox:
        """Crée le champ de système de maisons"""
        self.house_system_combo = QComboBox()
        
        house_systems = {
            "Placidus": "P",
            "Koch": "K",
            "Campanus": "C", 
            "Regiomontanus": "R",
            "Equal": "E",
            "Porphyry": "O"
        }
        
        for name, code in house_systems.items():
            self.house_system_combo.addItem(name, code)
        
        self.house_system_combo.setCurrentText("Placidus")
        
        return self.house_system_combo
    
    def on_calculate(self):
        """Validation et émission du signal"""
        # Validation basique
        if not self.city_edit.text().strip():
            self.city_edit.setStyleSheet("border: 2px solid #e94560;")
            return
        
        self.city_edit.setStyleSheet("")
        self.calculate_clicked.emit()
    
    def get_data(self) -> Optional[Dict]:
        """Retourne les données du formulaire"""
        try:
            date = self.date_edit.date().toPython()
            time = self.time_edit.time().toPython()
            
            # Combiner date et heure
            datetime_obj = datetime.combine(date, time)
            
            return {
                'date': datetime_obj,
                'timezone': self.timezone_combo.currentText(),
                'latitude': self.lat_spin.value(),
                'longitude': self.lon_spin.value(),
                'house_system': self.house_system_combo.currentData(),
                'city': self.city_edit.text().strip()
            }
        except Exception as e:
            print(f"Erreur lors de la récupération des données : {e}")
            return None
    
    def set_location(self, city: str, latitude: float, longitude: float, timezone: str):
        """Définit les données de localisation"""
        self.city_edit.setText(city)
        self.lat_spin.setValue(latitude)
        self.lon_spin.setValue(longitude)
        
        # Trouver le fuseau horaire
        index = self.timezone_combo.findText(timezone)
        if index >= 0:
            self.timezone_combo.setCurrentIndex(index)
    
    def clear(self):
        """Efface le formulaire"""
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit.setTime(QTime.currentTime())
        self.city_edit.clear()
        self.lat_spin.setValue(48.8566)
        self.lon_spin.setValue(2.3522)
        self.timezone_combo.setCurrentText("Europe/Paris")


class TransitForm(QWidget):
    """Formulaire pour calculer les transits"""
    
    calculate_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        
        # Données natales (lecture seule)
        natal_group = QGroupBox("Données Natales")
        natal_layout = QFormLayout()
        
        self.natal_date_label = QLabel()
        self.natal_time_label = QLabel()
        self.natal_place_label = QLabel()
        
        natal_layout.addRow("Date natale:", self.natal_date_label)
        natal_layout.addRow("Heure natale:", self.natal_time_label)
        natal_layout.addRow("Lieu natal:", self.natal_place_label)
        
        natal_group.setLayout(natal_layout)
        
        # Date des transits
        transit_group = QGroupBox("Date des Transits")
        transit_layout = QFormLayout()
        
        self.transit_date = QDateEdit()
        self.transit_date.setDate(QDate.currentDate())
        self.transit_date.setDisplayFormat("dd/MM/yyyy")
        
        self.transit_time = QTimeEdit()
        self.transit_time.setTime(QTime.currentTime())
        self.transit_time.setDisplayFormat("HH:mm")
        
        transit_layout.addRow("Date:", self.transit_date)
        transit_layout.addRow("Heure:", self.transit_time)
        
        transit_group.setLayout(transit_layout)
        
        # Bouton calculer
        self.calculate_btn = QPushButton("🔄 Calculer les Transits")
        self.calculate_btn.clicked.connect(self.calculate_clicked.emit)
        
        layout.addWidget(natal_group)
        layout.addWidget(transit_group)
        layout.addWidget(self.calculate_btn)
        layout.addStretch()
    
    def set_natal_data(self, natal_data: Dict):
        """Définit les données natales"""
        self.natal_date_label.setText(natal_data['date'].strftime("%d/%m/%Y"))
        self.natal_time_label.setText(natal_data['date'].strftime("%H:%M"))
        self.natal_place_label.setText(f"{natal_data['city']} ({natal_data['latitude']:.2f}°, {natal_data['longitude']:.2f}°)")
    
    def get_data(self) -> Optional[Dict]:
        """Retourne les données de transit"""
        try:
            date = self.transit_date.date().toPython()
            time = self.transit_time.time().toPython()
            
            datetime_obj = datetime.combine(date, time)
            
            return {
                'date': datetime_obj
            }
        except Exception as e:
            print(f"Erreur : {e}")
            return None


class CompatibilityForm(QWidget):
    """Formulaire pour la compatibilité"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title_label = None
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout(self)
        
        # Titre (sera défini plus tard)
        self.title_label = QLabel("Personne")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #4fbdba;")
        layout.addWidget(self.title_label)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Date:", self.date_edit)
        
        # Heure
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setDisplayFormat("HH:mm")
        form_layout.addRow("Heure:", self.time_edit)
        
        # Lieu
        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("Ville, Pays")
        form_layout.addRow("Lieu:", self.city_edit)
        
        # Coordonnées
        coords_layout = QHBoxLayout()
        
        self.lat_spin = QDoubleSpinBox()
        self.lat_spin.setRange(-90, 90)
        self.lat_spin.setDecimals(4)
        self.lat_spin.setValue(48.8566)
        self.lat_spin.setSuffix("°")
        
        self.lon_spin = QDoubleSpinBox()
        self.lon_spin.setRange(-180, 180)
        self.lon_spin.setDecimals(4)
        self.lon_spin.setValue(2.3522)
        self.lon_spin.setSuffix("°")
        
        coords_layout.addWidget(QLabel("Lat:"))
        coords_layout.addWidget(self.lat_spin)
        coords_layout.addWidget(QLabel("Lon:"))
        coords_layout.addWidget(self.lon_spin)
        
        form_layout.addRow("Coordonnées:", coords_layout)
        
        layout.addLayout(form_layout)
        layout.addStretch()
    
    def set_title(self, title: str):
        """Définit le titre du formulaire"""
        if self.title_label:
            self.title_label.setText(title)
    
    def get_data(self) -> Optional[Dict]:
        """Retourne les données du formulaire"""
        try:
            date = self.date_edit.date().toPython()
            time = self.time_edit.time().toPython()
            
            datetime_obj = datetime.combine(date, time)
            
            return {
                'date': datetime_obj,
                'latitude': self.lat_spin.value(),
                'longitude': self.lon_spin.value(),
                'city': self.city_edit.text().strip()
            }
        except Exception as e:
            print(f"Erreur : {e}")
            return None
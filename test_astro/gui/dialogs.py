"""
Dialogues modaux pour l'interface graphique
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QLabel, QTextEdit, QTabWidget, QDialogButtonBox,
    QListWidget, QListWidgetItem, QFrame
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from typing import Dict


class SettingsDialog(QDialog):
    """Dialogue des paramètres de l'application"""
    
    def __init__(self, current_config: Dict, parent=None):
        super().__init__(parent)
        self.current_config = current_config.copy()
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface"""
        self.setWindowTitle("Préférences")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Onglets
        tabs = QTabWidget()
        
        # Onglet Général
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "Général")
        
        # Onglet Calcul
        calc_tab = self.create_calculation_tab()
        tabs.addTab(calc_tab, "Calcul")
        
        # Onglet Affichage
        display_tab = self.create_display_tab()
        tabs.addTab(display_tab, "Affichage")
        
        layout.addWidget(tabs)
        
        # Boutons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        
        layout.addWidget(buttons)
    
    def create_general_tab(self):
        """Crée l'onglet général"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Langue
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Français", "English", "Español"])
        self.language_combo.setCurrentText("Français")
        layout.addRow("Langue:", self.language_combo)
        
        # Format de date
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(["JJ/MM/AAAA", "MM/JJ/AAAA", "AAAA-MM-JJ"])
        layout.addRow("Format de date:", self.date_format_combo)
        
        # Format d'heure
        self.time_format_combo = QComboBox()
        self.time_format_combo.addItems(["24h", "12h (AM/PM)"])
        layout.addRow("Format d'heure:", self.time_format_combo)
        
        # Unités
        self.units_combo = QComboBox()
        self.units_combo.addItems(["Métrique", "Impérial"])
        layout.addRow("Unités:", self.units_combo)
        
        # Sauvegarde automatique
        self.auto_save_check = QCheckBox("Sauvegarde automatique")
        self.auto_save_check.setChecked(True)
        layout.addRow(self.auto_save_check)
        
        # Intervalle de sauvegarde
        self.auto_save_spin = QSpinBox()
        self.auto_save_spin.setRange(1, 60)
        self.auto_save_spin.setSuffix(" minutes")
        self.auto_save_spin.setValue(10)
        layout.addRow("Intervalle:", self.auto_save_spin)
        
        return widget
    
    def create_calculation_tab(self):
        """Crée l'onglet de calcul"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Système de maisons par défaut
        self.default_house_combo = QComboBox()
        house_systems = ["Placidus", "Koch", "Campanus", "Regiomontanus", "Equal", "Porphyry"]
        self.default_house_combo.addItems(house_systems)
        
        current_house = [name for name, code in HOUSE_SYSTEMS.items() 
                        if code == self.current_config.get('house_system', 'P')][0]
        self.default_house_combo.setCurrentText(current_house)
        layout.addRow("Système de maisons:", self.default_house_combo)
        
        # Orb des aspects
        self.orb_spin = QDoubleSpinBox()
        self.orb_spin.setRange(0.1, 15.0)
        self.orb_spin.setSingleStep(0.5)
        self.orb_spin.setSuffix("°")
        self.orb_spin.setValue(8.0)
        layout.addRow("Orb par défaut:", self.orb_spin)
        
        # Planètes à inclure
        planets_group = QGroupBox("Planètes à inclure dans les calculs")
        planets_layout = QVBoxLayout()
        
        self.planet_checks = {}
        planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                  'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
        
        for planet in planets:
            check = QCheckBox(planet)
            check.setChecked(planet in self.current_config.get('planets', []))
            planets_layout.addWidget(check)
            self.planet_checks[planet] = check
        
        planets_group.setLayout(planets_layout)
        layout.addRow(planets_group)
        
        # Éphémérides
        self.ephemeris_check = QCheckBox("Utiliser les éphémérides Swiss Ephemeris")
        self.ephemeris_check.setChecked(self.current_config.get('use_ephemeris', True))
        layout.addRow(self.ephemeris_check)
        
        # Précision
        self.precision_combo = QComboBox()
        self.precision_combo.addItems(["Standard", "Haute", "Maximum"])
        layout.addRow("Précision:", self.precision_combo)
        
        return widget
    
    def create_display_tab(self):
        """Crée l'onglet d'affichage"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Thème de couleur
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Sombre", "Clair", "Automatique"])
        layout.addRow("Thème:", self.theme_combo)
        
        # Animations
        self.animations_check = QCheckBox("Activer les animations")
        self.animations_check.setChecked(True)
        layout.addRow(self.animations_check)
        
        # Affichage par défaut
        display_group = QGroupBox("Éléments à afficher par défaut")
        display_layout = QVBoxLayout()
        
        self.show_grid_check = QCheckBox("Grille")
        self.show_grid_check.setChecked(True)
        display_layout.addWidget(self.show_grid_check)
        
        self.show_aspects_check = QCheckBox("Aspects")
        self.show_aspects_check.setChecked(True)
        display_layout.addWidget(self.show_aspects_check)
        
        self.show_planets_check = QCheckBox("Planètes")
        self.show_planets_check.setChecked(True)
        display_layout.addWidget(self.show_planets_check)
        
        self.show_houses_check = QCheckBox("Maisons")
        self.show_houses_check.setChecked(True)
        display_layout.addWidget(self.show_houses_check)
        
        self.show_zodiac_check = QCheckBox("Zodiaque")
        self.show_zodiac_check.setChecked(True)
        display_layout.addWidget(self.show_zodiac_check)
        
        display_group.setLayout(display_layout)
        layout.addRow(display_group)
        
        # Taille des symboles
        self.symbol_size_spin = QSpinBox()
        self.symbol_size_spin.setRange(8, 24)
        self.symbol_size_spin.setSuffix(" px")
        self.symbol_size_spin.setValue(12)
        layout.addRow("Taille des symboles:", self.symbol_size_spin)
        
        return widget
    
    def apply_settings(self):
        """Applique les paramètres sans fermer la fenêtre"""
        # Mettre à jour la configuration
        self.current_config['house_system'] = HOUSE_SYSTEMS[self.default_house_combo.currentText()]
        self.current_config['use_ephemeris'] = self.ephemeris_check.isChecked()
        
        # Mettre à jour la liste des planètes
        selected_planets = [planet for planet, check in self.planet_checks.items() 
                           if check.isChecked()]
        self.current_config['planets'] = selected_planets
        
        # Émettre un signal ou notifier que les paramètres ont changé
        print("Paramètres appliqués")
    
    def get_config(self) -> Dict:
        """Retourne la configuration modifiée"""
        self.apply_settings()  # S'assurer que la dernière configuration est appliquée
        return self.current_config.copy()


class AboutDialog(QDialog):
    """Dialogue À propos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface"""
        self.setWindowTitle("À propos d'Astrolog Python")
        self.setModal(True)
        self.resize(400, 500)
        
        layout = QVBoxLayout(self)
        
        # Logo ou icône
        logo_label = QLabel("✦")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 72px; color: #4fbdba;")
        layout.addWidget(logo_label)
        
        # Titre
        title_label = QLabel("Astrolog Python")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4fbdba;")
        layout.addWidget(title_label)
        
        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #eee;")
        layout.addWidget(version_label)
        
        # Description
        desc_text = """
        <p style='color: #eee; text-align: center;'>
        Calculateur de thèmes nataux et d'astrologie moderne<br>
        Basé sur les algorithmes d'Astrolog 7.80<br><br>
        
        Fonctionnalités :<br>
        • Calculs précis des positions planétaires<br>
        • Systèmes de maisons multiples<br>
        • Aspects et configurations<br>
        • Transits et progressions<br>
        • Compatibilité (synastrie)<br>
        • Éphémérides complètes<br><br>
        
        © 2024 Astrolog Python<br>
        Logiciel libre sous licence GPL-3.0
        </p>
        """
        
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        desc_label.setOpenExternalLinks(True)
        layout.addWidget(desc_label)
        
        # Bouton
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class ExportDialog(QDialog):
    """Dialogue d'export des résultats"""
    
    def __init__(self, chart_data: Dict, parent=None):
        super().__init__(parent)
        self.chart_data = chart_data
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface"""
        self.setWindowTitle("Exporter le thème")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Options d'export
        options_group = QGroupBox("Options d'export")
        options_layout = QVBoxLayout()
        
        self.pdf_check = QCheckBox("Exporter en PDF")
        self.pdf_check.setChecked(True)
        options_layout.addWidget(self.pdf_check)
        
        self.svg_check = QCheckBox("Exporter la carte en SVG")
        self.svg_check.setChecked(True)
        options_layout.addWidget(self.svg_check)
        
        self.json_check = QCheckBox("Exporter les données (JSON)")
        self.json_check.setChecked(True)
        options_layout.addWidget(self.json_check)
        
        self.txt_check = QCheckBox("Exporter le rapport texte")
        self.txt_check.setChecked(True)
        options_layout.addWidget(self.txt_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Contenu à exporter
        content_group = QGroupBox("Contenu")
        content_layout = QVBoxLayout()
        
        self.positions_check = QCheckBox("Positions planétaires")
        self.positions_check.setChecked(True)
        content_layout.addWidget(self.positions_check)
        
        self.aspects_check = QCheckBox("Table des aspects")
        self.aspects_check.setChecked(True)
        content_layout.addWidget(self.aspects_check)
        
        self.houses_check = QCheckBox("Maisons")
        self.houses_check.setChecked(True)
        content_layout.addWidget(self.houses_check)
        
        self.interpretations_check = QCheckBox("Interprétations")
        self.interpretations_check.setChecked(True)
        content_layout.addWidget(self.interpretations_check)
        
        content_group.setLayout(content_layout)
        layout.addWidget(content_group)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.export)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
    
    def export(self):
        """Effectue l'export"""
        from PySide6.QtWidgets import QFileDialog
        
        # Demander le nom de fichier
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Exporter le thème", "", "PDF Files (*.pdf);;All Files (*)")
        
        if file_name:
            # Ici, vous appelleriez vos fonctions d'export réelles
            # Pour l'instant, on simule l'export
            exported_formats = []
            
            if self.pdf_check.isChecked():
                exported_formats.append("PDF")
            
            if self.svg_check.isChecked():
                exported_formats.append("SVG")
            
            if self.json_check.isChecked():
                exported_formats.append("JSON")
            
            if self.txt_check.isChecked():
                exported_formats.append("texte")
            
            print(f"Export du thème en formats : {', '.join(exported_formats)}")
            
            self.accept()
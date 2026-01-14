"""
Fenêtre principale de l'interface graphique Astrolog Python
Interface moderne avec Qt6/PySide6
"""

import sys
from datetime import datetime
from typing import Optional, Dict
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QGroupBox, QPushButton, QLabel, QLineEdit, QDateEdit,
    QTimeEdit, QComboBox, QTextEdit, QTableWidget, QTableWidgetItem,
    QSplitter, QFrame, QGraphicsView, QGraphicsScene, QMessageBox,
    QProgressDialog, QDialog, QDialogButtonBox, QScrollArea
)
from PySide6.QtCore import (
    Qt, QDate, QTime, QTimer, QPropertyAnimation, QRect, QEasingCurve,
    Signal, Slot, QPointF
)
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPixmap, QPainterPath,
    QLinearGradient, QRadialGradient, QPolygonF, QTransform
)
from PySide6.QtCharts import (
    QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis,
    QValueAxis, QScatterSeries, QLineSeries
)

from ..core.calculator import AstrologicalCalculator
from ..core.constants import *
from .chart_widget import AstrologicalChartWidget
from .forms import BirthDataForm, TransitForm, CompatibilityForm
from .dialogs import SettingsDialog, AboutDialog, ExportDialog


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application Astrolog Python"""
    
    def __init__(self):
        super().__init__()
        self.calculator = AstrologicalCalculator()
        self.current_chart = None
        self.charts_history = []
        
        self.init_ui()
        self.apply_modern_style()
        self.setup_animations()
        
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("✦ Astrolog Python - Calculateur de Thèmes Nataux")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Créer les sections
        self.create_navigation_panel()
        self.create_main_content()
        self.create_status_bar()
        
        # Ajouter au layout principal
        main_layout.addWidget(self.nav_panel)
        main_layout.addWidget(self.main_content, 1)
        
        # Menu et barre d'outils
        self.create_menu_bar()
        self.create_tool_bar()
        
    def create_navigation_panel(self):
        """Crée le panneau de navigation latéral"""
        self.nav_panel = QWidget()
        self.nav_panel.setFixedWidth(250)
        self.nav_panel.setObjectName("navPanel")
        
        nav_layout = QVBoxLayout(self.nav_panel)
        nav_layout.setSpacing(10)
        nav_layout.setContentsMargins(20, 20, 20, 20)
        
        # Logo
        logo_label = QLabel("✦ ASTROLOG")
        logo_label.setObjectName("logo")
        logo_label.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(logo_label)
        
        # Boutons de navigation
        nav_buttons = [
            ("🌟 Thème Natal", "natal"),
            ("🔄 Transits", "transits"),
            ("💞 Compatibilité", "compatibility"),
            ("📊 Éphémérides", "ephemeris"),
            ("⚙️ Paramètres", "settings")
        ]
        
        self.nav_buttons = {}
        for text, name in nav_buttons:
            btn = QPushButton(text)
            btn.setObjectName(f"navBtn_{name}")
            btn.clicked.connect(lambda checked, x=name: self.switch_tab(x))
            nav_layout.addWidget(btn)
            self.nav_buttons[name] = btn
        
        nav_layout.addStretch()
        
        # Quick actions
        quick_group = QGroupBox("Actions Rapides")
        quick_layout = QVBoxLayout()
        
        quick_calc_btn = QPushButton("🕐 Maintenant")
        quick_calc_btn.clicked.connect(self.quick_calculation)
        quick_layout.addWidget(quick_calc_btn)
        
        quick_group.setLayout(quick_layout)
        nav_layout.addWidget(quick_group)
    
    def create_main_content(self):
        """Crée le contenu principal avec onglets"""
        self.main_content = QWidget()
        self.main_content.setObjectName("mainContent")
        
        # Layout principal du contenu
        content_layout = QVBoxLayout(self.main_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("mainTabs")
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Créer les onglets
        self.create_natal_tab()
        self.create_transits_tab()
        self.create_compatibility_tab()
        self.create_ephemeris_tab()
        
        content_layout.addWidget(self.tab_widget)
    
    def create_natal_tab(self):
        """Crée l'onglet du thème natal"""
        natal_widget = QWidget()
        natal_layout = QHBoxLayout(natal_widget)
        
        # Séparateur
        splitter = QSplitter(Qt.Horizontal)
        
        # Panneau de gauche : formulaire
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Formulaire de données de naissance
        self.birth_form = BirthDataForm()
        self.birth_form.calculate_clicked.connect(self.calculate_natal_chart)
        left_layout.addWidget(self.birth_form)
        
        # Ajouter le graphique de répartition élémentaire
        elements_group = QGroupBox("Répartition Élémentaire")
        elements_layout = QVBoxLayout()
        self.element_chart = self.create_element_chart()
        elements_layout.addWidget(self.element_chart)
        elements_group.setLayout(elements_layout)
        left_layout.addWidget(elements_group)
        
        splitter.addWidget(left_panel)
        
        # Panneau central : carte du ciel
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        
        # Carte astrologique
        self.chart_widget = AstrologicalChartWidget()
        center_layout.addWidget(self.chart_widget)
        
        splitter.addWidget(center_panel)
        
        # Panneau de droite : résultats
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Table des positions
        positions_group = QGroupBox("Positions Planétaires")
        positions_layout = QVBoxLayout()
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(4)
        self.positions_table.setHorizontalHeaderLabels(["Planète", "Signe", "Degré", "Maison"])
        positions_layout.addWidget(self.positions_table)
        positions_group.setLayout(positions_layout)
        right_layout.addWidget(positions_group)
        
        # Table des aspects
        aspects_group = QGroupBox("Aspects Principaux")
        aspects_layout = QVBoxLayout()
        self.aspects_table = QTableWidget()
        self.aspects_table.setColumnCount(5)
        self.aspects_table.setHorizontalHeaderLabels(["Planètes", "Aspect", "Orb", "Type", ""])
        aspects_layout.addWidget(self.aspects_table)
        aspects_group.setLayout(aspects_layout)
        right_layout.addWidget(aspects_group)
        
        splitter.addWidget(right_panel)
        
        # Définir les proportions
        splitter.setSizes([300, 500, 400])
        
        natal_layout.addWidget(splitter)
        
        self.tab_widget.addTab(natal_widget, "🌟 Thème Natal")
    
    def create_transits_tab(self):
        """Crée l'onglet des transits"""
        transits_widget = QWidget()
        transits_layout = QVBoxLayout(transits_widget)
        
        # Formulaire de transits
        self.transit_form = TransitForm()
        self.transit_form.calculate_clicked.connect(self.calculate_transits)
        transits_layout.addWidget(self.transit_form)
        
        # Résultats des transits
        results_widget = QWidget()
        results_layout = QHBoxLayout(results_widget)
        
        # Liste des transits actifs
        left_results = QWidget()
        left_layout = QVBoxLayout(left_results)
        
        transits_list_group = QGroupBox("Transits Actifs")
        transits_list_layout = QVBoxLayout()
        self.transits_list = QTextEdit()
        self.transits_list.setReadOnly(True)
        transits_list_layout.addWidget(self.transits_list)
        transits_list_group.setLayout(transits_list_layout)
        left_layout.addWidget(transits_list_group)
        
        results_layout.addWidget(left_results)
        
        # Graphique des transits
        right_results = QWidget()
        right_layout = QVBoxLayout(right_results)
        
        self.transits_chart = self.create_transits_chart()
        right_layout.addWidget(self.transits_chart)
        
        results_layout.addWidget(right_results)
        
        transits_layout.addWidget(results_widget)
        
        self.tab_widget.addTab(transits_widget, "🔄 Transits")
    
    def create_compatibility_tab(self):
        """Crée l'onglet de compatibilité"""
        compatibility_widget = QWidget()
        compatibility_layout = QHBoxLayout(compatibility_widget)
        
        # Formulaires pour les deux personnes
        left_form = CompatibilityForm()
        left_form.set_title("Personne 1")
        self.compatibility_form1 = left_form
        
        right_form = CompatibilityForm()
        right_form.set_title("Personne 2")
        self.compatibility_form2 = right_form
        
        # Bouton de calcul
        calculate_btn = QPushButton("Calculer la Compatibilité")
        calculate_btn.clicked.connect(self.calculate_compatibility)
        
        # Résultats
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Score de compatibilité
        score_group = QGroupBox("Score de Compatibilité")
        score_layout = QVBoxLayout()
        self.compatibility_score_label = QLabel("0%")
        self.compatibility_score_label.setAlignment(Qt.AlignCenter)
        self.compatibility_score_label.setObjectName("compatibilityScore")
        score_layout.addWidget(self.compatibility_score_label)
        score_group.setLayout(score_layout)
        results_layout.addWidget(score_group)
        
        # Aspects de synastrie
        synastry_group = QGroupBox("Aspects de Synastrie")
        synastry_layout = QVBoxLayout()
        self.synastry_table = QTableWidget()
        self.synastry_table.setColumnCount(4)
        self.synastry_table.setHorizontalHeaderLabels(["Planètes", "Aspect", "Orb", "Score"])
        synastry_layout.addWidget(self.synastry_table)
        synastry_group.setLayout(synastry_layout)
        results_layout.addWidget(synastry_group)
        
        compatibility_layout.addWidget(left_form)
        compatibility_layout.addWidget(right_form)
        compatibility_layout.addWidget(calculate_btn)
        compatibility_layout.addWidget(results_widget)
        
        self.tab_widget.addTab(compatibility_widget, "💞 Compatibilité")
    
    def create_ephemeris_tab(self):
        """Crée l'onglet des éphémérides"""
        ephemeris_widget = QWidget()
        ephemeris_layout = QVBoxLayout(ephemeris_widget)
        
        # Contrôles
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        
        controls_layout.addWidget(QLabel("Date:"))
        self.ephemeris_date = QDateEdit()
        self.ephemeris_date.setDate(QDate.currentDate())
        controls_layout.addWidget(self.ephemeris_date)
        
        controls_layout.addWidget(QLabel("Durée:"))
        self.ephemeris_duration = QComboBox()
        self.ephemeris_duration.addItems(["1 jour", "1 semaine", "1 mois", "3 mois"])
        controls_layout.addWidget(self.ephemeris_duration)
        
        calculate_btn = QPushButton("Calculer")
        calculate_btn.clicked.connect(self.calculate_ephemeris)
        controls_layout.addWidget(calculate_btn)
        
        controls_layout.addStretch()
        
        ephemeris_layout.addWidget(controls_widget)
        
        # Table des éphémérides
        self.ephemeris_table = QTableWidget()
        self.ephemeris_table.setColumnCount(8)
        self.ephemeris_table.setHorizontalHeaderLabels([
            "Date", "Soleil", "Lune", "Mercure", "Vénus", "Mars", "Jupiter", "Saturne"
        ])
        ephemeris_layout.addWidget(self.ephemeris_table)
        
        self.tab_widget.addTab(ephemeris_widget, "📊 Éphémérides")
    
    def apply_modern_style(self):
        """Applique un style moderne et élégant"""
        style_sheet = """
        /* Style général */
        QMainWindow {
            background-color: #1a1a2e;
        }
        
        /* Panneau de navigation */
        #navPanel {
            background-color: #16213e;
            border-right: 1px solid #4fbdba;
        }
        
        #logo {
            color: #4fbdba;
            font-size: 24px;
            font-weight: bold;
            padding: 20px;
        }
        
        /* Boutons de navigation */
        QPushButton[name^="navBtn"] {
            background-color: transparent;
            color: #eee;
            border: none;
            padding: 15px;
            text-align: left;
            font-size: 14px;
            border-radius: 8px;
            margin: 2px;
        }
        
        QPushButton[name^="navBtn"]:hover {
            background-color: rgba(79, 189, 186, 0.2);
            color: #4fbdba;
        }
        
        QPushButton[name^="navBtn"]:pressed {
            background-color: rgba(79, 189, 186, 0.3);
        }
        
        /* Contenu principal */
        #mainContent {
            background-color: #0f3460;
        }
        
        /* Onglets */
        QTabWidget::pane {
            border: none;
            background-color: #0f3460;
        }
        
        QTabBar::tab {
            background-color: #16213e;
            color: #eee;
            padding: 15px 25px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }
        
        QTabBar::tab:selected {
            background-color: #4fbdba;
            color: #1a1a2e;
        }
        
        QTabBar::tab:hover {
            background-color: rgba(79, 189, 186, 0.7);
        }
        
        /* Boutons */
        QPushButton {
            background-color: #4fbdba;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background-color: #7ec8e3;
            transform: translateY(-2px);
        }
        
        QPushButton:pressed {
            background-color: #3da9a6;
        }
        
        QPushButton:disabled {
            background-color: #555;
            color: #999;
        }
        
        /* Groupes */
        QGroupBox {
            color: #4fbdba;
            font-weight: bold;
            border: 2px solid #4fbdba;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        /* Tables */
        QTableWidget {
            background-color: #16213e;
            color: #eee;
            border: 1px solid #4fbdba;
            border-radius: 8px;
            gridline-color: #4fbdba;
            selection-background-color: rgba(79, 189, 186, 0.3);
        }
        
        QTableWidget::item {
            padding: 8px;
        }
        
        QHeaderView::section {
            background-color: #16213e;
            color: #4fbdba;
            padding: 10px;
            border: 1px solid #4fbdba;
            font-weight: bold;
        }
        
        /* Labels */
        QLabel {
            color: #eee;
            font-size: 13px;
        }
        
        QLabel#compatibilityScore {
            font-size: 48px;
            font-weight: bold;
            color: #4fbdba;
            padding: 20px;
        }
        
        /* ScrollBar */
        QScrollBar:vertical {
            background-color: #16213e;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #4fbdba;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #7ec8e3;
        }
        
        /* LineEdit */
        QLineEdit {
            background-color: #16213e;
            color: #eee;
            border: 2px solid #4fbdba;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
        }
        
        QLineEdit:focus {
            border-color: #7ec8e3;
            outline: none;
        }
        
        /* ComboBox */
        QComboBox {
            background-color: #16213e;
            color: #eee;
            border: 2px solid #4fbdba;
            border-radius: 8px;
            padding: 10px;
        }
        
        QComboBox::drop-down {
            border: none;
            padding-right: 15px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #4fbdba;
            width: 0;
            height: 0;
        }
        
        /* Date/Time Edit */
        QDateEdit, QTimeEdit {
            background-color: #16213e;
            color: #eee;
            border: 2px solid #4fbdba;
            border-radius: 8px;
            padding: 8px;
        }
        
        /* TextEdit */
        QTextEdit {
            background-color: #16213e;
            color: #eee;
            border: 2px solid #4fbdba;
            border-radius: 8px;
            padding: 10px;
            font-family: 'Courier New', monospace;
        }
        
        /* StatusBar */
        QStatusBar {
            background-color: #16213e;
            color: #4fbdba;
            border-top: 1px solid #4fbdba;
        }
        """
        
        self.setStyleSheet(style_sheet)
    
    def setup_animations(self):
        """Configure les animations fluides"""
        # Animation de la carte
        self.chart_animation = QPropertyAnimation(self.chart_widget, b"geometry")
        self.chart_animation.setDuration(1000)
        self.chart_animation.setEasingCurve(QEasingCurve.OutBack)
    
    def create_menu_bar(self):
        """Crée la barre de menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")
        
        new_action = file_menu.addAction("Nouveau thème")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_chart)
        
        open_action = file_menu.addAction("Ouvrir")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_chart)
        
        save_action = file_menu.addAction("Sauvegarder")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_chart)
        
        file_menu.addSeparator()
        
        export_action = file_menu.addAction("Exporter...")
        export_action.triggered.connect(self.export_chart)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Quitter")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Menu Calcul
        calc_menu = menubar.addMenu("Calcul")
        
        calc_natal_action = calc_menu.addAction("Calculer thème natal")
        calc_natal_action.triggered.connect(self.calculate_natal_chart)
        
        calc_transits_action = calc_menu.addAction("Calculer transits")
        calc_transits_action.triggered.connect(self.calculate_transits)
        
        calc_compatibility_action = calc_menu.addAction("Calculer compatibilité")
        calc_compatibility_action.triggered.connect(self.calculate_compatibility)
        
        # Menu Affichage
        view_menu = menubar.addMenu("Affichage")
        
        self.show_grid_action = view_menu.addAction("Grille")
        self.show_grid_action.setCheckable(True)
        self.show_grid_action.setChecked(True)
        
        self.show_aspects_action = view_menu.addAction("Aspects")
        self.show_aspects_action.setCheckable(True)
        self.show_aspects_action.setChecked(True)
        
        self.show_planets_action = view_menu.addAction("Planètes")
        self.show_planets_action.setCheckable(True)
        self.show_planets_action.setChecked(True)
        
        # Menu Outils
        tools_menu = menubar.addMenu("Outils")
        
        ephemeris_action = tools_menu.addAction("Éphémérides")
        ephemeris_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        
        atlas_action = tools_menu.addAction("Atlas")
        atlas_action.triggered.connect(self.open_atlas)
        
        settings_action = tools_menu.addAction("Préférences")
        settings_action.triggered.connect(self.open_settings)
        
        # Menu Aide
        help_menu = menubar.addMenu("Aide")
        
        about_action = help_menu.addAction("À propos")
        about_action.triggered.connect(self.show_about)
        
        help_action = help_menu.addAction("Aide")
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
    
    def create_tool_bar(self):
        """Crée la barre d'outils"""
        toolbar = self.addToolBar("Principal")
        toolbar.setObjectName("mainToolbar")
        
        # Actions rapides
        toolbar.addAction("🌟", self.calculate_natal_chart).setToolTip("Calculer thème natal")
        toolbar.addAction("🔄", self.calculate_transits).setToolTip("Calculer transits")
        toolbar.addAction("💞", self.calculate_compatibility).setToolTip("Calculer compatibilité")
        
        toolbar.addSeparator()
        
        toolbar.addAction("💾", self.save_chart).setToolTip("Sauvegarder")
        toolbar.addAction("📤", self.export_chart).setToolTip("Exporter")
        
        toolbar.addSeparator()
        
        toolbar.addAction("⚙️", self.open_settings).setToolTip("Paramètres")
    
    def create_status_bar(self):
        """Crée la barre de statut"""
        self.statusBar().showMessage("Prêt - Entrez les données de naissance pour calculer un thème")
    
    def create_element_chart(self) -> QChartView:
        """Crée un graphique circulaire des éléments"""
        chart = QChart()
        chart.setTitle("Répartition Élémentaire")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        series = QPieSeries()
        series.append("Feu", 25)
        series.append("Terre", 25)
        series.append("Air", 25)
        series.append("Eau", 25)
        
        # Couleurs des éléments
        colors = ["#FF6B6B", "#8B4513", "#87CEEB", "#4169E1"]
        for i, slice in enumerate(series.slices()):
            slice.setBrush(QColor(colors[i]))
            slice.setLabelVisible(True)
        
        chart.addSeries(series)
        chart.legend().setAlignment(Qt.AlignRight)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setMinimumHeight(200)
        
        return chart_view
    
    def create_transits_chart(self) -> QChartView:
        """Crée un graphique pour les transits"""
        chart = QChart()
        chart.setTitle("Transits Actifs")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Série de données pour les transits
        series = QScatterSeries()
        series.setName("Transits")
        series.setMarkerSize(10)
        series.setColor(QColor("#4fbdba"))
        
        # Données d'exemple
        for i in range(10):
            series.append(i, i * 2 + 5)
        
        chart.addSeries(series)
        chart.createDefaultAxes()
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view
    
    # Slots pour les actions
    @Slot()
    def switch_tab(self, tab_name: str):
        """Change d'onglet selon le nom"""
        tab_indices = {
            "natal": 0,
            "transits": 1,
            "compatibility": 2,
            "ephemeris": 3,
            "settings": 4
        }
        
        if tab_name in tab_indices:
            self.tab_widget.setCurrentIndex(tab_indices[tab_name])
    
    @Slot()
    def calculate_natal_chart(self):
        """Calcule le thème natal"""
        try:
            # Récupérer les données du formulaire
            birth_data = self.birth_form.get_data()
            if not birth_data:
                return
            
            # Afficher la barre de progression
            progress = QProgressDialog("Calcul du thème natal...", "Annuler", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setAutoClose(True)
            progress.show()
            
            # Simuler la progression
            for i in range(0, 101, 20):
                progress.setValue(i)
                QApplication.processEvents()
            
            # Calculer le thème
            self.current_chart = self.calculator.calculate_natal_chart(
                birth_data['date'],
                birth_data['latitude'],
                birth_data['longitude'],
                birth_data['timezone']
            )
            
            progress.setValue(100)
            
            # Afficher les résultats
            self.display_natal_results(self.current_chart)
            
            # Ajouter à l'historique
            self.charts_history.append(self.current_chart)
            
            self.statusBar().showMessage(f"Thème natal calculé pour {birth_data['date'].strftime('%d/%m/%Y %H:%M')}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du calcul : {str(e)}")
            self.statusBar().showMessage("Erreur lors du calcul")
    
    @Slot()
    def calculate_transits(self):
        """Calcule les transits"""
        if not self.current_chart:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord calculer un thème natal")
            return
        
        # Récupérer les données de transit
        transit_data = self.transit_form.get_data()
        if not transit_data:
            return
        
        try:
            transits = self.calculator.calculate_transits(self.current_chart, transit_data['date'])
            
            # Afficher les résultats
            self.display_transits_results(transits)
            
            self.statusBar().showMessage(f"Transits calculés pour {transit_data['date'].strftime('%d/%m/%Y')}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du calcul des transits : {str(e)}")
    
    @Slot()
    def calculate_compatibility(self):
        """Calcule la compatibilité"""
        # Récupérer les données des deux formulaires
        data1 = self.compatibility_form1.get_data()
        data2 = self.compatibility_form2.get_data()
        
        if not data1 or not data2:
            return
        
        try:
            # Calculer les deux thèmes
            chart1 = self.calculator.calculate_natal_chart(
                data1['date'], data1['latitude'], data1['longitude'], data1['timezone']
            )
            chart2 = self.calculator.calculate_natal_chart(
                data2['date'], data2['latitude'], data2['longitude'], data2['timezone']
            )
            
            # Calculer la compatibilité
            compatibility = self.calculator.calculate_compatibility(chart1, chart2)
            
            # Afficher les résultats
            self.display_compatibility_results(compatibility)
            
            self.statusBar().showMessage("Compatibilité calculée")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du calcul de compatibilité : {str(e)}")
    
    @Slot()
    def calculate_ephemeris(self):
        """Calcule les éphémérides"""
        try:
            date = self.ephemeris_date.date().toPython()
            duration_text = self.ephemeris_duration.currentText()
            
            # Calculer la période
            if duration_text == "1 jour":
                days = 1
            elif duration_text == "1 semaine":
                days = 7
            elif duration_text == "1 mois":
                days = 30
            else:
                days = 90
            
            # Générer les éphémérides
            ephemeris_data = []
            current_date = date
            
            for day in range(days):
                jd = self._datetime_to_julian(current_date, 'UTC')
                positions = self.calculator.ephemeris.calculate_all_planets(jd)
                
                row_data = {
                    'date': current_date.strftime('%d/%m/%Y'),
                    'positions': positions
                }
                ephemeris_data.append(row_data)
                current_date = self.add_days(current_date, 1)
            
            # Afficher dans la table
            self.display_ephemeris_results(ephemeris_data)
            
            self.statusBar().showMessage(f"Éphémérides calculées pour {days} jours")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du calcul des éphémérides : {str(e)}")
    
    def display_natal_results(self, chart: Dict):
        """Affiche les résultats du thème natal"""
        # Mettre à jour la carte
        self.chart_widget.set_chart(chart)
        
        # Mettre à jour la table des positions
        self.update_positions_table(chart['planet_positions'], chart['planet_houses'])
        
        # Mettre à jour la table des aspects
        self.update_aspects_table(chart['aspects'])
        
        # Mettre à jour le graphique des éléments
        self.update_element_chart(chart['element_counts'])
    
    def display_transits_results(self, transits: Dict):
        """Affiche les résultats des transits"""
        # Afficher dans la liste de texte
        transit_text = ""
        for transit in transits['transit_aspects'][:10]:  # Top 10
            transit_text += f"{transit['transit_planet']} {transit['aspect']} {transit['natal_planet']} (Orb: {transit['orb']:.1f}°)\n"
            transit_text += f"  → {transit['interpretation']}\n\n"
        
        self.transits_list.setText(transit_text)
    
    def display_compatibility_results(self, compatibility: Dict):
        """Affiche les résultats de compatibilité"""
        # Score
        self.compatibility_score_label.setText(f"{compatibility['compatibility_percentage']:.0f}%")
        
        # Table des aspects
        self.synastry_table.setRowCount(len(compatibility['synastry_aspects']))
        
        for i, aspect in enumerate(compatibility['synastry_aspects'][:10]):  # Top 10
            self.synastry_table.setItem(i, 0, QTableWidgetItem(f"{aspect['planet1']} - {aspect['planet2']}"))
            self.synastry_table.setItem(i, 1, QTableWidgetItem(aspect['aspect']))
            self.synastry_table.setItem(i, 2, QTableWidgetItem(f"{aspect['orb']:.1f}°"))
            self.synastry_table.setItem(i, 3, QTableWidgetItem(str(aspect['score'])))
    
    def display_ephemeris_results(self, ephemeris_data: List[Dict]):
        """Affiche les résultats des éphémérides"""
        self.ephemeris_table.setRowCount(len(ephemeris_data))
        
        for i, day_data in enumerate(ephemeris_data):
            self.ephemeris_table.setItem(i, 0, QTableWidgetItem(day_data['date']))
            
            positions = day_data['positions']
            planet_names = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturne']
            
            for j, planet in enumerate(planet_names):
                if planet in positions:
                    longitude = positions[planet]['longitude']
                    sign_index = int(longitude // 30)
                    sign = ZODIAC_SIGNS[sign_index]
                    deg = int(longitude % 30)
                    
                    self.ephemeris_table.setItem(i, j+1, QTableWidgetItem(f"{sign} {deg}°"))
    
    def update_positions_table(self, positions: Dict, planet_houses: Dict):
        """Met à jour la table des positions planétaires"""
        self.positions_table.setRowCount(len(positions))
        
        for i, (planet, data) in enumerate(positions.items()):
            # Planète
            self.positions_table.setItem(i, 0, QTableWidgetItem(planet))
            
            # Signe
            sign_index = int(data['longitude'] // 30)
            sign = ZODIAC_SIGNS[sign_index]
            self.positions_table.setItem(i, 1, QTableWidgetItem(f"{ZODIAC_SYMBOLS[sign_index]} {sign}"))
            
            # Degré
            deg = int(data['longitude'] % 30)
            minute = int((data['longitude'] % 1) * 60)
            self.positions_table.setItem(i, 2, QTableWidgetItem(f"{deg}°{minute:02d}'"))
            
            # Maison
            house = planet_houses[planet]
            self.positions_table.setItem(i, 3, QTableWidgetItem(str(house)))
    
    def update_aspects_table(self, aspects: List[Dict]):
        """Met à jour la table des aspects"""
        self.aspects_table.setRowCount(min(10, len(aspects)))  # Top 10
        
        for i, aspect in enumerate(aspects[:10]):
            # Planètes
            planets_text = f"{aspect['planet1']} - {aspect['planet2']}"
            self.aspects_table.setItem(i, 0, QTableWidgetItem(planets_text))
            
            # Aspect
            self.aspects_table.setItem(i, 1, QTableWidgetItem(aspect['aspect']))
            
            # Orb
            self.aspects_table.setItem(i, 2, QTableWidgetItem(f"{aspect['orb']:.1f}°"))
            
            # Type
            self.aspects_table.setItem(i, 3, QTableWidgetItem(aspect['type']))
            
            # Status (applying/separating)
            status = "⏳" if aspect.get('applying', False) else "↗"
            self.aspects_table.setItem(i, 4, QTableWidgetItem(status))
    
    def update_element_chart(self, element_counts: Dict[str, int]):
        """Met à jour le graphique des éléments"""
        # Créer une nouvelle série avec les vraies données
        chart = self.element_chart.chart()
        chart.removeAllSeries()
        
        series = QPieSeries()
        total = sum(element_counts.values())
        
        if total > 0:
            for element, count in element_counts.items():
                percentage = (count / total) * 100
                series.append(f"{element} ({count})", count)
        
        # Couleurs des éléments
        colors = ["#FF6B6B", "#8B4513", "#87CEEB", "#4169E1"]
        for i, slice in enumerate(series.slices()):
            slice.setBrush(QColor(colors[i]))
            slice.setLabelVisible(True)
            slice.setLabelFormat("{label}: {percentage:.1f}%")
        
        chart.addSeries(series)
    
    def add_days(self, date: datetime, days: int) -> datetime:
        """Ajoute des jours à une date"""
        from datetime import timedelta
        return date + timedelta(days=days)
    
    # Autres méthodes
    def quick_calculation(self):
        """Calcule le thème du moment présent"""
        now = datetime.now()
        
        # Utiliser Paris comme lieu par défaut
        self.birth_form.set_date_time(now)
        self.birth_form.set_location("Paris, France", 48.8566, 2.3522, "Europe/Paris")
        
        self.calculate_natal_chart()
    
    def new_chart(self):
        """Nouveau thème"""
        self.current_chart = None
        self.birth_form.clear()
        self.statusBar().showMessage("Nouveau thème - Entrez les données de naissance")
    
    def open_chart(self):
        """Ouvrir un thème sauvegardé"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir un thème", "", "Fichiers JSON (*.json)")
        
        if file_name:
            try:
                import json
                with open(file_name, 'r', encoding='utf-8') as f:
                    chart_data = json.load(f)
                
                # Restaurer le thème
                self.restore_chart(chart_data)
                self.statusBar().showMessage(f"Thème ouvert : {file_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ouverture : {str(e)}")
    
    def save_chart(self):
        """Sauvegarder le thème actuel"""
        if not self.current_chart:
            QMessageBox.warning(self, "Attention", "Aucun thème à sauvegarder")
            return
        
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder le thème", "", "Fichiers JSON (*.json)")
        
        if file_name:
            try:
                import json
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(self.current_chart, f, indent=2, default=str)
                
                self.statusBar().showMessage(f"Thème sauvegardé : {file_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde : {str(e)}")
    
    def export_chart(self):
        """Exporter le thème"""
        if not self.current_chart:
            QMessageBox.warning(self, "Attention", "Aucun thème à exporter")
            return
        
        dialog = ExportDialog(self.current_chart, self)
        dialog.exec()
    
    def open_settings(self):
        """Ouvrir les paramètres"""
        dialog = SettingsDialog(self.calculator.current_config, self)
        if dialog.exec() == QDialog.Accepted:
            self.calculator.current_config = dialog.get_config()
            self.statusBar().showMessage("Paramètres mis à jour")
    
    def open_atlas(self):
        """Ouvrir l'atlas des villes"""
        # À implémenter
        QMessageBox.information(self, "Info", "Fonction atlas en développement")
    
    def show_about(self):
        """Afficher la boîte À propos"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def show_help(self):
        """Afficher l'aide"""
        QMessageBox.information(self, "Aide", 
            "Astrolog Python - Calculateur de thèmes nataux\n\n"
            "1. Entrez les données de naissance\n"
            "2. Cliquez sur 'Calculer le thème'\n"
            "3. Explorez les résultats dans les différents onglets\n\n"
            "Pour plus d'informations, visitez notre site web.")
    
    def on_tab_changed(self, index):
        """Appelé quand l'onglet change"""
        tab_names = ["natal", "transits", "compatibility", "ephemeris"]
        if index < len(tab_names):
            # Mettre à jour le bouton de navigation actif
            for name, btn in self.nav_buttons.items():
                btn.setStyleSheet("")
            
            if tab_names[index] in self.nav_buttons:
                self.nav_buttons[tab_names[index]].setStyleSheet(
                    "background-color: #4fbdba; color: #1a1a2e;"
                )
    
    def restore_chart(self, chart_data: Dict):
        """Restaure un thème depuis des données sauvegardées"""
        self.current_chart = chart_data
        self.display_natal_results(chart_data)
    
    def closeEvent(self, event):
        """Gestion de la fermeture de l'application"""
        reply = QMessageBox.question(
            self, "Quitter", "Voulez-vous vraiment quitter Astrolog Python?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """Fonction principale"""
    app = QApplication(sys.argv)
    
    # Définir le style de l'application
    app.setApplicationName("Astrolog Python")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("AstrologPython")
    
    # Créer et afficher la fenêtre principale
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
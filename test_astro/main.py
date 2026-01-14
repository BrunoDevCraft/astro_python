#!/usr/bin/env python3
"""
Astrolog Python - Version moderne du célèbre logiciel d'astrologie
Point d'entrée principal de l'application
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import main

if __name__ == "__main__":
    # Vérifier les dépendances
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCharts import QChartView
    except ImportError as e:
        print("❌ Erreur : PySide6 n'est pas installé.")
        print("Installation : pip install pyside6")
        sys.exit(1)
    
    try:
        import pytz
    except ImportError:
        print("❌ Erreur : pytz n'est pas installé.")
        print("Installation : pip install pytz")
        sys.exit(1)
    
    # Lancer l'application
    print("🌟 Démarrage d'Astrolog Python...")
    main()
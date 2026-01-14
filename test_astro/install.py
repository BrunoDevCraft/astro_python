#!/usr/bin/env python3
"""
Script d'installation automatique d'Astrolog Python
Installe toutes les dépendances et configure l'application
"""

import os
import sys
import subprocess
import platform
import json
import shutil
import urllib.request
import zipfile
import tarfile
from pathlib import Path
from typing import List, Dict, Optional
import argparse


class Colors:
    """Codes couleurs pour l'affichage"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class AstrologInstaller:
    """Installateur principal d'Astrolog Python"""
    
    def __init__(self, verbose: bool = False, dev_mode: bool = False):
        self.verbose = verbose
        self.dev_mode = dev_mode
        self.platform = platform.system()
        self.python_version = sys.version_info
        
        # Chemins
        self.root_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.root_dir / "venv"
        self.data_dir = self.root_dir / "data"
        self.config_file = self.root_dir / "config.json"
        
        # Dépendances
        self.core_dependencies = [
            "PySide6>=6.5.0",
            "PySide6-Addons>=6.5.0",
            "pytz>=2023.3",
            "python-dateutil>=2.8.2"
        ]
        
        self.optional_dependencies = [
            "reportlab>=4.0.0",      # Pour PDF
            "svgwrite>=1.4.3",       # Pour SVG
            "swisseph>=2.10.3"       # Pour éphémérides précises
        ]
        
        self.dev_dependencies = [
            "pytest>=7.4.0",
            "pytest-qt>=4.2.0", 
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0"
        ]
    
    def print_header(self):
        """Affiche l'en-tête de l'installation"""
        header = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                      ✦ ASTROLOG PYTHON ✦                    ║
║                                                              ║
║  Calculateur de thèmes nataux et d'astrologie moderne       ║
║  Version 1.0.0 - Installation Automatique                   ║
╚══════════════════════════════════════════════════════════════╝
{Colors.RESET}
        """
        print(header)
    
    def print_step(self, step: str, status: str = "INFO"):
        """Affiche une étape avec couleur"""
        color_map = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "STEP": Colors.MAGENTA
        }
        
        color = color_map.get(status, Colors.WHITE)
        print(f"{color}{Colors.BOLD}[{status}]{Colors.RESET} {step}")
    
    def check_python_version(self) -> bool:
        """Vérifie la version de Python"""
        self.print_step("Vérification de la version Python...", "STEP")
        
        if self.python_version < (3, 8):
            self.print_step(f"Python {self.python_version.major}.{self.python_version.minor} "
                          f"détecté - Version minimale requise : 3.8", "ERROR")
            return False
        
        self.print_step(f"Python {self.python_version.major}.{self.python_version.minor} "
                       f"✓ - Version compatible", "SUCCESS")
        return True
    
    def check_system_requirements(self) -> bool:
        """Vérifie les prérequis système"""
        self.print_step("Vérification des prérequis système...", "STEP")
        
        # Vérifier l'espace disque
        try:
            total_space = shutil.disk_usage(self.root_dir).total
            free_space = shutil.disk_usage(self.root_dir).free
            
            # Besoin d'au moins 500MB d'espace libre
            required_space = 500 * 1024 * 1024  # 500MB en bytes
            
            if free_space < required_space:
                self.print_step(f"Espace disque insuffisant : "
                              f"{free_space / (1024**3):.1f}GB disponibles, "
                              f"500MB requis", "ERROR")
                return False
            
            self.print_step(f"Espace disque disponible : "
                           f"{free_space / (1024**3):.1f}GB ✓", "SUCCESS")
            
        except Exception as e:
            self.print_step(f"Impossible de vérifier l'espace disque : {e}", "WARNING")
        
        # Vérifier les bibliothèques système
        if self.platform == "Linux":
            self._check_linux_dependencies()
        elif self.platform == "Darwin":  # macOS
            self._check_macos_dependencies()
        elif self.platform == "Windows":
            self._check_windows_dependencies()
        
        return True
    
    def _check_linux_dependencies(self):
        """Vérifie les dépendances Linux"""
        required_packages = ['libgl1-mesa-glx', 'libglib2.0-0']
        
        for package in required_packages:
            try:
                result = subprocess.run(['dpkg', '-l', package], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.print_step(f"Package système manquant : {package}", "WARNING")
            except FileNotFoundError:
                # dpkg n'est pas disponible (pas une distribution Debian)
                pass
    
    def _check_macos_dependencies(self):
        """Vérifie les dépendances macOS"""
        # Vérifier si Xcode Command Line Tools est installé
        try:
            result = subprocess.run(['xcode-select', '-p'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.print_step("Xcode Command Line Tools ✓", "SUCCESS")
            else:
                self.print_step("Xcode Command Line Tools non installé", "WARNING")
        except FileNotFoundError:
            pass
    
    def _check_windows_dependencies(self):
        """Vérifie les dépendances Windows"""
        # Vérifier la version de Windows
        version = platform.version()
        self.print_step(f"Windows {version} détecté", "INFO")
        
        # Vérifier Visual C++ Redistributables
        try:
            import winreg
            # Vérifier dans le registre
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64")
            winreg.CloseKey(key)
            self.print_step("Visual C++ Redistributables ✓", "SUCCESS")
        except:
            self.print_step("Visual C++ Redistributables - À vérifier", "WARNING")
    
    def create_virtual_environment(self) -> bool:
        """Crée l'environnement virtuel Python"""
        self.print_step("Création de l'environnement virtuel...", "STEP")
        
        try:
            if self.venv_dir.exists():
                self.print_step("Suppression de l'ancien environnement virtuel...", "INFO")
                shutil.rmtree(self.venv_dir)
            
            # Créer le virtual env
            import venv
            builder = venv.EnvBuilder(system_site_packages=False,
                                    clear=True,
                                    with_pip=True)
            builder.create(self.venv_dir)
            
            self.print_step("Environnement virtuel créé ✓", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_step(f"Erreur lors de la création du venv : {e}", "ERROR")
            return False
    
    def get_pip_path(self) -> Path:
        """Retourne le chemin de pip dans le venv"""
        if self.platform == "Windows":
            return self.venv_dir / "Scripts" / "pip.exe"
        else:
            return self.venv_dir / "bin" / "pip"
    
    def get_python_path(self) -> Path:
        """Retourne le chemin de Python dans le venv"""
        if self.platform == "Windows":
            return self.venv_dir / "Scripts" / "python.exe"
        else:
            return self.venv_dir / "bin" / "python"
    
    def install_dependencies(self, dependencies: List[str], 
                           description: str = "dépendances") -> bool:
        """Installe une liste de dépendances"""
        self.print_step(f"Installation des {description}...", "STEP")
        
        pip_path = self.get_pip_path()
        
        # Mettre à jour pip d'abord
        try:
            subprocess.run([
                str(pip_path), "install", "--upgrade", "pip"
            ], check=True, capture_output=not self.verbose)
        except subprocess.CalledProcessError:
            self.print_step("Impossible de mettre à jour pip", "WARNING")
        
        # Installer les dépendances par groupes
        for i in range(0, len(dependencies), 3):  # 3 par 3 pour éviter les timeouts
            group = dependencies[i:i+3]
            group_str = ", ".join(group)
            
            try:
                self.print_step(f"Installation de : {group_str}", "INFO")
                
                cmd = [str(pip_path), "install"] + group
                if not self.verbose:
                    cmd.append("-q")  # mode silencieux
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.print_step(f"✓ {group_str}", "SUCCESS")
                else:
                    self.print_step(f"✗ {group_str} - {result.stderr}", "ERROR")
                    return False
                    
            except Exception as e:
                self.print_step(f"Erreur lors de l'installation de {group_str} : {e}", "ERROR")
                return False
        
        return True
    
    def download_ephemeris_files(self) -> bool:
        """Télécharge les fichiers d'éphémérides Swiss Ephemeris"""
        self.print_step("Téléchargement des fichiers d'éphémérides...", "STEP")
        
        ephe_dir = self.data_dir / "ephe"
        ephe_dir.mkdir(exist_ok=True)
        
        # URLs des fichiers d'éphémérides (période moderne)
        ephemeris_files = {
            "sepl_18.se1": "https://www.astro.com/ftp/swisseph/planets/sepl_18.se1",
            "semo_18.se1": "https://www.astro.com/ftp/swisseph/moon/semo_18.se1",
            "seas_18.se1": "https://www.astro.com/ftp/swisseph/asteroids/seas_18.se1"
        }
        
        for filename, url in ephemeris_files.items():
            file_path = ephe_dir / filename
            
            if file_path.exists():
                self.print_step(f"{filename} déjà présent ✓", "SUCCESS")
                continue
            
            try:
                self.print_step(f"Téléchargement de {filename}...", "INFO")
                
                urllib.request.urlretrieve(
                    url, 
                    file_path,
                    reporthook=self._download_progress_hook
                )
                
                self.print_step(f"✓ {filename} téléchargé", "SUCCESS")
                
            except Exception as e:
                self.print_step(f"Erreur lors du téléchargement de {filename} : {e}", "WARNING")
                # Continuer sans les éphémérides
    
    def _download_progress_hook(self, block_num, block_size, total_size):
        """Affiche la progression du téléchargement"""
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(downloaded / total_size * 100, 100)
            if block_num % 10 == 0:  # Afficher tous les 10 blocs
                print(f"\rProgression : {percent:.1f}%", end='', flush=True)
    
    def create_config_file(self) -> bool:
        """Crée le fichier de configuration"""
        self.print_step("Création du fichier de configuration...", "STEP")
        
        config = {
            "version": "1.0.0",
            "installation_date": datetime.now().isoformat(),
            "platform": self.platform,
            "python_version": f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}",
            "paths": {
                "root_dir": str(self.root_dir),
                "data_dir": str(self.data_dir),
                "config_file": str(self.config_file)
            },
            "settings": {
                "default_house_system": "P",  # Placidus
                "default_timezone": "Europe/Paris",
                "use_ephemeris": True,
                "language": "fr",
                "theme": "dark",
                "animations": True
            },
            "dependencies": {
                "core": self.core_dependencies,
                "optional": self.optional_dependencies,
                "dev": self.dev_dependencies if self.dev_mode else []
            }
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.print_step("Fichier de configuration créé ✓", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_step(f"Erreur lors de la création du config : {e}", "ERROR")
            return False
    
    def create_desktop_entry(self) -> bool:
        """Crée une entrée bureau (Linux/macOS) ou raccourci (Windows)"""
        self.print_step("Création du raccourci bureau...", "STEP")
        
        try:
            if self.platform == "Linux":
                return self._create_linux_desktop_entry()
            elif self.platform == "Darwin":  # macOS
                return self._create_macos_app_bundle()
            elif self.platform == "Windows":
                return self._create_windows_shortcut()
            
        except Exception as e:
            self.print_step(f"Erreur lors de la création du raccourci : {e}", "WARNING")
            return False
    
    def _create_linux_desktop_entry(self) -> bool:
        """Crée une entrée .desktop pour Linux"""
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = desktop_dir / "astrolog-python.desktop"
        
        content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Astrolog Python
Comment=Calculateur de thèmes nataux et d'astrologie moderne
Exec={self.get_python_path()} {self.root_dir / "main.py"}
Icon={self.root_dir / "assets" / "icon.png"}
Terminal=false
Categories=Education;Science;
Keywords=astrology;horoscope;chart;
StartupNotify=true
"""
        
        with open(desktop_file, 'w') as f:
            f.write(content)
        
        # Rendre exécutable
        desktop_file.chmod(0o755)
        
        self.print_step("Raccourci Linux créé ✓", "SUCCESS")
        return True
    
    def _create_macos_app_bundle(self) -> bool:
        """Crée un bundle d'application pour macOS"""
        app_dir = Path.home() / "Applications" / "AstrologPython.app"
        app_dir.mkdir(parents=True, exist_ok=True)
        
        contents_dir = app_dir / "Contents"
        contents_dir.mkdir(exist_ok=True)
        
        macos_dir = contents_dir / "MacOS"
        macos_dir.mkdir(exist_ok=True)
        
        resources_dir = contents_dir / "Resources"
        resources_dir.mkdir(exist_ok=True)
        
        # Info.plist
        info_plist = contents_dir / "Info.plist"
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Astrolog Python</string>
    <key>CFBundleDisplayName</key>
    <string>Astrolog Python</string>
    <key>CFBundleIdentifier</key>
    <string>com.astrologpython.app</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleExecutable</key>
    <string>AstrologPython</string>
</dict>
</plist>"""
        
        with open(info_plist, 'w') as f:
            f.write(plist_content)
        
        # Script de lancement
        launcher_script = macos_dir / "AstrologPython"
        launcher_content = f"""#!/bin/bash
cd "{self.root_dir}"
source venv/bin/activate
python main.py
"""
        
        with open(launcher_script, 'w') as f:
            f.write(launcher_content)
        
        launcher_script.chmod(0o755)
        
        self.print_step("Bundle macOS créé ✓", "SUCCESS")
        return True
    
    def _create_windows_shortcut(self) -> bool:
        """Crée un raccourci Windows"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = Path(desktop) / "Astrolog Python.lnk"
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(self.get_python_path())
            shortcut.WorkingDirectory = str(self.root_dir)
            shortcut.Arguments = str(self.root_dir / "main.py")
            shortcut.IconLocation = str(self.root_dir / "assets" / "icon.ico")
            shortcut.save()
            
            self.print_step("Raccourci Windows créé ✓", "SUCCESS")
            return True
            
        except ImportError:
            self.print_step("Modules Windows non disponibles", "WARNING")
            return False
    
    def create_launcher_script(self) -> bool:
        """Crée des scripts de lancement multi-plateforme"""
        self.print_step("Création des scripts de lancement...", "STEP")
        
        # Script Bash (Linux/macOS)
        bash_script = self.root_dir / "astrolog.sh"
        bash_content = f"""#!/bin/bash
# Astrolog Python Launcher

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
cd "$SCRIPT_DIR"

# Activer l'environnement virtuel
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Environnement virtuel non trouvé. Lancez install.py d'abord."
    exit 1
fi

# Lancer l'application
echo "🌟 Démarrage d'Astrolog Python..."
python main.py "$@"

# Désactiver l'environnement virtuel
deactivate
"""
        
        with open(bash_script, 'w') as f:
            f.write(bash_content)
        
        bash_script.chmod(0o755)
        
        # Script Batch (Windows)
        batch_script = self.root_dir / "astrolog.bat"
        batch_content = f"""@echo off
REM Astrolog Python Launcher

cd /d "%~dp0"

REM Activer l'environnement virtuel
if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
) else (
    echo ❌ Environnement virtuel non trouvé. Lancez install.py d'abord.
    pause
    exit /b 1
)

REM Lancer l'application
echo 🌟 Démarrage d'Astrolog Python...
python main.py %*

REM Désactiver l'environnement virtuel
deactivate

pause
"""
        
        with open(batch_script, 'w') as f:
            f.write(batch_content)
        
        self.print_step("Scripts de lancement créés ✓", "SUCCESS")
        return True
    
    def run_tests(self) -> bool:
        """Exécute les tests de validation"""
        self.print_step("Exécution des tests de validation...", "STEP")
        
        try:
            # Importer et exécuter les tests
            from tests.validation import AstrologValidationTests
            import unittest
            
            # Lancer les tests basiques
            suite = unittest.TestLoader().loadTestsFromTestCase(AstrologValidationTests)
            runner = unittest.TextTestRunner(verbosity=0 if not self.verbose else 2)
            result = runner.run(suite)
            
            if result.wasSuccessful():
                self.print_step("Tous les tests passés ✓", "SUCCESS")
                return True
            else:
                self.print_step(f"{len(result.failures)} tests ont échoué", "WARNING")
                return False
                
        except Exception as e:
            self.print_step(f"Erreur lors des tests : {e}", "WARNING")
            return False
    
    def create_uninstaller(self) -> bool:
        """Crée un script de désinstallation"""
        self.print_step("Création du script de désinstallation...", "STEP")
        
        uninstall_script = self.root_dir / "uninstall.py"
        
        content = f'''#!/usr/bin/env python3
"""
Script de désinstallation d'Astrolog Python
"""

import shutil
import sys
import os
from pathlib import Path

def uninstall():
    """Désinstalle complètement Astrolog Python"""
    print("🗑️  Désinstallation d'Astrolog Python...")
    
    root_dir = Path(__file__).parent.absolute()
    
    # Supprimer l'environnement virtuel
    venv_dir = root_dir / "venv"
    if venv_dir.exists():
        shutil.rmtree(venv_dir)
        print("✓ Environnement virtuel supprimé")
    
    # Supprimer les fichiers de configuration
    config_files = [
        "config.json",
        "data/ephe/*.se1",
        "data/cities.db"
    ]
    
    for pattern in config_files:
        for file_path in root_dir.glob(pattern):
            if file_path.exists():
                file_path.unlink()
                print(f"✓ {file_path.name} supprimé")
    
    # Supprimer les raccourcis (plateforme spécifique)
    if sys.platform == "linux":
        desktop_file = Path.home() / ".local" / "share" / "applications" / "astrolog-python.desktop"
        if desktop_file.exists():
            desktop_file.unlink()
            print("✓ Raccourci Linux supprimé")
    
    elif sys.platform == "darwin":
        app_bundle = Path.home() / "Applications" / "AstrologPython.app"
        if app_bundle.exists():
            shutil.rmtree(app_bundle)
            print("✓ Bundle macOS supprimé")
    
    elif sys.platform == "win32":
        try:
            import winshell
            desktop = Path(winshell.desktop())
            shortcut = desktop / "Astrolog Python.lnk"
            if shortcut.exists():
                shortcut.unlink()
                print("✓ Raccourci Windows supprimé")
        except:
            pass
    
    print("\\n✅ Désinstallation terminée!")
    print("Les scripts source sont conservés. Supprimez le dossier manuellement si nécessaire.")

if __name__ == "__main__":
    uninstall()
'''
        
        with open(uninstall_script, 'w') as f:
            f.write(content)
        
        uninstall_script.chmod(0o755)
        
        self.print_step("Script de désinstallation créé ✓", "SUCCESS")
        return True
    
    def print_final_report(self):
        """Affiche le rapport final d'installation"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    INSTALLATION TERMINÉE                     ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}\n")
        
        print(f"{Colors.GREEN}✅ Astrolog Python a été installé avec succès !{Colors.RESET}\n")
        
        print("📋 Résumé de l'installation :")
        print(f"  • Répertoire d'installation : {self.root_dir}")
        print(f"  • Environnement virtuel : {self.venv_dir}")
        print(f"  • Configuration : {self.config_file}")
        
        print(f"\n{Colors.CYAN}🚀 Pour lancer l'application :{Colors.RESET}")
        
        if self.platform == "Windows":
            print("  astrolog.bat")
        else:
            print("  ./astrolog.sh")
            print("  ou")
            print(f"  {self.get_python_path()} main.py")
        
        print(f"\n{Colors.YELLOW}📖 Documentation et support :{Colors.RESET}")
        print("  • Lisez le fichier README.md pour plus d'informations")
        print("  • Exécutez les tests : python -m pytest tests/")
        print("  • Pour désinstaller : python uninstall.py")
        
        print(f"\n{Colors.BLUE}🌟 Bonne exploration astrologique !{Colors.RESET}\n")
    
    def install(self) -> bool:
        """Procédure principale d'installation"""
        self.print_header()
        
        print(f"{Colors.YELLOW}Cette installation va :{Colors.RESET}")
        print("  • Créer un environnement virtuel Python")
        print("  • Installer toutes les dépendances nécessaires")
        print("  • Télécharger les fichiers d'éphémérides")
        print("  • Créer des raccourcis et scripts de lancement")
        print("  • Exécuter les tests de validation")
        
        print(f"\n{Colors.CYAN}Commencer l'installation ? [O/N] : {Colors.RESET}", end='')
        response = input().strip().lower()
        
        if response not in ['o', 'oui', 'y', 'yes']:
            print("Installation annulée.")
            return False
        
        print()
        
        # Étape 1 : Vérifications
        if not self.check_python_version():
            return False
        
        if not self.check_system_requirements():
            return False
        
        # Étape 2 : Environnement virtuel
        if not self.create_virtual_environment():
            return False
        
        # Étape 3 : Dépendances de base
        if not self.install_dependencies(self.core_dependencies, "dépendances principales"):
            return False
        
        # Étape 4 : Dépendances optionnelles
        optional_success = self.install_dependencies(self.optional_dependencies, 
                                                   "dépendances optionnelles")
        
        # Étape 5 : Dépendances de développement (si mode dev)
        if self.dev_mode:
            self.install_dependencies(self.dev_dependencies, "dépendances de développement")
        
        # Étape 6 : Fichiers d'éphémérides
        self.download_ephemeris_files()
        
        # Étape 7 : Configuration
        if not self.create_config_file():
            return False
        
        # Étape 8 : Raccourcis et scripts
        self.create_desktop_entry()
        self.create_launcher_script()
        
        # Étape 9 : Tests
        self.run_tests()
        
        # Étape 10 : Désinstallateur
        self.create_uninstaller()
        
        # Rapport final
        self.print_final_report()
        
        return True


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Installateur d'Astrolog Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python install.py                    # Installation standard
  python install.py --dev             # Installation avec outils de développement
  python install.py --verbose         # Installation avec sortie détaillée
  python install.py --help            # Afficher cette aide
        """
    )
    
    parser.add_argument(
        "--dev", 
        action="store_true",
        help="Installer avec les outils de développement"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="Mode verbeux avec sortie détaillée"
    )
    
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Sauter l'exécution des tests"
    )
    
    args = parser.parse_args()
    
    # Créer et lancer l'installateur
    installer = AstrologInstaller(
        verbose=args.verbose,
        dev_mode=args.dev
    )
    
    try:
        success = installer.install()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Installation interrompue par l'utilisateur.{Colors.RESET}")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n\n{Colors.RED}Erreur fatale : {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
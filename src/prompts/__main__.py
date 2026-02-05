"""
Point d'entrée du module src.prompts.

Permet d'exécuter : python -m src.prompts
"""

from . import print_module_info, print_quick_guide

if __name__ == "__main__":
    print_module_info()
    print("\n")
    print_quick_guide()
    
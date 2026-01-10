"""
Module de calcul de statistiques simples.
"""

import math


def calculate_average(numbers):
    """
    Calcule la moyenne d'une liste de nombres.
    
    Args:
        numbers (list): Liste de nombres
        
    Returns:
        float: La moyenne, ou 0 si la liste est vide
    """
    if not numbers:
        return 0
    
    total = sum(numbers)
    count = len(numbers)
    average = total / count
    return average


def calculate_standard_deviation(numbers):
    """
    Calcule l'écart-type d'une liste de nombres.
    
    Args:
        numbers (list): Liste de nombres
        
    Returns:
        float: L'écart-type, ou 0 si la liste est vide
    """
    if not numbers:
        return 0
    
    avg = calculate_average(numbers)
    variance = sum((x - avg) ** 2 for x in numbers) / len(numbers)
    std_dev = math.sqrt(variance)
    return std_dev


def main():
    """Point d'entrée principal du programme."""
    data = [1, 2, 3, 4, 5]
    
    avg = calculate_average(data)
    std = calculate_standard_deviation(data)
    
    print(f"Données : {data}")
    print(f"Moyenne : {avg:.2f}")
    print(f"Écart-type : {std:.2f}")


if __name__ == "__main__":
    main()
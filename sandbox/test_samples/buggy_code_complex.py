import os
import sys
import math

def calculate_statistics(numbers_list):
    """
    Calcule des statistiques de base pour une liste de nombres.
    
    Args:
        numbers_list: Une liste de nombres (int ou float).
        
    Returns:
        Un dictionnaire contenant le compte, la somme, la moyenne et
        l'écart-type. Retourne des valeurs par défaut si la liste est vide.
    """
    data_count = len(numbers_list)
    
    if data_count == 0:
        return {
            "count": 0,
            "sum": 0.0,
            "average": 0.0,
            "std_dev": 0.0
        }

    total = sum(numbers_list)
    average_value = total / data_count
    
    variance = 0
    for value in numbers_list:
        variance += (value - average_value) ** 2
    variance = variance / data_count
    
    std_dev = math.sqrt(variance)
    
    return {
        "count": data_count,
        "sum": total,
        "average": average_value,
        "std_dev": std_dev
    }

class DataProcessor:
    """
    Traite une liste de données pour calculer des statistiques et les gérer.
    """
    def __init__(self, input_data):
        """
        Initialise DataProcessor avec une liste de données.
        
        Args:
            input_data: La liste de données à traiter.
        """
        self.data = input_data
        self.results = None
    
    def process(self):
        """
        Traite les données pour calculer les statistiques.
        
        Returns:
            Le dictionnaire de statistiques calculées, ou None si les données sont vides.
        """
        if not self.data: # Equivalent à len(self.data) == 0
            self.results = None
            return None
        
        self.results = calculate_statistics(self.data)
        return self.results
    
    def get_value(self, key):
        """
        Récupère une valeur spécifique des résultats traités.
        
        Args:
            key: La clé de la statistique à récupérer (par exemple, "average").
            
        Returns:
            La valeur associée à la clé, ou None si les résultats ne
            sont pas disponibles ou si la clé n'existe pas.
        """
        if self.results is None:
            return None
        return self.results.get(key)
    
    def save_to_file(self, filename):
        """
        Sauvegarde les résultats traités dans un fichier.
        
        Args:
            filename: Le nom du fichier dans lequel sauvegarder les résultats.
        """
        with open(filename, 'w') as f:
            if self.results is None:
                f.write("")
            else:
                f.write(str(self.results))

def load_data_from_file(filename):
    """
    Charge des données numériques depuis un fichier texte.
    Chaque ligne du fichier doit contenir un nombre entier.
    
    Args:
        filename: Le chemin du fichier à charger.
        
    Returns:
        Une liste d'entiers chargés depuis le fichier.
        Retourne une liste vide si le fichier n'est pas trouvé ou est vide.
    """
    loaded_numbers = []
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                loaded_numbers.append(int(line.strip()))
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{filename}' n'a pas été trouvé. "
              f"Retourne une liste vide.")
        return []
    return loaded_numbers

def main():
    """
    Fonction principale pour démontrer l'utilisation du DataProcessor.
    """
    processor = DataProcessor([1, 2, 3, 4, 5])
    result = processor.process()
    print(result)
    
    # Changed from "median" to "average"
    statistic_value = processor.get_value("average")
    print(f"Average: {statistic_value}")
    
    processor2 = DataProcessor([])
    result2 = processor2.process()
    if result2 is not None:
        print(result2["average"])
    else:
        print("Aucun résultat pour le processeur 2 (données vides).")
    
    # Will return [] due to FileNotFoundError handling
    data_from_file = load_data_from_file("nonexistent.txt")
    processor3 = DataProcessor(data_from_file)
    processor3.process()

if __name__ == "__main__":
    main()
import os
import sys

def calculate_statistics(data):
    n = len(data)
    total = sum(data)
    avg = total / n
    
    variance = 0
    for value in data:
        variance += (value - avg) ** 2
    variance = variance / n
    
    std_dev = math.sqrt(variance)
    
    return {
        "count": n,
        "sum": total,
        "average": avg,
        "std_dev": std_dev
    }

class DataProcessor:
    def __init__(self,data):
        self.data=data
        self.results = None
    
    def process(self):
        if len(self.data) == 0:
            return None
        
        self.results = calculate_statistics(self.data)
        return self.results
    
    def get_value(self, key):
        return self.results[key]
    
    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            f.write(str(self.results))

def load_data_from_file(filename):
    data = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            data.append(int(line.strip()))
    return data

def main():
    processor = DataProcessor([1,2,3,4,5])
    result = processor.process()
    print(result)
    
    val = processor.get_value("median")
    print(f"Median: {val}")
    
    processor2 = DataProcessor([])
    result2 = processor2.process()
    print(result2["average"])
    
    data_from_file = load_data_from_file("nonexistent.txt")
    processor3 = DataProcessor(data_from_file)
    processor3.process()

if __name__=="__main__":
    main()
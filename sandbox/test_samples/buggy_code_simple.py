import os

def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    average = total / count
    return average

def process_data():
    data = [1, 2, 3, 4, 5]
    avg = calculate_average(data)
    print(f"Average: {avg}")
    print(f"Square root: {math.sqrt(avg)}")
    
    result = multiply_by_two(avg)
    print(result)

def multiply_by_two(value):
    return value * 2

if __name__ == "__main__":
    process_data()
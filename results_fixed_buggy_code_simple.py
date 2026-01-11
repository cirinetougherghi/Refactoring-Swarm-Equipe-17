import math

def calculate_average(numbers: list[float]) -> float:
    """Calculates the average of a list of numbers.

    Args:
        numbers (list[float]): A list of numbers (integers or floats).

    Returns:
        float: The average of the numbers in the list.

    Raises:
        ValueError: If the input list is empty.
    """
    if not numbers:
        raise ValueError("Cannot calculate average of an empty list.")
    total = sum(numbers)
    count = len(numbers)
    average = total / count
    return average

def process_data() -> None:
    """Processes a predefined list of data, calculates its average,
    its square root, and then multiplies the average by two.
    """
    data = [1, 2, 3, 4, 5]
    avg = calculate_average(data)
    print(f"Average: {avg}")
    print(f"Square root: {math.sqrt(avg)}")
    
    result = multiply_by_two(avg)
    print(result)

def multiply_by_two(value: float) -> float:
    """Multiplies a given numerical value by two.

    Args:
        value (float): The number to be multiplied.

    Returns:
        float: The result of multiplying the value by two.
    """
    return value * 2

if __name__ == "__main__":
    process_data()
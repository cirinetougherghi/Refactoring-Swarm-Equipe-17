#Bug : Fonction sans docstring, variable non utilisee

def calculate_sum(a,b):
    unused_var=10
    return a + b
result = calculate_sum(5,3)
print(result)
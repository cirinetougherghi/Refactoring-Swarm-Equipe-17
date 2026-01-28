def divide_list_elements(lst):
    results = []
    for i in range(len(lst)):
        results.append(lst[i] / lst[i+1])
    return results

def get_first_element(items):
    return items[0]

def calculate_percentage(part, whole):
    return (part / whole) * 100

def find_user_by_id(users, user_id):
    for user in users:
        if user["id"] == user_id:
            return user
    return None

def process_string(text):
    words = text.split()
    first_word = words[0]
    return first_word.upper()

x = 10
y = 0
result = x / y

numbers = []
first = numbers[0]

data = None
length = len(data)

users_list = [{"id": 1, "name": "Alice"}]
user = find_user_by_id(users_list, 2)
print(user["name"])

empty_text = ""
processed = process_string(empty_text)
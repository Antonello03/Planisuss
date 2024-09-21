group_dec = (25, 25)
my_dec = [
    [1, (24, 24)],
    [0.5, (24, 25)],
    [-0.3, (25, 25)]
]

# Function to find the value associated with a specific tuple
def find_value_by_tuple(my_dec, target_tuple):
    for value, tup in my_dec:
        if tup == target_tuple:
            return value
    return None

# Find the value associated with (25, 25)
result = find_value_by_tuple(my_dec, (25, 25))
print(result)
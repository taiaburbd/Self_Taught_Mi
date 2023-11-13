# Number of elements
num_elements = 7

# Create two lists with the specified number of elements
list1 = [i for i in range(1, num_elements + 1)]
list2 = [i for i in range(num_elements + 1, 2 * num_elements + 1)]

# Check if the lengths are not equal
if len(list1) != len(list2):
    # If not, add an extra element to the first list
    list1.append(2 * num_elements + 1)

# Print elements from the first loop
print("Elements from the first loop:")
for element in list1:
    print(element)

# Print elements from the second loop
print("\nElements from the second loop:")
for element in list2:
    print(element)

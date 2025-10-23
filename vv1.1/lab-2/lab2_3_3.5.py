import sys
 
args = sys.argv[1:]
arr = []
for arg in args:
    num = int(arg)
    arr.append(num)

# 2. Вывести пары отрицательных чисел, стоящих рядом
print("Пары отрицательных чисел, стоящих рядом:")
for i in range(len(arr) - 1):
    if arr[i] < 0 and arr[i+1] < 0:
        print(f"({arr[i]}, {arr[i+1]})")
    
# 3. Удалить все одинаковые повторяющиеся числа
i = 0
while i < len(arr):
    j = i + 1
    while j < len(arr):
        if arr[i] == arr[j]:
            arr.pop(j) 
        else:
            j += 1 
    i += 1

# 4. Вывести в консоль полученный массив
print("Массив после удаления повторяющихся чисел:")
output = ""
for num in arr:
    output += str(num) + " "
print(output.strip())

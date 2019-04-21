
def count(filepath):
    total = 0
    file = open(filepath)
    for line in file.readlines():
        line = line.strip()
        for id in line.split():
            total += 1

    return total

print (count("output.txt"))

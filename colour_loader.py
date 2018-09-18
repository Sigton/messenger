
def load_colours():
    with open("RGB.txt", 'r') as infile:
        data = infile.read().split("\n")

    colours = [line.split(" ")[0] for line in data]
    return colours

# <h2 className="text-4xl font-bold mb-4" id={`home heading ${index}`}>Introduction {item}</h2>
with open("output_jsx.txt", "w") as out:
    with open("input_file.md") as f:
        lines = f.readlines()
        for line in lines:
            if line[0] == "#":
                pass

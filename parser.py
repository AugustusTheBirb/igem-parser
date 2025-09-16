# <h2 className="text-4xl font-bold mb-4" id={`home heading ${index}`}>Introduction {item}</h2>
# <h3 className="text-2xl font-bold mb-4" id={`home subheading ${index+1}`}>Subheading {item}</h3>
def parseBoldItalic(string):
    bold = False
    italic = False
    skip = False
    newString = ""
    for index in range(len(string)):
        if skip:
            skip = False
            continue
        if string[index:index+2] == "**" and not bold:
            bold=True
            skip=True
            newString += "<strong>"
        elif string[index:index+2] == "**" and bold:
            bold = False
            skip=True
            newString +="</strong>"
        elif string[index] == "*" and not italic: 
            italic=True
            newString += "<em>"
        elif string[index] == "*" and italic:
            italic = False
            newString +="</em>"
        if string[index] != "*":
            newString += string[index]
    return newString        

def parseReferences(string):
    newString = ""
    num = ""
    skip = False
    isNumber = False
    for i, letter in enumerate(string):
        if skip: 
            skip = False
            continue
            
        if string[i:i+2] == "\\[":
            print("weow")
            isNumber = True
            skip = True
            continue
        if string[i:i+2] == "\\]":
            isNumber = False
            scroll_link = (
            '<ScrollLink '
            'to={"reference-'
            f'{num}'
            '"} '
            'smooth={true} '
            'duration={500} '
            'offset={-20} '
            'className="cursor-pointer text-blue-500 hover:underline">'
            f'[{num}]'
            '</ScrollLink>'
            )
            newString += scroll_link
            skip = True
            continue
        if isNumber:
            num += letter
        if not isNumber:
            newString += letter
    return newString

def parseLinks(string):
    newString = "" 
    linkT = False
    linkR = False
    linkText = ""
    linkRoute = ""
    for i, letter in enumerate(string):
        if letter == "[" and string[i+1] not in  "1234567890":
            linkT = True
            continue
        if letter == "]" and linkT:
            linkT = False
            linkR = True
            continue
        if linkR and letter == "(":
            continue
        if linkR and letter == ")":
            linkR = False
            newString += f'<a className="text-blue-500 hover:underline cursor-pointer" href="{linkRoute}">{linkText}</a>'
            continue
        if linkR:
            linkRoute += letter
        if linkT:
            linkText += letter
        if not linkR and not linkT:
            newString += letter
    return parseBoldItalic(parseReferences(newString))

def isOrderedListItem(string):
    idx = 0
    breakFlag = False
    while idx < 1000:
        if string[idx] in "1234567890":
            idx += 1
        elif line[idx] == ".":
            break
        else:
            breakFlag = True
            break
    if breakFlag: return False, 0
    else: return True, idx

def isTableRow(string):
    return "|" in string.strip()

def parseTableRow(string, isHeader=False):
    cells = [cell.strip() for cell in string.split("|")[1:-1]]  # Remove empty first/last elements
    tag = "th" if isHeader else "td"
    className = "px-4 py-2 border border-gray-300 font-semibold bg-gray-50" if isHeader else "px-4 py-2 border border-gray-300"
    
    row_content = ""
    for cell in cells:
        row_content += f'<{tag} className="{className}">{parseLinks(cell)}</{tag}>'
    
    return f'<tr>{row_content}</tr>'

with open("output_jsx.txt", "w") as out:
    with open("input_file.md") as f:
        table_body_started = False
        headerIndex = 0
        subheaderIndex = 0
        ul = False
        ol = False
        table = False
        lines = f.readlines()
        ref = False
        refIdx = 1
        imageCount = 0
        skipNext = False
        for i, line in enumerate(lines):
            isOlItem, numberLength = isOrderedListItem(line)
            isTable = isTableRow(line)
            
            if skipNext: 
                skipNext = False
                continue

            if line.startswith("img(") and line.strip().endswith(")"):
                url = line[4:-2]  
                caption = lines[i + 1].strip()
                imageCount += 1
                skipNext = True
                jsx = f'<div className="my-4">\n'
                jsx += f'  <img src="{url}" alt="{caption}" className="h-100 w-auto mx-auto" />\n'
                jsx += f'  <p className="text-sm text-center mt-2"><b>Fig {imageCount}.</b> {caption}</p>\n'
                jsx += f'</div>\n'
                out.write(jsx)
                continue

            if line == "\n" : continue
            # Headers
            elif line[0] == "#":
                if line[0:2] == "# ":
                    if "References" in line:
                        ref = True
                    out.write(f'<h2 className="text-4xl font-bold mb-4" id="heading {headerIndex}">{line[2:-1].replace("*","")}</h2>\n')
                    headerIndex += 1
                elif line[0:3] == "## ":
                    out.write(f'<h3 className="text-2xl font-bold mb-4" id="subheading {subheaderIndex}">{line[3:-1].replace("*","")}</h3>\n')
                    subheaderIndex += 1
            # Table handling
            elif isTable and not table:
                # Start of table - write header
                table = True
                out.write('<div style=\{\{  overflowX: "auto", webkitOverflowScrolling: "touch",\}\}>\n')
                out.write('<table className="text-base min-w-full border-collapse border border-gray-300 my-4">\n<thead className="text-center" >\n')
                out.write(parseTableRow(line, isHeader=True) + '\n')
            elif isTable and table:
                # Check if this is the alignment row (contains :---- pattern)
                if line.strip().startswith('|') and ':' in line and '-' in line:
                    # Skip alignment row
                    continue
                else:
                    # This is a data row
                    if i > 0 and not table_body_started:
                        out.write('</thead>\n<tbody>\n')
                        table_body_started = True
                    elif 'table_body_started' not in locals():
                        table_body_started = False
                        
                    if table_body_started or (i > 0 and lines[i-1].strip().startswith('|') and ':' in lines[i-1] and '-' in lines[i-1]):
                        if not table_body_started:
                            out.write('</thead>\n<tbody>\n')
                            table_body_started = True
                        out.write(parseTableRow(line) + '\n')
                    
                    # Check if table ends
                    if i+1 == len(lines) or not isTableRow(lines[i+1]):
                        out.write('</tbody>\n</table>\n</div>\n')
                        table = False
                        if 'table_body_started' in locals():
                            del table_body_started
            # ul and ol
            # ul
            elif line[0] in "-*" and not ul:
                ul = True
                out.write('<ul className="text-base list-disc pl-12 space-y-2 py-2">\n')
                out.write(f'<li>{parseLinks(line[2:-1])}</li>\n')
            elif line[0] in "-*" and ul:
                out.write(f'<li>{parseLinks(line[2:-1])}</li>\n')
                if i+1 == len(lines) or lines[i+1][0] not in "-*":
                    out.write("</ul>\n")
                    ul = False
            # ol
            elif line[0:2] == "1." and not ol:
                ol = True
                out.write('<ol className="text-base list-decimal pl-12 space-y-2 py-2">\n')
                addition = ""
                if ref: 
                    addition = f' id="reference-{refIdx}"'
                    refIdx += 1
                out.write(f'<li{addition}>{parseLinks(line[numberLength+2:-1])}</li>\n')
            elif isOlItem and ol:
                addition = ""
                if ref: 
                    addition = f' id="reference-{refIdx}"'
                    refIdx += 1
                out.write(f'<li{addition}>{parseLinks(line[numberLength+2:-1])}</li>\n')
                if i+1 != len(lines): isOlItem, _ = isOrderedListItem(lines[i+1])
                if i+1 == len(lines) or not isOlItem:
                    out.write("</ol>\n")
                    ol = False
            else:
                out.write(f'<p className="py-2 text-base">{parseLinks(line[:-1])}</p>\n')
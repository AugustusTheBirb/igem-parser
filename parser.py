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
            newString += "<Strong>"
        elif string[index:index+2] == "**" and bold:
            bold = False
            skip=True
            newString +="</Strong>"
        elif string[index] == "*" and not italic:
            italic=True
            newString += "<Em>"
        elif string[index] == "*" and italic:
            italic = False
            newString +="</Em>"
        else:
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
            # Peek ahead to see if this is a numeric reference
            j = i + 2
            temp_num = ""
            while j < len(string) and string[j] in "0123456789":
                temp_num += string[j]
                j += 1
            # Only treat as reference if it's followed by \] and contains digits
            if j < len(string) and string[j:j+2] == "\\]" and temp_num:
                isNumber = True
                skip = True
                continue
            else:
                # Not a numeric reference, treat as escaped bracket
                skip = True
                newString += "["
                continue
        if string[i:i+2] == "\\]":
            if isNumber:
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
                num = ""
                skip = True
                continue
            else:
                # Escaped closing bracket, not part of a reference
                skip = True
                newString += "]"
                continue
        if isNumber:
            num += letter
        if not isNumber:
            newString += letter
    return newString

def isIEEEReference(string):
    """Check if line starts with IEEE-style reference like \[1\]"""
    stripped = string.strip()
    if not stripped.startswith("\\["):
        return False, 0

    # Find the closing \]
    idx = 2  # Start after \[
    while idx < len(stripped) and stripped[idx] in "0123456789":
        idx += 1

    if idx < len(stripped) and stripped[idx:idx+2] == "\\]":
        # Extract reference number
        ref_num = stripped[2:idx]
        # Return True and the reference number
        return True, ref_num

    return False, 0

def unescapeString(string):
    """Remove escape characters for special characters (except brackets, which are handled by parseReferences)"""
    result = ""
    skip = False
    for i in range(len(string)):
        if skip:
            skip = False
            continue
        if string[i] == "\\" and i + 1 < len(string) and string[i+1] in "._":
            # Skip the backslash but the next iteration will add the character
            continue
        result += string[i]
    return result

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
            newString += f'<Link href="{linkRoute}">{linkText}</Link>'
            continue
        if linkR:
            linkRoute += letter
        if linkT:
            linkText += letter
        if not linkR and not linkT:
            newString += letter
    return parseBoldItalic(unescapeString(parseReferences(newString)))

def parseIEEEReference(string):
    """Parse IEEE reference content without converting numeric references to ScrollLinks"""
    newString = ""
    linkT = False
    linkR = False
    linkText = ""
    linkRoute = ""
    for i, letter in enumerate(string):
        if letter == "[" and i + 1 < len(string) and string[i+1] not in "1234567890":
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
            newString += f'<Link href="{linkRoute}">{linkText}</Link>'
            linkRoute = ""
            linkText = ""
            continue
        if linkR:
            linkRoute += letter
        if linkT:
            linkText += letter
        if not linkR and not linkT:
            newString += letter
    return parseBoldItalic(unescapeString(newString))

def isOrderedListItem(string):
    idx = 0
    breakFlag = False
    while idx < 1000:
        if string[idx] in "1234567890":
            idx += 1
        elif string[idx] == "." and (idx == 0 or string[idx-1] != "\\"):
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
    tag = "TH" if isHeader else "TD"

    row_content = ""
    for cell in cells:
        row_content += f'<{tag}>{parseLinks(cell)}</{tag}>'

    return f'<TR>{row_content}</TR>'

with open("output_jsx.txt", "w", encoding="utf-8") as out:
    # Write imports at the top
    with open("input_file.md", encoding="utf-8") as f:
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
        ieeeRef = False
        ieeeRefContent = ""
        ieeeRefNum = ""
        for i, line in enumerate(lines):
            isOlItem, numberLength = isOrderedListItem(line)
            isTable = isTableRow(line)
            isIEEE, ieeeNum = isIEEEReference(line)

            if skipNext:
                skipNext = False
                continue

            if line.startswith("img(") and line.strip().endswith(")"):
                url = line[4:-2]
                caption = lines[i + 1].strip()
                imageCount += 1
                skipNext = True
                jsx = f'<Figure src="{url}" alt="{caption}" caption="{caption}" figNumber={imageCount} />\n'
                out.write(jsx)
                continue

            # Handle IEEE-style references
            if isIEEE and not ieeeRef:
                # Start of a new IEEE reference
                ieeeRef = True
                ieeeRefNum = ieeeNum
                # Remove the \[num\] prefix and store the content
                stripped = line.strip()
                idx = stripped.find("\\]") + 2
                ieeeRefContent = stripped[idx:].strip()
                continue
            elif ieeeRef and not isIEEE and line.strip() != "":
                # Continuation of IEEE reference
                ieeeRefContent += " " + line.strip()
                continue
            elif ieeeRef and (line.strip() == "" or isIEEE):
                # End of IEEE reference (blank line or start of new reference)
                if not ol:
                    out.write('<OL>\n')
                    ol = True
                out.write(f'<LI id="reference-{ieeeRefNum}">{parseIEEEReference(ieeeRefContent)}</LI>\n')
                ieeeRef = False
                ieeeRefContent = ""
                ieeeRefNum = ""

                # If this is a new IEEE reference, handle it
                if isIEEE:
                    ieeeRef = True
                    ieeeRefNum = ieeeNum
                    stripped = line.strip()
                    idx = stripped.find("\\]") + 2
                    ieeeRefContent = stripped[idx:].strip()
                continue

            if line == "\n" : continue
            # Headers
            elif line[0] == "#":
                if line[0:2] == "# ":
                    if "References" in line:
                        ref = True
                    content = line[2:].rstrip('\n').replace("*","")
                    out.write(f'<H2 id="heading {headerIndex}">{content}</H2>\n')
                    headerIndex += 1
                elif line[0:3] == "## ":
                    content = line[3:].rstrip('\n').replace("*","")
                    out.write(f'<H3 id="subheading {subheaderIndex}">{content}</H3>\n')
                    subheaderIndex += 1
            # Table handling
            elif isTable and not table:
                # Start of table - write header
                table = True
                table_body_started = False
                out.write('<TableWrapper>\n')
                out.write('<Table>\n<THead>\n')
                out.write(parseTableRow(line, isHeader=True) + '\n')
            elif isTable and table:
                # Check if this is the alignment row (contains :---- pattern)
                if line.strip().startswith('|') and ':' in line and '-' in line:
                    # Skip alignment row
                    continue
                else:
                    # This is a data row
                    if i > 0 and not table_body_started:
                        out.write('</THead>\n<TBody>\n')
                        table_body_started = True
                    elif 'table_body_started' not in locals():
                        table_body_started = False

                    if table_body_started or (i > 0 and lines[i-1].strip().startswith('|') and ':' in lines[i-1] and '-' in lines[i-1]):
                        if not table_body_started:
                            out.write('</THead>\n<TBody>\n')
                            table_body_started = True
                        out.write(parseTableRow(line) + '\n')

                    # Check if table ends
                    if i+1 == len(lines) or not isTableRow(lines[i+1]):
                        out.write('</TBody>\n</Table>\n</TableWrapper>\n')
                        table = False
                        if 'table_body_started' in locals():
                            del table_body_started
            # ul and ol
            # ul
            elif line[0:2] in ["- ", "* "] and not ul:
                ul = True
                out.write('<UL>\n')
                content = line[2:].rstrip('\n')
                out.write(f'<LI>{parseLinks(content)}</LI>\n')
            elif line[0:2] in ["- ", "* "] and ul:
                content = line[2:].rstrip('\n')
                out.write(f'<LI>{parseLinks(content)}</LI>\n')
                if i+1 == len(lines) or lines[i+1][0:2] not in ["- ", "* "]:
                    out.write("</UL>\n")
                    ul = False
            # ol
            elif isOlItem and not ol:
                ol = True
                out.write('<OL>\n')
                addition = ""
                if ref:
                    addition = f' id="reference-{refIdx}"'
                    refIdx += 1
                content = line[numberLength+2:].rstrip('\n')
                out.write(f'<LI{addition}>{parseLinks(content)}</LI>\n')
            elif isOlItem and ol:
                addition = ""
                if ref:
                    addition = f' id="reference-{refIdx}"'
                    refIdx += 1
                content = line[numberLength+2:].rstrip('\n')
                out.write(f'<LI{addition}>{parseLinks(content)}</LI>\n')
                if i+1 != len(lines): isOlItem, _ = isOrderedListItem(lines[i+1])
                if i+1 == len(lines) or not isOlItem:
                    out.write("</OL>\n")
                    ol = False
            else:
                content = line.rstrip('\n')
                out.write(f'<P>{parseLinks(content)}</P>\n')

        # Handle any remaining IEEE reference at end of file
        if ieeeRef and ieeeRefContent:
            if not ol:
                out.write('<OL>\n')
                ol = True
            out.write(f'<LI id="reference-{ieeeRefNum}">{parseIEEEReference(ieeeRefContent)}</LI>\n')

        # Close any open OL tag
        if ol:
            out.write("</OL>\n")
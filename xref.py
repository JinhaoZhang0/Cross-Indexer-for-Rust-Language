import os
import re

from typing import List


class Row:
    def __init__(self, file_name, column1, column2, src_line, color):
        # row_name works as an identifier of the current row
        # 		can be a choose between int & String
        # column1 & column2 are list of lines that should fit into two rows
        # color is the color of row (black/grey)
        self.file_name = file_name
        self.asm = column1
        self.src = column2
        self.src_line = src_line
        self.color = color

    def print_row(self):
        print("file name: ", self.file_name)
        print("    color: ", self.color)
        print("source line: ", self.src_line)
        print("asm: ")
        for asm in self.asm:
            print(asm)
        print("src: ")
        for src in self.src:
            print(src)
        print("")


# TODO: haven't coded yet
def write_html(rows):
    html_file = open("xref.html", "w")
    # Add header and footer into html file
    header = open("header.txt", "r")
    footer = open("footer.txt", "r")
    html_file.write(header.read())
    header.close()

    # add row elements into html file
    for row in rows:
        html_file.write("\n\t\t<div class=\"code-block\">\n")
        html_file.write("\t\t\t<div class=\"asm-block\">\n")
        html_file.write("\t\t\t\t<span>~</span>\n")
        asm_start = row.asm[0].split(' ', 1)
        html_file.write("\t\t\t\t<pre class=\"prettyprint linenums:" + asm_start[0] + "\">\n")

        for i in range(len(row.asm)):
            asm_code = row.asm[i].split(":", 1)
            asm_addr = asm_code[0].split()
            asm_token = asm_code[1].split()
            html_file.write("<span class=\"nocode\"><a name=\"asmline"+ asm_addr[1] + "\">" + asm_addr[1]
                            + "</a></span>: ")
            html_file.write(asm_code[1])
            need_ref = re.search(r'j|call', asm_code[1], re.I)
            if need_ref and asm_token[-2] != "callq":
                html_file.write("<span class=\"nocode\">(REF: <a href=\"#asmline" + asm_token[-2] + "\">"
                                + asm_token[-2] + "</a>)</span>")
            if i != len(row.asm) - 1:
                html_file.write("\n")
            else:
                html_file.write("\t</pre>\n")
                # asm_code = row.asm[i].split(' ', 1)
                # html_file.write(asm_code[1] + "\n")
        # asm_code = row.asm[-1].split(' ', 1)
        # html_file.write(asm_code[1] + "\t</pre>\n")
        html_file.write("\t\t\t</div>\n")
        html_file.write("\t\t\t<div class=\"src-block\">\n")
        html_file.write("\t\t\t\t<span>" + row.file_name + "</span>\n")
        if row.color == "black":
            html_file.write("\t\t\t\t<pre class=\"prettyprint linenums:" + row.src_line + "\">\n")
            for i in range(len(row.src) - 1):
                html_file.write(row.src[i] + "\n")
            html_file.write(row.src[-1] + "\t</pre>\n")
        else:
            html_file.write("\t\t\t\t<pre class=\"grey\">\n")
            src_line = int(row.src_line)
            for i in range(len(row.src) - 1):
                html_file.write("   " + str(src_line) + ".\t" + row.src[i] + "\n")
                src_line += 1
            html_file.write("   " + str(src_line) + ".\t" + row.src[-1] + "\t</pre>\n")
        html_file.write("\t\t\t</div>\n")
        html_file.write("\t\t</div>\n")

        # html_file.write("\t\t\t\t" + code.replace(' ', "&nbsp;").replace('\"', "&quot;").replace(
        #     '&"', "&amp;").replace('<',"&lt;").replace('>', "&gt;") + "<br>\n")

    html_file.write(footer.read())
    footer.close()
    html_file.close()


# TODO: haven't coded yet
def obdjump_dwarfjump():
    objdump_stream = os.popen("objdump -d myprogram")
    objdump = objdump_stream.read()
    dwarf_stream = os.popen("llvm-dwarfdump --debug-line myprogram")
    dwarf = dwarf_stream.read()

    f = open("objdump.txt", "w")
    f.write(objdump)
    f.close()

    f2 = open("dwarfdump.txt", "w")
    f2.write(dwarf)
    f2.close()


# Find rust file blocks in the dwarf file, return the blocks
def find_rust_block_in_dwarf(file_names) -> List[List[str]]:
    # Open generated dwarfdump file
    f = open("dwarfdump.txt", "r")
    r_names = []

    # Change the file name to regex format
    # Such as: r_names = [r'name: \"fib\.rs\"(.*)', r'name: \"main\.rs\"(.*)']
    for file_name in file_names:
        r_name = file_name.replace('.', "\.")
        r_name = 'name: \\\"' + r_name + '\"(.*)'
        # print(r_name)
        r_names.append(r_name)

    # Get the blocks using regex
    files = []
    dwarf = f.readlines()
    rows = len(dwarf)
    f.close()
    for r_name in r_names:
        i = 0
        func = []
        for line in dwarf:
            file = re.search(r_name, line, re.I | re.M)
            i += 1
            if file:
                break

        for j in range(i, rows):
            file = re.search(r'debug_line(.*)', dwarf[j], re.I | re.M)
            if not file:
                func.append(dwarf[j])
            else:
                break
        files.append(func)
    # print(files)

    return files


# Find dwarf lines
def find_dwarf_lines(block):
    lines = []
    for line in block:
        asm_src = re.match(r'0x[0-9a-f]{16}.*', line)
        if asm_src:
            lines.append(asm_src.group())
    return lines


# get a source file list , each element is a dictionary
# keys are source code line numbers
def get_src_file_dict(files):
    src_files = []
    for file in files:
        f = open(file, "r")
        lines = f.readlines()
        f.close()
        src_lines = {}
        for i in range(len(lines)):
            src_lines[str(i + 1)] = lines[i]
        src_files.append(src_lines)
    return src_files


# def find_src_line(file:str, num:int, src_dic:dict):


# Find assembly code blocks in asm file using memory addresses
def find_asm_block_in_asm(dwarf_blocks_lines):
    # get the memory addresses from dwarf blocks
    asm_addresses = []
    for line in dwarf_blocks_lines:
        token = line[0].split()
        asm_address = token[0].replace('0x', '')
        asm_addresses.append(asm_address)

    # Get the blocks using memory addresses
    blocks = []
    f = open("asm.txt", "r")
    asm = f.readlines()
    rows = len(asm)
    f.close()
    for addr in asm_addresses:
        i = 0
        block = []
        address = addr + '(.*)'
        for line in asm:
            file = re.search(address, line, re.I | re.M)
            i += 1
            if file:
                break
        for j in range(i, rows):
            file = re.match(r'^$', asm[j])
            if not file:
                asm_code = str(j + 1) + asm[j]
                block.append(asm_code)
            else:
                break
        blocks.append(block)
    return blocks


# match the assembly code and source code line by line (assembly centred), put all the necessary information in rows
def row_matching(file_names, src_blocks, asm_blocks, dwarf_blocks_lines):
    rows = []
    for i in range(len(file_names)):
        dwarf_line = dwarf_blocks_lines[i]
        asm_line = asm_blocks[i]
        src_line = src_blocks[i]
        # list for detecting repeated source line, if repeated, grey-out the source code
        color = []
        # Pointers for asm lines and dwarf lines
        j, k = 0, 0
        while k < len(dwarf_line) - 1:
            token = dwarf_line[k].split()
            token_next = dwarf_line[k + 1].split()
            # skip the line if source code line is 0
            if token[1] == "0":
                k += 1
                continue

            # Generate next token so that its source line number is different from the current token
            while token_next[1] == token[1]:
                k += 1
                if k + 1 < len(dwarf_line):
                    token_next = dwarf_line[k + 1].split()
                else:
                    break
            asm_addr_curr = token[0].replace("0x000000000000", "")
            asm_addr_next = token_next[0].replace("0x000000000000", "")
            # Get the assembly code from asm block
            asm_code = []
            asm_start = None
            while not asm_start:
                asm_start = re.search(asm_addr_curr, asm_line[j])
                j += 1
            asm_code.append(asm_line[j - 1].replace("\n", ""))
            asm_end = re.search(asm_addr_next, asm_line[j])
            while not asm_end:
                # print(asm_line[j])
                asm_code.append(asm_line[j].replace("\n", ""))
                j += 1
                if j == len(asm_line):
                    break
                asm_end = re.search(asm_addr_next, asm_line[j])

            # Get the source code from source block
            # print(token[1])
            src_code = [src_line[token[1]].replace("\n", "")]
            # record all the information in the row object
            # if the source code appears before, turn code into grey
            if token[1] not in color:
                row = Row(file_names[i], asm_code, src_code, token[1], "black")
                color.append(token[1])
                rows.append(row)
            else:
                row = Row(file_names[i], asm_code, src_code, token[1], "grey")
                rows.append(row)
            k += 1

    return rows


# TODO: main function
def xref():
    file_names = ['fib.rs', 'main.rs']
    dwarf_blocks = find_rust_block_in_dwarf(file_names)
    dwarf_blocks_lines = []
    for d_block in dwarf_blocks:
        dwarf_lines = find_dwarf_lines(d_block)
        dwarf_blocks_lines.append(dwarf_lines)
    src_blocks = get_src_file_dict(file_names)
    asm_blocks = find_asm_block_in_asm(dwarf_blocks_lines)
    rows = row_matching(file_names, src_blocks, asm_blocks, dwarf_blocks_lines)
    for row in rows:
        row.print_row()
    write_html(rows)


if __name__ == '__main__':
    xref()

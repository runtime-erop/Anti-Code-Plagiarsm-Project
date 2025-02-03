import tkinter as tk
from tkinter import filedialog
import ast
import re
import time

def rm_cmt(c):
    c = re.sub(r'#.*', '', c)
    c = re.sub(r'\'\'\'.*?\'\'\'', '', c, flags=re.DOTALL)
    c = re.sub(r'\"\"\".*?\"\"\"', '', c, flags=re.DOTALL)
    return c.strip()

def remove_bom(c):
    if c.startswith('\ufeff'):
        c = c[1:]
    return c

def norm(c):
    try:
        p = ast.parse(c)
        for n in ast.walk(p):
            if isinstance(n, ast.Name):
                n.id = 'V'
            elif isinstance(n, ast.FunctionDef):
                n.name = 'F'
                for a in n.args.args:
                    a.arg = 'V'
            elif isinstance(n, ast.Constant):
                n.value = 'C'
        return ast.dump(p)
    except Exception as e:
        return None

def split_code(c):
    parts = []
    lines = c.splitlines()
    current_part = []
    in_function = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("def ") or stripped.startswith("class "):
            if current_part:
                parts.append("\n".join(current_part))
                current_part = []
            in_function = True
            current_part.append(line)
        elif in_function:
            current_part.append(line)
            if stripped == "":
                in_function = False
                parts.append("\n".join(current_part))
                current_part = []
        else:
            if stripped:
                current_part.append(line)
            else:
                if current_part:
                    parts.append("\n".join(current_part))
                    current_part = []

    if current_part:
        parts.append("\n".join(current_part))

    return parts

def compare_parts(p1, p2):
    matches = []
    for part1 in p1:
        norm1 = norm(part1)
        if norm1 is None:
            continue
        for part2 in p2:
            norm2 = norm(part2)
            if norm2 is None:
                continue
            if norm1 == norm2:
                matches.append((part1, part2))
                break
    return matches

def main():
    r = tk.Tk()
    r.withdraw()

    print("Press 'n' for normal mode, 'f' for function misplacement detection, 'df' for debug mode (function), 'dn' for debug mode (normal):")
    mode = input().strip().lower()

    f = filedialog.askopenfilenames(title="Select two files", filetypes=[("Python Files", "*.py")])
    
    if len(f) != 2:
        print("INVALID FILE: 1")
        print("INVALID FILE: 2")
        return

    start_time = time.time()

    p1, p2 = f
    with open(p1, 'r', encoding='utf-8-sig') as f1, open(p2, 'r', encoding='utf-8-sig') as f2:
        c1, c2 = f1.read(), f2.read()

    c1, c2 = remove_bom(c1), remove_bom(c2)
    c1, c2 = rm_cmt(c1), rm_cmt(c2)

    if not c1.strip():
        print("INVALID FILE: 1 (Empty after removing comments)")
        n1 = None
    else:
        n1 = norm(c1)

    if not c2.strip():
        print("INVALID FILE: 2 (Empty after removing comments)")
        n2 = None
    else:
        n2 = norm(c2)

    if mode in ('f', 'df'):
        p1_parts = split_code(c1)
        p2_parts = split_code(c2)
        matches = compare_parts(p1_parts, p2_parts)

        if mode == 'df':
            print("Parts from File 1:")
            for i, part in enumerate(p1_parts, 1):
                print(f"Part {i}:\n{part}")
            print("\nParts from File 2:")
            for i, part in enumerate(p2_parts, 1):
                print(f"Part {i}:\n{part}")
            print("\nMatching Parts:")
            for match in matches:
                print(f"Match:\n{match[0]}\n{match[1]}")

        if len(matches) == max(len(p1_parts), len(p2_parts)):
            print("FILES MATCH WITH FUNCTION REPOSITION DETECTION")
        else:
            print("FILES DO NOT MATCH WITH FUNCTION REPOSITION DETECTION")

    elif mode in ('n', 'dn'):
        if mode == 'dn':
            print("Normalized Code 1:", n1)
            print("Normalized Code 2:", n2)

        if n1 is None:
            print("INVALID FILE: 1")
        if n2 is None:
            print("INVALID FILE: 2")

        if n1 is None or n2 is None:
            return

        if n1 == n2:
            print("FILES MATCH")
        else:
            print("FILES DO NOT MATCH")

    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    main()

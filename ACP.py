import tkinter as tk
from tkinter import filedialog
import ast
import re

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
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
        return None
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return None

def main():
    r = tk.Tk()
    r.withdraw()

    f = filedialog.askopenfilenames(title="Select two files", filetypes=[("Python Files", "*.py")])
    
    if len(f) != 2:
        print("INVALID FILE: 1")
        print("INVALID FILE: 2")
        return

    p1, p2 = f
    with open(p1, 'r', encoding='utf-8-sig') as f1, open(p2, 'r', encoding='utf-8-sig') as f2:
        c1, c2 = f1.read(), f2.read()

    print("Raw Code 1:", repr(c1))
    print("Raw Code 2:", repr(c2))

    c1, c2 = remove_bom(c1), remove_bom(c2)
    c1, c2 = rm_cmt(c1), rm_cmt(c2)

    print("Code 1 After Removing Comments:", repr(c1))
    print("Code 2 After Removing Comments:", repr(c2))

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

if __name__ == "__main__":
    main()

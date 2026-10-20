import time
from typing import Tuple
from pysat.formula import CNF
from src.instances import NQueensInstance
from src.encodings import encode_amo, encode_alo


def grid_to_var(r: int, c: int, n: int) -> int:
    # Chuyen toa do (r, c) 0-indexed sang index bien SAT 1-indexed (1..N^2)
    return r * n + c + 1


def var_to_grid(var_id: int, n: int) -> Tuple[int, int]:
    # Chuyen nguoc lai index bien sang (r, c)
    v = var_id - 1
    return v // n, v % n


def build_nqueens_cnf(
    instance: NQueensInstance,
    amo_method: str = "sequential",
    alo_column: bool = False,
    symmetry_breaking: bool = False
) -> Tuple[CNF, int, float]:
    t0 = time.perf_counter()
    n = instance.N
    cnf = CNF()
    top_id = n * n

    # Rang buoc tung hang: moi hang dung 1 quan hau (ALO + AMO)
    for r in range(n):
        row_lits = [grid_to_var(r, c, n) for c in range(n)]
        for cl in encode_alo(row_lits):
            cnf.append(cl)
        clauses, top_id = encode_amo(row_lits, top_id, method=amo_method)
        cnf.extend(clauses)

    # Rang buoc tung cot: toi da 1 hau (co the them ALO neu can)
    for c in range(n):
        col_lits = [grid_to_var(r, c, n) for r in range(n)]
        if alo_column:
            for cl in encode_alo(col_lits):
                cnf.append(cl)
        clauses, top_id = encode_amo(col_lits, top_id, method=amo_method)
        cnf.extend(clauses)

    # Duong cheo chinh: r - c = k (chi xet duong cheo co tu 2 o tro len)
    for k in range(-(n - 2), n - 1):
        diag_lits = []
        for r in range(n):
            c = r - k
            if 0 <= c < n:
                diag_lits.append(grid_to_var(r, c, n))
        if len(diag_lits) >= 2:
            clauses, top_id = encode_amo(diag_lits, top_id, method=amo_method)
            cnf.extend(clauses)

    # Duong cheo phu: r + c = k
    for k in range(1, 2 * n - 2):
        anti_lits = []
        for r in range(n):
            c = k - r
            if 0 <= c < n:
                anti_lits.append(grid_to_var(r, c, n))
        if len(anti_lits) >= 2:
            clauses, top_id = encode_amo(anti_lits, top_id, method=amo_method)
            cnf.extend(clauses)

    # Hau da dat san (cho bien the V2, V3)
    for (fr, fc) in instance.fixed_queens:
        cnf.append([grid_to_var(fr, fc, n)])

    # Pha doi xung: hau o hang 0 chi nam o nua ban co dau tien
    if symmetry_breaking and n >= 2:
        half = (n + 1) // 2
        for c in range(half, n):
            cnf.append([-grid_to_var(0, c, n)])

    encode_time = time.perf_counter() - t0
    return cnf, top_id, encode_time


def export_dimacs(cnf: CNF, top_id: int, filepath: str) -> None:
    # Xuat file .cnf theo chuan DIMACS cho solver Kissat
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"p cnf {top_id} {len(cnf.clauses)}\n")
        for cl in cnf.clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")

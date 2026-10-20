import math
from typing import List, Tuple
from pysat.card import CardEnc, EncType


def encode_alo(lits: List[int]) -> List[List[int]]:
    if not lits:
        return []
    return [lits]


def _encode_amo_pairwise(lits: List[int]) -> List[List[int]]:
    # Cap doi phu dinh (-x_i v -x_j)
    clauses = []
    n = len(lits)
    for i in range(n):
        for j in range(i + 1, n):
            clauses.append([-lits[i], -lits[j]])
    return clauses


def _encode_amo_commander(lits: List[int], top_id: int, group_size: int = 3) -> Tuple[List[List[int]], int]:
    # Commander encoding: chia bien thanh tung nhom nho group_size
    n = len(lits)
    if n <= 1:
        return [], top_id
    if n <= group_size:
        return _encode_amo_pairwise(lits), top_id

    clauses = []
    curr_top = top_id
    commanders = []

    for i in range(0, n, group_size):
        group = lits[i:i + group_size]
        if len(group) == 1:
            commanders.append(group[0])
            continue

        curr_top += 1
        cmd = curr_top
        commanders.append(cmd)

        # 1. AMO noi bo trong group
        clauses.extend(_encode_amo_pairwise(group))

        # 2. Lien he giua group va bien commander:
        # co it nhat 1 bien bat -> commander bat
        for x in group:
            clauses.append([-x, cmd])

        # commander bat -> co bien trong nhom bat
        clauses.append([-cmd] + group)

    # De quy ap dung AMO cho danh sach cac commander
    rec_clauses, curr_top = _encode_amo_commander(commanders, curr_top, group_size)
    clauses.extend(rec_clauses)
    return clauses, curr_top


def _encode_amo_product(lits: List[int], top_id: int) -> Tuple[List[List[int]], int]:
    # 2D Product encoding: xep bien len luoi 2D kich thuoc p x q
    n = len(lits)
    if n <= 1:
        return [], top_id
    if n <= 3:
        return _encode_amo_pairwise(lits), top_id

    p = math.ceil(math.sqrt(n))
    q = math.ceil(n / p)

    curr_top = top_id
    # Bien hang va bien cot phu tro
    row_vars = [curr_top + i + 1 for i in range(p)]
    curr_top += p

    col_vars = [curr_top + j + 1 for j in range(q)]
    curr_top += q

    clauses = []

    # Map tung literal vao toa do (u, v)
    for idx, x in enumerate(lits):
        u = idx // q
        v = idx % q
        clauses.append([-x, row_vars[u]])
        clauses.append([-x, col_vars[v]])

    # AMO tren tap bien hang va bien cot
    clauses.extend(_encode_amo_pairwise(row_vars))
    clauses.extend(_encode_amo_pairwise(col_vars))

    return clauses, curr_top


def encode_amo(lits: List[int], top_id: int, method: str = "pairwise") -> Tuple[List[List[int]], int]:
    if len(lits) <= 1:
        return [], top_id

    method = method.lower()

    if method == "pairwise":
        return _encode_amo_pairwise(lits), top_id

    elif method == "commander":
        return _encode_amo_commander(lits, top_id, group_size=3)

    elif method == "product":
        return _encode_amo_product(lits, top_id)

    elif method == "sequential":
        cnf = CardEnc.atmost(lits=lits, bound=1, top_id=top_id, encoding=EncType.seqcounter)
        max_var = max((abs(lit) for cl in cnf.clauses for lit in cl), default=top_id)
        return cnf.clauses, max(top_id, max_var)

    elif method == "bitwise":
        cnf = CardEnc.atmost(lits=lits, bound=1, top_id=top_id, encoding=EncType.bitwise)
        max_var = max((abs(lit) for cl in cnf.clauses for lit in cl), default=top_id)
        return cnf.clauses, max(top_id, max_var)

    elif method == "ladder":
        cnf = CardEnc.atmost(lits=lits, bound=1, top_id=top_id, encoding=EncType.ladder)
        max_var = max((abs(lit) for cl in cnf.clauses for lit in cl), default=top_id)
        return cnf.clauses, max(top_id, max_var)

    elif method == "totalizer":
        cnf = CardEnc.atmost(lits=lits, bound=1, top_id=top_id, encoding=EncType.totalizer)
        max_var = max((abs(lit) for cl in cnf.clauses for lit in cl), default=top_id)
        return cnf.clauses, max(top_id, max_var)

    else:
        raise ValueError(f"Khong ho tro kieu ma hoa AMO: {method}")


SUPPORTED_ENCODINGS = [
    "pairwise",
    "sequential",
    "bitwise",
    "ladder",
    "totalizer",
    "commander",
    "product"
]

from typing import List, Tuple, Union, Optional


def verify_nqueens_solution(
    n: int,
    solution: Union[List[int], List[Tuple[int, int]]],
    fixed_queens: Optional[List[Tuple[int, int]]] = None
) -> Tuple[bool, str]:
    if solution is None:
        return False, "Solution is None"

    if len(solution) != n:
        return False, f"Expected {n} queens, got {len(solution)}"

    # Chuan hoa ve danh sach toa do (r, c)
    if isinstance(solution[0], tuple):
        coords = list(solution)
    elif isinstance(solution[0], int):
        coords = [(r, c) for r, c in enumerate(solution)]
    else:
        return False, f"Dinh dang solution khong hop le: {type(solution[0])}"

    rows = set()
    cols = set()
    main_diags = set()  # r - c
    anti_diags = set()  # r + c

    for idx, (r, c) in enumerate(coords):
        if not (0 <= r < n and 0 <= c < n):
            return False, f"Quan hau {idx} tai ({r}, {c}) nam ngoai ban co"

        if r in rows:
            return False, f"Trung hang: {r}"
        rows.add(r)

        if c in cols:
            return False, f"Trung cot: {c}"
        cols.add(c)

        d_main = r - c
        if d_main in main_diags:
            return False, f"Xung dot duong cheo chinh (r - c = {d_main}) tai ({r}, {c})"
        main_diags.add(d_main)

        d_anti = r + c
        if d_anti in anti_diags:
            return False, f"Xung dot duong cheo phu (r + c = {d_anti}) tai ({r}, {c})"
        anti_diags.add(d_anti)

    # Kiem tra cac quan hau co dinh (V2/V3)
    if fixed_queens:
        solution_set = set(coords)
        for (fr, fc) in fixed_queens:
            if (fr, fc) not in solution_set:
                return False, f"Thieu quan hau bat buoc tai ({fr}, {fc})"

    return True, "Valid solution"


if __name__ == "__main__":
    # Test nhanh tren N=4 va N=8
    assert verify_nqueens_solution(4, [1, 3, 0, 2])[0]
    assert not verify_nqueens_solution(4, [1, 2, 0, 3])[0]
    print("verify.py OK")

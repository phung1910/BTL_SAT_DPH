import random
from dataclasses import dataclass, field
from typing import List, Tuple
from src.verify import verify_nqueens_solution


@dataclass
class NQueensInstance:
    N: int
    variant: str  # V1, V2, V3
    fixed_queens: List[Tuple[int, int]] = field(default_factory=list)
    seed: int = 0
    k_ratio: float = 0.0
    instance_id: str = ""

    def __post_init__(self):
        if not self.instance_id:
            if self.variant == "V1":
                self.instance_id = f"V1_N{self.N}_s{self.seed}"
            else:
                pct = int(round(self.k_ratio * 100))
                self.instance_id = f"{self.variant}_N{self.N}_k{pct}pct_s{self.seed}"


def get_constructive_solution(n: int) -> List[int]:
    # Sinh nhanh 1 nghiem dung O(N) theo thuat toan Bernhardsson
    if n < 4:
        raise ValueError("Yeu cau N >= 4")

    rem = n % 6
    if rem not in (2, 3):
        evens = list(range(2, n + 1, 2))
        odds = list(range(1, n + 1, 2))
        sol_1based = evens + odds
    elif rem == 2:
        evens = list(range(2, n + 1, 2))
        odds = [3, 1] + [x for x in range(7, n + 1, 2)] + [5]
        if n == 8:
            odds = [3, 1, 7, 5]
        sol_1based = evens + odds
    else:  # rem == 3
        evens = [x for x in range(4, n + 1, 2)] + [2]
        odds = [x for x in range(5, n + 1, 2)] + [1, 3]
        sol_1based = evens + odds

    sol_0based = [x - 1 for x in sol_1based]
    is_valid, _ = verify_nqueens_solution(n, sol_0based)
    if is_valid:
        return sol_0based

    # Neu co ngoai le, fallback ve backtracking don gian
    return _simple_solve_nqueens(n)


def _simple_solve_nqueens(n: int) -> List[int]:
    cols = [-1] * n
    col_used = [False] * n
    d1_used = [False] * (2 * n)
    d2_used = [False] * (2 * n)

    def backtrack(r: int) -> bool:
        if r == n:
            return True
        candidates = list(range(n))
        random.shuffle(candidates)
        for c in candidates:
            if not col_used[c] and not d1_used[r - c + n] and not d2_used[r + c]:
                cols[r] = c
                col_used[c] = True
                d1_used[r - c + n] = True
                d2_used[r + c] = True

                if backtrack(r + 1):
                    return True

                col_used[c] = False
                d1_used[r - c + n] = False
                d2_used[r + c] = False
        return False

    backtrack(0)
    return cols


def generate_v1(N: int, seed: int = 0) -> NQueensInstance:
    # Ban co trong tieu chuan
    return NQueensInstance(N=N, variant="V1", fixed_queens=[], seed=seed, k_ratio=0.0)


def generate_v2(N: int, k_ratio: float, seed: int = 0) -> NQueensInstance:
    # V2: Lay k quan hau tu 1 nghiem dung (luon SAT)
    rng = random.Random(seed)
    full_sol = get_constructive_solution(N)
    k = max(1, int(round(k_ratio * N)))

    chosen_rows = rng.sample(range(N), k)
    fixed = sorted([(r, full_sol[r]) for r in chosen_rows])

    return NQueensInstance(
        N=N,
        variant="V2",
        fixed_queens=fixed,
        seed=seed,
        k_ratio=k_ratio
    )


def generate_v3(N: int, k_ratio: float, seed: int = 0) -> NQueensInstance:
    # V3: Dat ngau nhien k quan hau (co the SAT hoac UNSAT)
    rng = random.Random(seed)
    k = max(1, int(round(k_ratio * N)))

    chosen_rows = rng.sample(range(N), k)
    chosen_cols = rng.sample(range(N), k)

    fixed = sorted([(chosen_rows[i], chosen_cols[i]) for i in range(k)])

    return NQueensInstance(
        N=N,
        variant="V3",
        fixed_queens=fixed,
        seed=seed,
        k_ratio=k_ratio
    )

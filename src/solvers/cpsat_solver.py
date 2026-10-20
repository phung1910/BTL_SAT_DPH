import time
import psutil
from typing import Optional, List
from ortools.sat.python import cp_model
from src.instances import NQueensInstance
from src.verify import verify_nqueens_solution
from src.solvers.base import BaseSolver, SolverResult


class CPSATSolver(BaseSolver):
    def __init__(self, model_type: str = "integer"):
        name = f"cpsat_{model_type}"
        super().__init__(name=name)
        self.model_type = model_type.lower()

    def solve(
        self,
        instance: NQueensInstance,
        time_limit: float = 600.0,
        **kwargs
    ) -> SolverResult:
        process = psutil.Process()
        mem_before = process.memory_info().rss / (1024 * 1024)

        t0_enc = time.perf_counter()
        model = cp_model.CpModel()
        n = instance.N

        solution: Optional[List[int]] = None
        num_vars = 0
        num_clauses = 0

        if self.model_type == "integer":
            # Mo hinh bien nguyen: queens[r] luu cot cua quan hau o hang r
            queens = [model.NewIntVar(0, n - 1, f"q_{r}") for r in range(n)]
            num_vars = n

            # Cac rang buoc AllDifferent cho cot va hai duong cheo
            model.AddAllDifferent(queens)
            model.AddAllDifferent([queens[r] - r for r in range(n)])
            model.AddAllDifferent([queens[r] + r for r in range(n)])

            for (fr, fc) in instance.fixed_queens:
                model.Add(queens[fr] == fc)

            num_clauses = 3 + len(instance.fixed_queens)

        elif self.model_type == "boolean":
            # Mo hinh ma tran nhi phan 0-1
            x = {}
            for r in range(n):
                for c in range(n):
                    x[r, c] = model.NewBoolVar(f"x_{r}_{c}")
            num_vars = n * n

            # Moi hang dung 1 quan hau
            for r in range(n):
                model.Add(sum(x[r, c] for c in range(n)) == 1)
                num_clauses += 1

            # Moi cot dung 1 quan hau
            for c in range(n):
                model.Add(sum(x[r, c] for r in range(n)) == 1)
                num_clauses += 1

            # Duong cheo chinh <= 1
            for k in range(-(n - 2), n - 1):
                diag = [x[r, r - k] for r in range(n) if 0 <= r - k < n]
                if len(diag) >= 2:
                    model.Add(sum(diag) <= 1)
                    num_clauses += 1

            # Duong cheo phu <= 1
            for k in range(1, 2 * n - 2):
                anti = [x[r, k - r] for r in range(n) if 0 <= k - r < n]
                if len(anti) >= 2:
                    model.Add(sum(anti) <= 1)
                    num_clauses += 1

            for (fr, fc) in instance.fixed_queens:
                model.Add(x[fr, fc] == 1)
                num_clauses += 1

        else:
            raise ValueError(f"Khong ro model type: {self.model_type}")

        t_encode = time.perf_counter() - t0_enc

        # Cau hinh solver CP-SAT
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        solver.parameters.num_search_workers = 1  # 1 worker de so sanh cong bang

        t0_solve = time.perf_counter()
        status_code = solver.Solve(model)
        t_solve = time.perf_counter() - t0_solve

        status = "UNKNOWN"
        is_valid = False
        error_msg = ""

        if status_code in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "SAT"
            if self.model_type == "integer":
                solution = [int(solver.Value(queens[r])) for r in range(n)]
            else:
                solution = [-1] * n
                for r in range(n):
                    for c in range(n):
                        if solver.Value(x[r, c]) == 1:
                            solution[r] = c
                            break
            is_valid, msg = verify_nqueens_solution(n, solution, instance.fixed_queens)
            if not is_valid:
                error_msg = f"Kiem tra nghiem that bai: {msg}"
        elif status_code == cp_model.INFEASIBLE:
            status = "UNSAT"
            is_valid = True
        elif status_code == cp_model.UNKNOWN:
            status = "TIMEOUT"

        mem_after = process.memory_info().rss / (1024 * 1024)
        mem_peak = max(mem_after, mem_before)

        return SolverResult(
            instance_id=instance.instance_id,
            solver_name=self.name,
            encoding=self.model_type,
            N=instance.N,
            status=status,
            t_encode=t_encode,
            t_solve=t_solve,
            mem_peak_mb=mem_peak,
            num_vars=num_vars,
            num_clauses=num_clauses,
            is_valid=is_valid,
            solution=solution,
            error_msg=error_msg
        )

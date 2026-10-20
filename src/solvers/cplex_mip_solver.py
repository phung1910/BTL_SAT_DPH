import time
import psutil
from typing import Optional, List
from src.instances import NQueensInstance
from src.verify import verify_nqueens_solution
from src.solvers.base import BaseSolver, SolverResult


class CPLEXMIPSolver(BaseSolver):
    def __init__(self):
        super().__init__(name="cplex_mip")

    def solve(
        self,
        instance: NQueensInstance,
        time_limit: float = 600.0,
        **kwargs
    ) -> SolverResult:
        process = psutil.Process()
        mem_before = process.memory_info().rss / (1024 * 1024)

        t0_enc = time.perf_counter()
        n = instance.N
        num_vars = n * n
        num_clauses = 0

        solution: Optional[List[int]] = None
        status = "UNKNOWN"
        t_solve = 0.0
        is_valid = False
        error_msg = ""

        try:
            from docplex.mp.model import Model
            mdl = Model(name=f"nqueens_{n}")
            mdl.time_limit = time_limit

            x = mdl.binary_var_matrix(n, n, name="x")

            for r in range(n):
                mdl.add_constraint(mdl.sum(x[r, c] for c in range(n)) == 1)
                num_clauses += 1

            for c in range(n):
                mdl.add_constraint(mdl.sum(x[r, c] for r in range(n)) == 1)
                num_clauses += 1

            for k in range(-(n - 2), n - 1):
                diag = [x[r, r - k] for r in range(n) if 0 <= r - k < n]
                if len(diag) >= 2:
                    mdl.add_constraint(mdl.sum(diag) <= 1)
                    num_clauses += 1

            for k in range(1, 2 * n - 2):
                anti = [x[r, k - r] for r in range(n) if 0 <= k - r < n]
                if len(anti) >= 2:
                    mdl.add_constraint(mdl.sum(anti) <= 1)
                    num_clauses += 1

            for (fr, fc) in instance.fixed_queens:
                mdl.add_constraint(x[fr, fc] == 1)
                num_clauses += 1

            t_encode = time.perf_counter() - t0_enc

            t0_solve = time.perf_counter()
            sol = mdl.solve(log_output=False)
            t_solve = time.perf_counter() - t0_solve

            if sol is not None:
                status = "SAT"
                sol_cols = [-1] * n
                for r in range(n):
                    for c in range(n):
                        if sol.get_value(x[r, c]) > 0.5:
                            sol_cols[r] = c
                            break
                solution = sol_cols
                is_valid, msg = verify_nqueens_solution(n, solution, instance.fixed_queens)
                if not is_valid:
                    error_msg = f"Kiem tra nghiem that bai: {msg}"
            else:
                solve_details = mdl.solve_details
                if solve_details and "time_limit" in str(solve_details.status).lower():
                    status = "TIMEOUT"
                else:
                    status = "UNSAT"
                    is_valid = True

        except Exception as e:
            t_encode = time.perf_counter() - t0_enc
            err_str = str(e).lower()
            status = "NO_RUNTIME" if "no cplex runtime found" in err_str else "ERROR"
            error_msg = str(e)

        mem_after = process.memory_info().rss / (1024 * 1024)
        mem_peak = max(mem_after, mem_before)

        return SolverResult(
            instance_id=instance.instance_id,
            solver_name=self.name,
            encoding="binary_mip",
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

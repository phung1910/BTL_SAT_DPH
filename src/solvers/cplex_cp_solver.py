import time
import psutil
from typing import Optional, List
from src.instances import NQueensInstance
from src.verify import verify_nqueens_solution
from src.solvers.base import BaseSolver, SolverResult


class CPLEXCPSolver(BaseSolver):
    def __init__(self):
        super().__init__(name="cplex_cp")

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
        num_vars = n
        num_clauses = 3 + len(instance.fixed_queens)

        solution: Optional[List[int]] = None
        status = "UNKNOWN"
        t_solve = 0.0
        is_valid = False
        error_msg = ""

        try:
            from docplex.cp.model import CpoModel
            mdl = CpoModel(name=f"nqueens_cp_{n}")

            # q[r] la chi so cot cua quan hau tai hang r
            q = [mdl.integer_var(0, n - 1, name=f"q_{r}") for r in range(n)]

            # Rang buoc cot va hai duong cheo khong trung nhau
            mdl.add(mdl.all_diff(q))
            mdl.add(mdl.all_diff([q[i] + i for i in range(n)]))
            mdl.add(mdl.all_diff([q[i] - i for i in range(n)]))

            for (fr, fc) in instance.fixed_queens:
                mdl.add(q[fr] == fc)

            t_encode = time.perf_counter() - t0_enc

            t0_solve = time.perf_counter()
            sol = mdl.solve(TimeLimit=time_limit, LogVerbosity="Quiet")
            t_solve = time.perf_counter() - t0_solve

            if sol and sol.is_solution():
                status = "SAT"
                solution = [int(sol.get_value(q[r])) for r in range(n)]
                is_valid, msg = verify_nqueens_solution(n, solution, instance.fixed_queens)
                if not is_valid:
                    error_msg = f"Kiem tra nghiem that bai: {msg}"
            elif sol and sol.get_solve_status() == "Infeasible":
                status = "UNSAT"
                is_valid = True
            else:
                status = "TIMEOUT"

        except Exception as e:
            t_encode = time.perf_counter() - t0_enc
            err_str = str(e).lower()
            status = "NO_RUNTIME" if ("cannot find" in err_str or "no cplex" in err_str) else "ERROR"
            error_msg = str(e)

        mem_after = process.memory_info().rss / (1024 * 1024)
        mem_peak = max(mem_after, mem_before)

        return SolverResult(
            instance_id=instance.instance_id,
            solver_name=self.name,
            encoding="cpo_all_diff",
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

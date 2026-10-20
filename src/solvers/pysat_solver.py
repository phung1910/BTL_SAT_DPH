import time
import psutil
from typing import Optional, List
from pysat.solvers import Solver
from src.instances import NQueensInstance
from src.cnf_builder import build_nqueens_cnf, var_to_grid
from src.verify import verify_nqueens_solution
from src.solvers.base import BaseSolver, SolverResult


class PySATSolver(BaseSolver):
    def __init__(self, solver_name: str = "cadical153", amo_method: str = "sequential"):
        super().__init__(name=solver_name)
        self.amo_method = amo_method

    def solve(
        self,
        instance: NQueensInstance,
        time_limit: float = 600.0,
        alo_column: bool = False,
        symmetry_breaking: bool = False,
        **kwargs
    ) -> SolverResult:
        process = psutil.Process()
        mem_before = process.memory_info().rss / (1024 * 1024)

        # Xay dung CNF
        cnf, num_vars, t_encode = build_nqueens_cnf(
            instance=instance,
            amo_method=self.amo_method,
            alo_column=alo_column,
            symmetry_breaking=symmetry_breaking
        )
        num_clauses = len(cnf.clauses)

        t_solve = 0.0
        status = "UNKNOWN"
        solution: Optional[List[int]] = None
        is_valid = False
        error_msg = ""

        try:
            with Solver(name=self.name, bootstrap_with=cnf.clauses) as solver:
                t0 = time.perf_counter()
                sat = solver.solve()
                t_solve = time.perf_counter() - t0

                if sat:
                    status = "SAT"
                    model = solver.get_model()
                    if model is not None:
                        # Trich xuat vi tri quan hau tu cac literal duong <= N^2
                        sol_cols = [-1] * instance.N
                        for lit in model:
                            if 1 <= lit <= instance.N * instance.N:
                                r, c = var_to_grid(lit, instance.N)
                                sol_cols[r] = c
                        solution = sol_cols
                        is_valid, msg = verify_nqueens_solution(
                            instance.N, solution, instance.fixed_queens
                        )
                        if not is_valid:
                            error_msg = f"Kiem tra nghiem that bai: {msg}"
                else:
                    status = "UNSAT"
                    is_valid = True

        except MemoryError:
            status = "MEMOUT"
            error_msg = "Tran bo nho RAM khi chay PySAT"
        except Exception as e:
            status = "ERROR"
            error_msg = str(e)

        mem_after = process.memory_info().rss / (1024 * 1024)
        mem_peak = max(mem_after, mem_before)

        return SolverResult(
            instance_id=instance.instance_id,
            solver_name=self.name,
            encoding=self.amo_method,
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

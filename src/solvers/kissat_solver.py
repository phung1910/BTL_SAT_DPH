import time
import os
import subprocess
import tempfile
import psutil
from typing import Optional, List
from pysat.solvers import Solver
from src.instances import NQueensInstance
from src.cnf_builder import build_nqueens_cnf, export_dimacs, var_to_grid
from src.verify import verify_nqueens_solution
from src.solvers.base import BaseSolver, SolverResult


class KissatSolver(BaseSolver):
    def __init__(self, amo_method: str = "sequential", use_wsl: bool = False, wsl_bin: str = "kissat"):
        super().__init__(name="kissat")
        self.amo_method = amo_method
        self.use_wsl = use_wsl
        self.wsl_bin = wsl_bin

    def solve(
        self,
        instance: NQueensInstance,
        time_limit: float = 600.0,
        **kwargs
    ) -> SolverResult:
        if self.use_wsl:
            return self._solve_wsl(instance, time_limit)
        return self._solve_pysat(instance, time_limit)

    def _solve_pysat(self, instance: NQueensInstance, time_limit: float) -> SolverResult:
        process = psutil.Process()
        mem_before = process.memory_info().rss / (1024 * 1024)

        cnf, num_vars, t_encode = build_nqueens_cnf(
            instance=instance,
            amo_method=self.amo_method
        )
        num_clauses = len(cnf.clauses)

        t_solve = 0.0
        status = "UNKNOWN"
        solution: Optional[List[int]] = None
        is_valid = False
        error_msg = ""

        try:
            with Solver(name="kissat404", bootstrap_with=cnf.clauses) as solver:
                t0 = time.perf_counter()
                sat = solver.solve()
                t_solve = time.perf_counter() - t0

                if sat:
                    status = "SAT"
                    model = solver.get_model()
                    if model is not None:
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
        except Exception as e:
            status = "ERROR"
            error_msg = str(e)

        mem_after = process.memory_info().rss / (1024 * 1024)
        mem_peak = max(mem_after, mem_before)

        return SolverResult(
            instance_id=instance.instance_id,
            solver_name="kissat",
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

    def _solve_wsl(self, instance: NQueensInstance, time_limit: float) -> SolverResult:
        process = psutil.Process()
        mem_before = process.memory_info().rss / (1024 * 1024)

        cnf, num_vars, t_encode = build_nqueens_cnf(
            instance=instance,
            amo_method=self.amo_method
        )
        num_clauses = len(cnf.clauses)

        # Tao file tam chua CNF theo chuan DIMACS
        with tempfile.NamedTemporaryFile(suffix=".cnf", delete=False, mode="w") as f:
            tmp_path = f.name

        export_dimacs(cnf, num_vars, tmp_path)

        # Chuyen duong dan Windows sang WSL
        wsl_path = tmp_path.replace("\\", "/").replace("C:", "/mnt/c")
        cmd = ["wsl", self.wsl_bin, f"--time={int(time_limit)}", wsl_path]

        t0 = time.perf_counter()
        status = "UNKNOWN"
        solution: Optional[List[int]] = None
        is_valid = False
        error_msg = ""

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=time_limit + 5)
            t_solve = time.perf_counter() - t0
            output = proc.stdout

            if "s SATISFIABLE" in output:
                status = "SAT"
                model_lits = []
                for line in output.splitlines():
                    if line.startswith("v"):
                        tokens = line.split()[1:]
                        for tok in tokens:
                            val = int(tok)
                            if val == 0:
                                break
                            model_lits.append(val)

                sol_cols = [-1] * instance.N
                for lit in model_lits:
                    if 1 <= lit <= instance.N * instance.N:
                        r, c = var_to_grid(lit, instance.N)
                        sol_cols[r] = c
                solution = sol_cols
                is_valid, msg = verify_nqueens_solution(instance.N, solution, instance.fixed_queens)
                if not is_valid:
                    error_msg = f"Kiem tra nghiem that bai: {msg}"
            elif "s UNSATISFIABLE" in output:
                status = "UNSAT"
                is_valid = True
            else:
                status = "TIMEOUT"
        except subprocess.TimeoutExpired:
            status = "TIMEOUT"
            t_solve = time_limit
        except Exception as e:
            status = "ERROR"
            error_msg = str(e)
            t_solve = time.perf_counter() - t0
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        mem_after = process.memory_info().rss / (1024 * 1024)
        mem_peak = max(mem_after, mem_before)

        return SolverResult(
            instance_id=instance.instance_id,
            solver_name="kissat_wsl" if self.use_wsl else "kissat",
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

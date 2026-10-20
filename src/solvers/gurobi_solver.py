import time
import psutil
from typing import Optional, List
import gurobipy as gp
from gurobipy import GRB
from src.instances import NQueensInstance
from src.verify import verify_nqueens_solution
from src.solvers.base import BaseSolver, SolverResult


class GurobiMIPSolver(BaseSolver):
    def __init__(self):
        super().__init__(name="gurobi_mip")

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
            # Tat log console de khong bi roi man hinh khi chay batch
            env = gp.Env(empty=True)
            env.setParam("OutputFlag", 0)
            env.setParam("Threads", 1)
            env.start()

            with gp.Model("nqueens", env=env) as model:
                model.setParam("TimeLimit", time_limit)

                # Bien nhi phan x[r, c]
                x = model.addVars(n, n, vtype=GRB.BINARY, name="x")

                # Rang buoc moi hang = 1
                for r in range(n):
                    model.addConstr(gp.quicksum(x[r, c] for c in range(n)) == 1, name=f"row_{r}")
                    num_clauses += 1

                # Rang buoc moi cot = 1
                for c in range(n):
                    model.addConstr(gp.quicksum(x[r, c] for r in range(n)) == 1, name=f"col_{c}")
                    num_clauses += 1

                # Rang buoc duong cheo chinh <= 1
                for k in range(-(n - 2), n - 1):
                    diag = [x[r, r - k] for r in range(n) if 0 <= r - k < n]
                    if len(diag) >= 2:
                        model.addConstr(gp.quicksum(diag) <= 1, name=f"d1_{k}")
                        num_clauses += 1

                # Rang buoc duong cheo phu <= 1
                for k in range(1, 2 * n - 2):
                    anti = [x[r, k - r] for r in range(n) if 0 <= k - r < n]
                    if len(anti) >= 2:
                        model.addConstr(gp.quicksum(anti) <= 1, name=f"d2_{k}")
                        num_clauses += 1

                for (fr, fc) in instance.fixed_queens:
                    model.addConstr(x[fr, fc] == 1, name=f"fix_{fr}_{fc}")
                    num_clauses += 1

                t_encode = time.perf_counter() - t0_enc

                t0_solve = time.perf_counter()
                model.optimize()
                t_solve = time.perf_counter() - t0_solve

                if model.status in (GRB.OPTIMAL, GRB.SUBOPTIMAL):
                    status = "SAT"
                    sol_cols = [-1] * n
                    for r in range(n):
                        for c in range(n):
                            if x[r, c].X > 0.5:
                                sol_cols[r] = c
                                break
                    solution = sol_cols
                    is_valid, msg = verify_nqueens_solution(n, solution, instance.fixed_queens)
                    if not is_valid:
                        error_msg = f"Kiem tra nghiem that bai: {msg}"
                elif model.status == GRB.INFEASIBLE:
                    status = "UNSAT"
                    is_valid = True
                elif model.status == GRB.TIME_LIMIT:
                    status = "TIMEOUT"

        except gp.GurobiError as ge:
            t_encode = time.perf_counter() - t0_enc
            if "size-limited license" in str(ge).lower():
                status = "LIC_LIMIT"
                error_msg = f"Gurobi vuot gioi han license: {ge}"
            else:
                status = "ERROR"
                error_msg = str(ge)
        except Exception as e:
            t_encode = time.perf_counter() - t0_enc
            status = "ERROR"
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

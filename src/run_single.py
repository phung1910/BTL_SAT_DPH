import json
import argparse
from src.instances import generate_v1, generate_v2, generate_v3
from src.solvers.pysat_solver import PySATSolver
from src.solvers.cpsat_solver import CPSATSolver
from src.solvers.gurobi_solver import GurobiMIPSolver
from src.solvers.cplex_mip_solver import CPLEXMIPSolver
from src.solvers.cplex_cp_solver import CPLEXCPSolver


def parse_args():
    parser = argparse.ArgumentParser(description="Chay giai mot instance N-Queens")
    parser.add_argument("--solver", type=str, required=True)
    parser.add_argument("--encoding", type=str, default="sequential")
    parser.add_argument("--variant", type=str, default="V1")
    parser.add_argument("--N", type=int, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--k_ratio", type=float, default=0.0)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--alo_col", action="store_true")
    parser.add_argument("--sym_break", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()

    # Khoi tao instance theo bien the
    if args.variant == "V1":
        instance = generate_v1(N=args.N, seed=args.seed)
    elif args.variant == "V2":
        instance = generate_v2(N=args.N, k_ratio=args.k_ratio, seed=args.seed)
    elif args.variant == "V3":
        instance = generate_v3(N=args.N, k_ratio=args.k_ratio, seed=args.seed)
    else:
        raise ValueError(f"Khong ro bien the: {args.variant}")

    # Khoi tao solver tuong ung
    solver_name = args.solver.lower()
    if solver_name in ["cadical153", "glucose4", "minisat22", "maplechrono"]:
        solver = PySATSolver(solver_name=solver_name, amo_method=args.encoding)
    elif solver_name.startswith("cpsat"):
        mtype = "integer" if "integer" in solver_name else "boolean"
        solver = CPSATSolver(model_type=mtype)
    elif solver_name == "gurobi":
        solver = GurobiMIPSolver()
    elif solver_name == "cplex_mip":
        solver = CPLEXMIPSolver()
    elif solver_name == "cplex_cp":
        solver = CPLEXCPSolver()
    else:
        raise ValueError(f"Khong ro solver: {solver_name}")

    res = solver.solve(
        instance=instance,
        time_limit=args.timeout,
        alo_column=args.alo_col,
        symmetry_breaking=args.sym_break
    )

    # In ket qua JSON ra stdout de tien trinh cha doc
    print("---RESULT_START---")
    print(json.dumps(res.to_dict()))
    print("---RESULT_END---")


if __name__ == "__main__":
    main()

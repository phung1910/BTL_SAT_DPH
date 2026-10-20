import os
import sys
import json
import time
import argparse
import subprocess
import pandas as pd
from typing import List, Dict, Any

DEFAULT_TIMEOUT = 600.0
PENALTY_FACTOR = 2.0  # PAR-2: gap 2 lan timeout cho cac truong hop TO/MO/Error
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "raw")


def run_instance_subprocess(
    solver: str,
    encoding: str,
    variant: str,
    N: int,
    seed: int = 0,
    k_ratio: float = 0.0,
    timeout: float = DEFAULT_TIMEOUT,
    alo_col: bool = False,
    sym_break: bool = False
) -> Dict[str, Any]:
    cmd = [
        sys.executable,
        "-m", "src.run_single",
        "--solver", solver,
        "--encoding", encoding,
        "--variant", variant,
        "--N", str(N),
        "--seed", str(seed),
        "--k_ratio", str(k_ratio),
        "--timeout", str(timeout)
    ]
    if alo_col:
        cmd.append("--alo_col")
    if sym_break:
        cmd.append("--sym_break")

    t0 = time.perf_counter()
    status = "UNKNOWN"
    t_solve = 0.0
    t_encode = 0.0
    mem_peak_mb = 0.0
    num_vars = 0
    num_clauses = 0
    is_valid = False
    error_msg = ""
    instance_id = f"{variant}_N{N}_s{seed}"

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 10.0
        )
        wall_time = time.perf_counter() - t0

        if proc.returncode == 0:
            stdout = proc.stdout
            if "---RESULT_START---" in stdout and "---RESULT_END---" in stdout:
                json_str = stdout.split("---RESULT_START---")[1].split("---RESULT_END---")[0].strip()
                res = json.loads(json_str)
                return _compute_par2(res, timeout)
            else:
                status = "ERROR"
                error_msg = f"Khong parse duoc stdout: {stdout[:200]}"
                t_solve = wall_time
        else:
            status = "CRASH"
            error_msg = f"Subprocess exit code {proc.returncode}: {proc.stderr[:200]}"
            t_solve = wall_time

    except subprocess.TimeoutExpired:
        status = "TIMEOUT"
        t_solve = timeout
        error_msg = "Qua thoi gian timeout"
    except Exception as e:
        status = "ERROR"
        error_msg = str(e)
        t_solve = time.perf_counter() - t0

    res = {
        "instance_id": instance_id,
        "solver_name": solver,
        "encoding": encoding,
        "N": N,
        "status": status,
        "t_encode": t_encode,
        "t_solve": t_solve,
        "mem_peak_mb": mem_peak_mb,
        "num_vars": num_vars,
        "num_clauses": num_clauses,
        "is_valid": is_valid,
        "error_msg": error_msg
    }
    return _compute_par2(res, timeout)


def _compute_par2(res: Dict[str, Any], timeout: float) -> Dict[str, Any]:
    # Tinh diem PAR-2
    status = res.get("status", "UNKNOWN")
    t_solve = res.get("t_solve", 0.0)

    if status in ("SAT", "UNSAT"):
        res["par2"] = t_solve
    else:
        res["par2"] = PENALTY_FACTOR * timeout
    return res


def load_existing_results(csv_path: str) -> pd.DataFrame:
    # Doc lai ket qua cu de resume neu bi ngat
    if os.path.exists(csv_path):
        try:
            return pd.read_csv(csv_path)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def is_already_run(df: pd.DataFrame, solver: str, encoding: str, N: int, instance_id: str) -> bool:
    if df.empty:
        return False
    cond = (
        (df["solver_name"] == solver) &
        (df["encoding"] == encoding) &
        (df["N"] == N) &
        (df["instance_id"] == instance_id)
    )
    return not df[cond].empty


def append_result(csv_path: str, res: Dict[str, Any]):
    df_row = pd.DataFrame([res])
    header = not os.path.exists(csv_path)
    df_row.to_csv(csv_path, mode="a", header=header, index=False)


# =========================================================================
# CAC THUC NGHIEM (E1 - E5)
# =========================================================================

def run_experiment_e1(timeout: float, n_list: List[int]):
    print(">>> Chay E1: So sanh 7 ky thuat ma hoa AMO tren CaDiCaL 153")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, "E1_encodings.csv")
    df_existing = load_existing_results(csv_path)

    encodings = ["pairwise", "sequential", "bitwise", "ladder", "totalizer", "commander", "product"]
    solver = "cadical153"

    for N in n_list:
        for enc in encodings:
            # Pairwise va totalizer voi N > 300 sinh so menh de qua lon de tran bo nho
            if enc in ("pairwise", "totalizer") and N > 300:
                print(f"[E1] Bo qua {enc} o N={N} de tranh tran RAM")
                continue

            inst_id = f"V1_N{N}_s0"
            if is_already_run(df_existing, solver, enc, N, inst_id):
                print(f"[E1] Da co ket qua: N={N}, enc={enc}")
                continue

            print(f"[E1] N={N:4d} | enc={enc:10s} ... ", end="", flush=True)
            res = run_instance_subprocess(
                solver=solver, encoding=enc, variant="V1", N=N, seed=0, timeout=timeout
            )
            append_result(csv_path, res)
            print(f"{res['status']} | time={res['t_solve']:.4f}s | vars={res['num_vars']} | clauses={res['num_clauses']}")


def run_experiment_e2(timeout: float, n_list: List[int], best_enc: str = "commander"):
    print(f">>> Chay E2: So sanh cac SAT Solvers (Encoding: {best_enc})")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, "E2_sat_solvers.csv")
    df_existing = load_existing_results(csv_path)

    solvers = ["cadical153", "glucose4", "minisat22", "maplechrono"]

    for N in n_list:
        for s in solvers:
            inst_id = f"V1_N{N}_s0"
            if is_already_run(df_existing, s, best_enc, N, inst_id):
                print(f"[E2] Da co ket qua: N={N}, solver={s}")
                continue

            print(f"[E2] N={N:4d} | solver={s:12s} ... ", end="", flush=True)
            res = run_instance_subprocess(
                solver=s, encoding=best_enc, variant="V1", N=N, seed=0, timeout=timeout
            )
            append_result(csv_path, res)
            print(f"{res['status']} | time={res['t_solve']:.4f}s | PAR2={res['par2']:.2f}")


def run_experiment_e3(timeout: float, n_list: List[int], best_sat_enc: str = "commander"):
    print(">>> Chay E3: So sanh SAT vs CP vs MIP")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, "E3_sat_vs_cp_mip.csv")
    df_existing = load_existing_results(csv_path)

    configs = [
        ("cadical153", best_sat_enc),
        ("cpsat_integer", "integer"),
        ("cpsat_boolean", "boolean"),
        ("gurobi", "binary_mip"),
        ("cplex_mip", "binary_mip"),
        ("cplex_cp", "cpo_all_diff"),
    ]

    for N in n_list:
        for (solver, enc) in configs:
            inst_id = f"V1_N{N}_s0"
            if is_already_run(df_existing, solver, enc, N, inst_id):
                print(f"[E3] Da co ket qua: N={N}, solver={solver}")
                continue

            print(f"[E3] N={N:4d} | solver={solver:14s} ... ", end="", flush=True)
            res = run_instance_subprocess(
                solver=solver, encoding=enc, variant="V1", N=N, seed=0, timeout=timeout
            )
            append_result(csv_path, res)
            print(f"{res['status']} | time={res['t_solve']:.4f}s | PAR2={res['par2']:.2f}")


def run_experiment_e4(timeout: float, n_list: List[int], best_solver: str = "cadical153", best_enc: str = "commander"):
    print(">>> Chay E4: Bien the V2 (Partial SAT) va V3 (Partial Random)")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, "E4_variants.csv")
    df_existing = load_existing_results(csv_path)

    k_ratios = [0.05, 0.10, 0.20]
    num_seeds = 5

    for variant in ["V2", "V3"]:
        for N in n_list:
            for k in k_ratios:
                for seed in range(num_seeds):
                    inst_id = f"{variant}_N{N}_k{int(round(k*100))}pct_s{seed}"
                    if is_already_run(df_existing, best_solver, best_enc, N, inst_id):
                        continue

                    print(f"[E4] {inst_id} ... ", end="", flush=True)
                    res = run_instance_subprocess(
                        solver=best_solver,
                        encoding=best_enc,
                        variant=variant,
                        N=N,
                        seed=seed,
                        k_ratio=k,
                        timeout=timeout
                    )
                    append_result(csv_path, res)
                    print(f"{res['status']} | time={res['t_solve']:.4f}s")


def run_experiment_e5(timeout: float, n_list: List[int], solver: str = "cadical153", enc: str = "commander"):
    print(">>> Chay E5: Ablation Studies (ALO tren cot va Symmetry Breaking)")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, "E5_ablation.csv")

    modes = [
        ("baseline", False, False),
        ("alo_column", True, False),
        ("sym_breaking", False, True),
        ("both", True, True),
    ]

    for N in n_list:
        for (mode_name, alo_col, sym_break) in modes:
            print(f"[E5] N={N:4d} | mode={mode_name:13s} ... ", end="", flush=True)
            res = run_instance_subprocess(
                solver=solver,
                encoding=enc,
                variant="V1",
                N=N,
                seed=0,
                timeout=timeout,
                alo_col=alo_col,
                sym_break=sym_break
            )
            res["ablation_mode"] = mode_name
            append_result(csv_path, res)
            print(f"{res['status']} | time={res['t_solve']:.4f}s | clauses={res['num_clauses']}")


def main():
    parser = argparse.ArgumentParser(description="Chay thuc nghiem benchmark N-Queens")
    parser.add_argument("--exp", type=str, default="E1", choices=["E1", "E2", "E3", "E4", "E5", "ALL"])
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--n_list", type=str, default="8,16,32,64,100,200,300,500")
    args = parser.parse_args()

    n_list = [int(x.strip()) for x in args.n_list.split(",") if x.strip()]

    if args.exp in ("E1", "ALL"):
        run_experiment_e1(args.timeout, n_list)
    if args.exp in ("E2", "ALL"):
        run_experiment_e2(args.timeout, n_list)
    if args.exp in ("E3", "ALL"):
        run_experiment_e3(args.timeout, n_list)
    if args.exp in ("E4", "ALL"):
        run_experiment_e4(args.timeout, [n for n in n_list if n <= 200])
    if args.exp in ("E5", "ALL"):
        run_experiment_e5(args.timeout, n_list)


if __name__ == "__main__":
    main()

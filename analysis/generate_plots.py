import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", font="DejaVu Sans", font_scale=1.1)
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "raw")
FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "report", "figures")


def plot_e1_encodings(csv_path: str = None):
    if csv_path is None:
        csv_path = os.path.join(RESULTS_DIR, "E1_encodings.csv")
    if not os.path.exists(csv_path):
        print(f"Khong tim thay file {csv_path}, hay chay E1 truoc.")
        return

    df = pd.read_csv(csv_path)
    os.makedirs(FIG_DIR, exist_ok=True)

    # 1. So luong clause theo N
    plt.figure(figsize=(8, 5))
    ax = sns.lineplot(
        data=df, x="N", y="num_clauses", hue="encoding", marker="o", linewidth=2.0
    )
    ax.set_yscale("log")
    ax.set_xscale("log")
    plt.title("So luong Clause theo ky thuat ma hoa AMO", fontsize=13, pad=12)
    plt.xlabel("Kich thuoc ban co N (log scale)", fontsize=11)
    plt.ylabel("So menh de / Clauses (log scale)", fontsize=11)
    plt.legend(title="Encoding", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "e1_clauses_scaling.png"), dpi=300)
    plt.savefig(os.path.join(FIG_DIR, "e1_clauses_scaling.pdf"))
    plt.close()
    print("Da luu e1_clauses_scaling.[png,pdf]")

    # 2. Thoi gian giai theo N
    plt.figure(figsize=(8, 5))
    ax = sns.lineplot(
        data=df, x="N", y="t_solve", hue="encoding", marker="s", linewidth=2.0
    )
    ax.set_yscale("log")
    plt.title("Thoi gian giai thuc te (CaDiCaL 153)", fontsize=13, pad=12)
    plt.xlabel("Kich thuoc ban co N", fontsize=11)
    plt.ylabel("Thoi gian giai (s, log scale)", fontsize=11)
    plt.legend(title="Encoding", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "e1_runtime_scaling.png"), dpi=300)
    plt.savefig(os.path.join(FIG_DIR, "e1_runtime_scaling.pdf"))
    plt.close()
    print("Da luu e1_runtime_scaling.[png,pdf]")


def plot_e3_cactus(csv_path: str = None):
    if csv_path is None:
        csv_path = os.path.join(RESULTS_DIR, "E3_sat_vs_cp_mip.csv")
    if not os.path.exists(csv_path):
        return

    df = pd.read_csv(csv_path)
    os.makedirs(FIG_DIR, exist_ok=True)

    plt.figure(figsize=(8, 5))
    for solver_name, group in df.groupby("solver_name"):
        solved = group[group["status"].isin(["SAT", "UNSAT"])].sort_values("t_solve")
        if not solved.empty:
            times = solved["t_solve"].tolist()
            indices = list(range(1, len(times) + 1))
            plt.plot(indices, times, marker="o", label=solver_name, linewidth=2)

    plt.yscale("log")
    plt.title("Cactus Plot: So instance giai duoc theo thoi gian", fontsize=13, pad=12)
    plt.xlabel("So luong instance da giai", fontsize=11)
    plt.ylabel("Thoi gian (s, log scale)", fontsize=11)
    plt.legend(title="Solver", loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "e3_cactus_plot.png"), dpi=300)
    plt.savefig(os.path.join(FIG_DIR, "e3_cactus_plot.pdf"))
    plt.close()
    print("Da luu e3_cactus_plot.[png,pdf]")


if __name__ == "__main__":
    plot_e1_encodings()
    plot_e3_cactus()

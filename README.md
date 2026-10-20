# Benchmark N-Queens: SAT Encodings vs CP/MIP

Dự án thực nghiệm giải bài toán N-Queens quy mô lớn bằng SAT Solver (với 7 kỹ thuật mã hóa At-Most-One) và so sánh hiệu năng với các công cụ CP/MIP (OR-Tools CP-SAT, Gurobi, CPLEX).

---

## 1. Cấu trúc thư mục

```text
nqueens-sat/
├── README.md                 # Hướng dẫn cài đặt và sử dụng
├── requirements.txt          # Thư viện phụ thuộc
├── src/
│   ├── verify.py             # Kiểm tra tính đúng đắn của nghiệm
│   ├── encodings.py          # 7 kỹ thuật mã hóa AMO (Pairwise, Sequential, Commander...)
│   ├── instances.py          # Bộ sinh bài toán (V1: chuẩn, V2: partial SAT, V3: partial ngẫu nhiên)
│   ├── cnf_builder.py        # Dựng công thức CNF & xuất file DIMACS
│   ├── run_single.py         # Script chạy giải 1 instance đơn lẻ
│   ├── run_experiments.py    # Điều phối thực nghiệm E1 - E5, lưu file CSV
│   └── solvers/              # Wrapper cho các solver
│       ├── base.py           # BaseSolver & SolverResult
│       ├── pysat_solver.py   # CaDiCaL, Glucose, MiniSat...
│       ├── cpsat_solver.py   # Google OR-Tools CP-SAT
│       ├── gurobi_solver.py  # Gurobi MIP
│       ├── cplex_mip_solver.py # IBM CPLEX MIP
│       ├── cplex_cp_solver.py  # IBM CPLEX CP Optimizer
│       └── kissat_solver.py  # Kissat qua PySAT / WSL
├── results/
│   └── raw/                  # Kết quả chạy thực nghiệm (CSV)
├── analysis/
│   └── generate_plots.py     # Vẽ biểu đồ kết quả
└── report/
    └── figures/              # Biểu đồ xuất ra dạng PNG / PDF
```

---

## 2. Cài đặt môi trường

Cần cài đặt Python (khuyến nghị Python 3.10 trở lên):

```bash
pip install -r requirements.txt
```

Các thư viện chính được sử dụng:
- `python-sat`: Thư viện SAT solver (CaDiCaL, Glucose, MiniSat...)
- `ortools`: Google CP-SAT solver
- `gurobipy`: Gurobi Optimizer
- `docplex`: IBM CPLEX (MIP & CP)
- `pandas`, `matplotlib`, `seaborn`: Xử lý số liệu và vẽ đồ thị

---

## 3. Cách chạy thực nghiệm

### Chạy thử một instance đơn lẻ
```bash
python -m src.run_single --solver cadical153 --encoding commander --variant V1 --N 100 --timeout 600
```

### Chạy các bài thực nghiệm (E1 - E5)

1. **E1: So sánh 7 kỹ thuật mã hóa AMO**
   ```bash
   python -m src.run_experiments --exp E1 --n_list 8,16,32,64,100,200,300,500 --timeout 600
   ```
   *(Với N > 300, Pairwise và Totalizer được tự động bỏ qua để tránh tràn bộ nhớ).*

2. **E2: So sánh các SAT Solver (trên encoding tốt nhất)**
   ```bash
   python -m src.run_experiments --exp E2 --n_list 8,16,32,64,100,200,300,500 --timeout 600
   ```

3. **E3: So sánh SAT vs CP vs MIP**
   ```bash
   python -m src.run_experiments --exp E3 --n_list 8,16,32,64,100,200,300,500 --timeout 600
   ```

4. **E4: Thử nghiệm với bài toán có đặt sẵn quân hậu (V2 & V3)**
   ```bash
   python -m src.run_experiments --exp E4 --n_list 32,64,100,200 --timeout 600
   ```

5. **E5: Ablation study (thêm ALO trên cột, phá vỡ tính đối xứng)**
   ```bash
   python -m src.run_experiments --exp E5 --n_list 32,64,100,200 --timeout 600
   ```

---

## 4. Vẽ biểu đồ kết quả

Sau khi các thực nghiệm lưu kết quả vào thư mục `results/raw/`, chạy script sau để vẽ đồ thị:

```bash
python -m analysis.generate_plots
```

Các hình vẽ sẽ được lưu vào thư mục `report/figures/`.

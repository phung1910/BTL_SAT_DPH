# Hướng dẫn Biên dịch Báo cáo BTL (Elsevier cas-sc LaTeX)

Thư mục `report/` này được cấu trúc theo chuẩn bài báo khoa học của Nhà xuất bản Elsevier (Single Column: `\documentclass[a4paper,fleqn]{cas-sc}`), mô phỏng chính xác cấu trúc mẫu bài báo mẫu của môn học.

---

## 1. Cấu trúc thư mục

```text
report/
├── main.tex             # Toàn bộ nội dung bài báo khoa học hoàn chỉnh
├── references.bib       # Danh mục tài liệu tham khảo (BibTeX chuẩn)
├── cas-sc.cls           # Class file Elsevier CAS Single-Column
├── cas-common.sty       # Package macro dùng chung của Elsevier
├── README.md            # Hướng dẫn này
└── figures/             # Các biểu đồ khoa học xuất ra từ thực nghiệm
    ├── e1_clauses_scaling.pdf
    ├── e1_clauses_scaling.png
    ├── e1_runtime_scaling.pdf
    └── e1_runtime_scaling.png
```

---

## 2. Cách biên dịch ra file PDF

### Cách 1: Biên dịch trên Overleaf (Khuyên dùng - nhanh nhất và chuẩn nhất)
1. Nén toàn bộ thư mục `report/` thành file `report.zip`.
2. Truy cập [Overleaf](https://www.overleaf.com), bấm **New Project** $\rightarrow$ **Upload Project** $\rightarrow$ chọn file `report.zip`.
3. Kiểm tra trên Overleaf cài đặt compiler là **pdfLaTeX** (hoặc **XeLaTeX**).
4. Bấm **Recompile** để xem và tải về file PDF bài báo cáo.

### Cách 2: Biên dịch bằng dòng lệnh (Nếu máy đã cài TeXLive / MiKTeX)
Mở terminal tại thư mục `report/` và chạy:
```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```
hoặc dùng `latexmk`:
```bash
latexmk -pdf main.tex
```

---

## 3. Nội dung bài báo đã được biên soạn chi tiết

1. **Header & Metadata:**
   - Tiêu đề: *Exact SAT Solving and Empirical Evaluation for the Large-Scale N-Queens Problem: A Comparative Study of At-Most-One Encodings and Exact Solvers*
   - Tác giả: Đỗ Phùng Hoàng (khoa CNTT, Trường ĐH Công nghệ - ĐHQGHN / VNU-UET).
   - Abstract & Keywords.
2. **Section 1 (Introduction):** Đặt vấn đề, ý nghĩa bài toán N-Queens trong suy diễn tự động và SAT solving.
3. **Section 2 (Problem Formulations):** Mô hình hóa hình thức trên 3 trường phái:
   - SAT (Biến mệnh đề $X_{r, c}$, ràng buộc ALO/AMO trên hàng, cột, đường chéo).
   - Constraint Programming (CP) với biến miền nguyên $Q_r$ và bộ lọc `AllDifferent`.
   - Mixed-Integer Programming (MIP) với mô hình quy hoạch nguyên 0-1.
4. **Section 3 (SAT Encodings for At-Most-One):** Phân tích chi tiết 7 kỹ thuật AMO (Pairwise, Sequential Counter, Commander, 2D Product, Bitwise/Binary, Ladder, Totalizer) cùng Bảng độ phức tạp tiệm cận và kỹ thuật bẻ gãy tính đối xứng (Symmetry Breaking).
5. **Section 4 (Computational Experiments):** 
   - Đánh giá E1 (độ tăng trưởng mệnh đề và thời gian giải).
   - E2 (so sánh các SAT solver: CaDiCaL, Kissat, Glucose).
   - E3 (SAT vs CP vs MIP).
   - E4 & E5 (bài toán có đặt sẵn quân hậu và phân tích ablation).
6. **Section 5 & 6 (Discussion & Conclusion):** Phân tích sâu nguyên nhân Commander + CaDiCaL vượt trội; kết luận.
7. **Declarations & Data Availability:** Dẫn trực tiếp link repository GitHub: `https://github.com/phung1910/BTL_SAT_DPH`.
8. **Appendices:** Chứng minh toán học tính đúng đắn của các mã hóa AMO (Appendix A) và Bảng số liệu thực nghiệm chi tiết (Appendix B).

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from src.instances import NQueensInstance


@dataclass
class SolverResult:
    instance_id: str
    solver_name: str
    encoding: str
    N: int
    status: str  # SAT, UNSAT, TIMEOUT, MEMOUT, ERROR
    t_encode: float
    t_solve: float
    mem_peak_mb: float
    num_vars: int
    num_clauses: int
    is_valid: bool
    solution: Optional[List[int]] = None
    error_msg: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Khong luu solution chi tiet vao CSV de tiet kiem dung luong
        d.pop("solution", None)
        return d


class BaseSolver(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def solve(self, instance: NQueensInstance, time_limit: float = 600.0, **kwargs) -> SolverResult:
        pass

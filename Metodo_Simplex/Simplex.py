import numpy as np
from fractions import Fraction

# Tolerancia para lidiar con errores de punto flotante
TOL = 1e-8

def to_frac(val):
    """Convierte un valor flotante a su representación en fracción tipo string."""
    if abs(val) < TOL: return "0"
    if abs(val - int(round(val))) < TOL: return str(int(round(val)))
    f = Fraction(val).limit_denominator(10000)
    if f.denominator == 1: return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"

class SimplexSolver:
    """Motor matemático del método Simplex (1 y 2 fases)."""
    def __init__(self, c, A, b, ops, maximize=True):
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.ops = ops
        self.maximize = maximize
        self.m, self.n = self.A.shape
        self.history = [] 
        self.solution = None
        self.optimal_value = None
        
        self.var_names = [f"x{i+1}" for i in range(self.n)]
        self.basis = []
        self.has_phase1 = False

    def _build_initial_tableau(self):
        num_h = sum(1 for op in self.ops if op == "<=")
        num_e = sum(1 for op in self.ops if op == ">=")
        num_a = sum(1 for op in self.ops if op in [">=", "="])
        
        if num_a > 0:
            self.has_phase1 = True

        total_vars = self.n + num_h + num_e + num_a
        self.tableau = np.zeros((self.m + 1, total_vars + 1))
        
        col_idx = self.n
        h_idx, e_idx, a_idx = 1, 1, 1
        
        for i, op in enumerate(self.ops):
            self.tableau[i, :self.n] = self.A[i]
            self.tableau[i, -1] = self.b[i]
            
            if op == "<=":
                self.tableau[i, col_idx] = 1
                self.var_names.append(f"h{h_idx}")
                self.basis.append(f"h{h_idx}")
                col_idx += 1
                h_idx += 1
            elif op == ">=":
                self.tableau[i, col_idx] = -1
                self.var_names.append(f"e{e_idx}")
                col_idx += 1
                e_idx += 1
                
                self.tableau[i, col_idx] = 1
                self.var_names.append(f"a{a_idx}")
                self.basis.append(f"a{a_idx}")
                col_idx += 1
                a_idx += 1
            elif op == "=":
                self.tableau[i, col_idx] = 1
                self.var_names.append(f"a{a_idx}")
                self.basis.append(f"a{a_idx}")
                col_idx += 1
                a_idx += 1

    def _setup_phase1(self):
        for i in range(self.m):
            if self.basis[i].startswith('a'):
                self.tableau[-1] -= self.tableau[i]
        self.history.append({
            'title': "Tabla Inicial (Fase 1)",
            'tableau': self.tableau.copy(),
            'basis': list(self.basis),
            'ratios': None,
            'vars': list(self.var_names),
            'msg': "Se seleccionan las variables de holgura y artificiales como base inicial."
        })

    def _setup_phase2(self):
        a_indices = [i for i, name in enumerate(self.var_names) if name.startswith('a')]
        self.tableau = np.delete(self.tableau, a_indices, axis=1)
        self.var_names = [name for name in self.var_names if not name.startswith('a')]
        
        c = self.c if self.maximize else -self.c
        self.tableau[-1, :] = 0
        self.tableau[-1, :self.n] = -c
        
        for i in range(self.m):
            if self.basis[i] in self.var_names:
                col_idx = self.var_names.index(self.basis[i])
                factor = self.tableau[-1, col_idx]
                self.tableau[-1] -= factor * self.tableau[i]
                
        self.history.append({
            'title': "Tabla Inicial (Fase 2)",
            'tableau': self.tableau.copy(),
            'basis': list(self.basis),
            'ratios': None,
            'vars': list(self.var_names),
            'msg': "Se eliminan las columnas artificiales y se restablece la función objetivo original."
        })

    def _pivot(self, pivot_row, pivot_col):
        pivot_val = self.tableau[pivot_row, pivot_col]
        self.tableau[pivot_row] /= pivot_val
        for i in range(self.m + 1):
            if i != pivot_row:
                self.tableau[i] -= self.tableau[i, pivot_col] * self.tableau[pivot_row]
        self.tableau[np.abs(self.tableau) < TOL] = 0.0
        self.basis[pivot_row] = self.var_names[pivot_col]

    def _run_simplex_loop(self, phase_name):
        iteration = 1
        while True:
            last_row = self.tableau[self.m, :-1]
            min_val = np.min(last_row)
            
            if min_val >= -TOL:
                msg = f"No hay coeficientes negativos en la función objetivo. Fin de la {phase_name}."
                self.history.append({
                    'title': f"Tabla Final ({phase_name})",
                    'tableau': self.tableau.copy(),
                    'basis': list(self.basis),
                    'ratios': None,
                    'vars': list(self.var_names),
                    'msg': msg
                })
                break
                
            entering_col = np.argmin(last_row)
            ratios = []
            ratio_strs = []
            for i in range(self.m):
                if self.tableau[i, entering_col] > TOL:
                    ratio_val = self.tableau[i, -1] / self.tableau[i, entering_col]
                    ratios.append(ratio_val)
                    num_str = to_frac(self.tableau[i, -1])
                    den_str = to_frac(self.tableau[i, entering_col])
                    res_str = to_frac(ratio_val)
                    ratio_strs.append(f"{res_str}" if den_str == "1" else f"{num_str}/{den_str} = {res_str}")
                else:
                    ratios.append(np.inf)
                    ratio_strs.append("")
            
            if all(r == np.inf for r in ratios):
                return False, "El problema no está acotado."
                
            leaving_row = np.argmin(ratios)
            ratio_strs[leaving_row] += " <- Mínimo"
            
            msg = ("Se divide la fila pivote por el valor pivote y se aplica reducción gaussiana.")
            self.history.append({
                'title': f"Iteración {iteration} ({phase_name})",
                'tableau': self.tableau.copy(),
                'basis': list(self.basis),
                'ratios': ratio_strs,
                'vars': list(self.var_names),
                'msg': msg
            })
            
            self._pivot(leaving_row, entering_col)
            iteration += 1
        return True, ""

    def solve(self):
        self._build_initial_tableau()
        
        if self.has_phase1:
            self._setup_phase1()
            success, msg = self._run_simplex_loop("Fase 1")
            if not success: return False, msg
            
            if abs(self.tableau[-1, -1]) > TOL:
                return False, "El problema no tiene solución factible (Z de Fase 1 > 0)."
                
            self._setup_phase2()
            success, msg = self._run_simplex_loop("Fase 2")
            if not success: return False, msg
        else:
            c = self.c if self.maximize else -self.c
            self.tableau[-1, :self.n] = -c
            
            self.history.append({
                'title': "Tabla Inicial",
                'tableau': self.tableau.copy(),
                'basis': list(self.basis),
                'ratios': None,
                'vars': list(self.var_names),
                'msg': "Configuración inicial."
            })
            success, msg = self._run_simplex_loop("Simplex")
            if not success: return False, msg
            
        self._extract_solution()
        return True, "Solución óptima encontrada."

    def _extract_solution(self):
        self.solution = np.zeros(self.n)
        for i in range(self.m):
            if self.basis[i].startswith('x'):
                var_idx = int(self.basis[i][1:]) - 1
                self.solution[var_idx] = self.tableau[i, -1]
        self.optimal_value = self.tableau[self.m, -1]
        if not self.maximize:
            self.optimal_value = -self.optimal_value
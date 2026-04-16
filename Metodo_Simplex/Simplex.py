"""
Método Simplex para resolver problemas de Programación Lineal.

Forma estándar:
    Maximizar: Z = c1*x1 + c2*x2 + ... + cn*xn
    Sujeto a:  a11*x1 + a12*x2 + ... + a1n*xn <= b1
               a21*x1 + a22*x2 + ... + a2n*xn <= b2
               ...
               am1*x1 + am2*x2 + ... + amn*xn <= bm
               xi >= 0
"""

from typing import List, Tuple
import numpy as np


class SimplexSolver:
    """Resuelve problemas de programación lineal usando el método Simplex."""

    def __init__(self, c: List[float], A: List[List[float]], b: List[float], maximize: bool = True):
        """
        Inicializa el problema de programación lineal.

        Args:
            c: Coeficientes de la función objetivo [c1, c2, ..., cn]
            A: Matriz de coeficientes de restricciones (m x n)
            b: Vector de términos independientes [b1, b2, ..., bm]
            maximize: True para maximizar, False para minimizar
        """
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.maximize = maximize
        
        self.m, self.n = self.A.shape  # m restricciones, n variables
        self.tableau = None
        self.solution = None
        self.optimal_value = None

    def _build_tableau(self) -> None:
        """Construye la tabla inicial del Simplex con variables de holgura."""
        # Si minimizamos, convertir a maximización multiplicando por -1
        c = self.c if self.maximize else -self.c
        self.tableau = np.zeros((self.m + 1, self.n + self.m + 1))
        self.tableau[:self.m, :self.n] = self.A
        self.tableau[:self.m, self.n:self.n + self.m] = np.eye(self.m)
        self.tableau[:self.m, -1] = self.b
        self.tableau[self.m, :self.n] = -c
        self.tableau[self.m, self.n:self.n + self.m] = 0

    def _pivot(self, pivot_row: int, pivot_col: int) -> None:
        """Realiza la operación de pivote en la tabla."""
        self.tableau[pivot_row] /= self.tableau[pivot_row, pivot_col]
        for i in range(self.m + 1):
            if i != pivot_row:
                self.tableau[i] -= self.tableau[i, pivot_col] * self.tableau[pivot_row]

    def _find_entering_variable(self) -> int | None:
        """Selecciona variable entrante: mínimo en fila objetivo con tolerancia numérica."""
        last_row = self.tableau[self.m, :-1]
        min_val = np.min(last_row)
        if min_val >= -1e-10:
            return None
        return np.argmin(last_row)

    def _find_leaving_variable(self, entering_col: int) -> int | None:
        """Selecciona variable saliente mediante test de mínima razón."""
        ratios = []
        for i in range(self.m):
            if self.tableau[i, entering_col] > 1e-10:
                ratios.append(self.tableau[i, -1] / self.tableau[i, entering_col])
            else:
                ratios.append(np.inf)
        if all(r == np.inf for r in ratios):
            return None
        return np.argmin(ratios)

    def solve(self, max_iterations: int = 1000) -> Tuple[bool, List[float], float]:
        """
        Resuelve el problema usando Simplex.

        Returns:
            (éxito, solución, valor óptimo)
        """
        self._build_tableau()
        iteration = 0
        while iteration < max_iterations:
            entering_col = self._find_entering_variable()
            if entering_col is None:
                break
            leaving_row = self._find_leaving_variable(entering_col)
            if leaving_row is None:
                return False, [], np.inf
            self._pivot(leaving_row, entering_col)
            iteration += 1
        self.solution = np.zeros(self.n)
        for i in range(self.n):
            col = self.tableau[:self.m, i]
            if np.sum(np.abs(col - np.round(col))) < 1e-10:
                unit_row = np.argmax(np.abs(col))
                if abs(col[unit_row] - 1.0) < 1e-10:
                    self.solution[i] = self.tableau[unit_row, -1]
        self.optimal_value = self.tableau[self.m, -1]
        if not self.maximize:
            self.optimal_value = -self.optimal_value
        return True, list(self.solution), self.optimal_value

    def print_solution(self) -> None:
        """Imprime la solución en formato legible."""
        if self.solution is None:
            print("Problema no resuelto aún.")
            return

        var_names = ['x', 'y']
        print("\n" + "=" * 50)
        print("SOLUCIÓN DEL SIMPLEX")
        print("=" * 50)
        for i, val in enumerate(self.solution[:2]):
            print(f"{var_names[i]} = {val:.6f}")
        print(f"\nValor óptimo (Z): {self.optimal_value:.6f}")
        print("=" * 50 + "\n")


def input_problem() -> Tuple[List[float], List[List[float]], List[float], bool]:
    """
    Solicita al usuario los datos del problema de programación lineal (2 variables: x, y).

    Returns:
        (c, A, b, maximize)
    """
    print("\n" + "=" * 60)
    print("INGRESO DE DATOS - MÉTODO SIMPLEX (2 variables: x, y)")
    print("=" * 60)

    # Tipo de optimización
    while True:
        opt_type = input("\n¿Deseas maximizar (M) o minimizar (m) ? [M/m]: ").strip().upper()
        if opt_type in ['M', 'MAXIMIZAR']:
            maximize = True
            break
        elif opt_type in ['m', 'MINIMIZAR']:
            maximize = False
            break
        else:
            print("Entrada inválida. Ingresa 'M' para maximizar o 'm' para minimizar.")

    while True:
        try:
            n_constraints = int(input("\n¿Cuántas restricciones tiene el problema? "))
            if n_constraints > 0:
                break
            print("El número debe ser mayor a 0.")
        except ValueError:
            print("Ingresa un número entero válido.")

    print("\nIngresa los coeficientes de la función objetivo Z = a*x + b*y:")
    c = []
    var_names = ['x', 'y']
    for i in range(2):
        while True:
            try:
                coef = float(input(f"  Coeficiente de {var_names[i]}: "))
                c.append(coef)
                break
            except ValueError:
                print("Ingresa un número válido (entero o decimal, usa . como separador).")

    print(f"\nIngresa los coeficientes de las restricciones (forma: a*x + b*y <= c):")
    A = []
    b = []

    for i in range(n_constraints):
        print(f"\nRestricción {i+1}:")
        constraint_row = []
        for j in range(2):
            while True:
                try:
                    coef = float(input(f"  Coeficiente de {var_names[j]}: "))
                    constraint_row.append(coef)
                    break
                except ValueError:
                    print("Ingresa un número válido.")

        while True:
            try:
                term = float(input(f"  Término independiente (lado derecho): "))
                b.append(term)
                break
            except ValueError:
                print("Ingresa un número válido.")

        A.append(constraint_row)

    return c, A, b, maximize


def display_problem(c: List[float], A: List[List[float]], b: List[float], maximize: bool) -> None:
    """Formatea y muestra el problema ingresado en notación estándar."""
    print("\n" + "=" * 60)
    print("PROBLEMA INGRESADO")
    print("=" * 60)

    opt_str = "Maximizar" if maximize else "Minimizar"
    c_str = f"{c[0]:.2f}*x"
    if c[1] >= 0:
        c_str += f" + {c[1]:.2f}*y"
    else:
        c_str += f" - {abs(c[1]):.2f}*y"
    
    print(f"\n{opt_str}:")
    print(f"  Z = {c_str}")

    print("\nSujeto a:")
    for i, row in enumerate(A):
        row_str = f"{row[0]:.2f}*x"
        if row[1] >= 0:
            row_str += f" + {row[1]:.2f}*y"
        else:
            row_str += f" - {abs(row[1]):.2f}*y"
        print(f"  {row_str} <= {b[i]:.2f}")
    print(f"  x, y >= 0")
    print("=" * 60)


if __name__ == "__main__":
    try:
        # Solicitar datos del usuario
        c, A, b, maximize = input_problem()

        # Mostrar resumen del problema
        display_problem(c, A, b, maximize)

        # Resolver
        print("\nResolviendo problema...")
        solver = SimplexSolver(c, A, b, maximize=maximize)
        success, solution, opt_val = solver.solve()

        if success:
            solver.print_solution()
        else:
            print("\n❌ No se pudo encontrar solución óptima.")
            print("   El problema podría estar no acotado o no tener solución factible.")

    except KeyboardInterrupt:
        print("\n\nProceso cancelado por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
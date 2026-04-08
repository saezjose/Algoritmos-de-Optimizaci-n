from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from typing import Iterable, List, Sequence, Tuple

import numpy as np
from scipy.spatial import ConvexHull


Constraint = Tuple[Fraction, Fraction, Fraction]
Point = Tuple[Fraction, Fraction]


def determinant_2x2(a: Fraction, b: Fraction, c: Fraction, d: Fraction) -> Fraction:
    """Calcula el determinante de una matriz 2x2."""
    return a * d - b * c


def to_fraction(value: float | int | str | Fraction) -> Fraction:
    """Convierte un valor numérico a Fraction para mantener precisión racional."""
    if isinstance(value, Fraction):
        return value
    return Fraction(str(value))


def normalize_constraints(matrix: Sequence[Sequence[float | int | str]]) -> List[Constraint]:
    """Normaliza una matriz n x 3 a una lista de restricciones (A, B, C)."""
    constraints: List[Constraint] = []
    for row in matrix:
        if len(row) != 3:
            raise ValueError("Cada fila debe tener exactamente 3 valores: A, B, C.")
        a, b, c = (to_fraction(row[0]), to_fraction(row[1]), to_fraction(row[2]))
        constraints.append((a, b, c))
    return constraints


def line_intersection(c1: Constraint, c2: Constraint) -> Point | None:
    """Calcula intersección exacta de dos rectas con regla de Cramer."""
    a1, b1, c1v = c1
    a2, b2, c2v = c2

    d = determinant_2x2(a1, b1, a2, b2)
    if d == 0:
        return None

    dx = determinant_2x2(c1v, b1, c2v, b2)
    dy = determinant_2x2(a1, c1v, a2, c2v)

    x = dx / d
    y = dy / d
    return (x, y)


def axis_intersections(constraint: Constraint) -> List[Point]:
    """Intersecciones de una línea con x=0 y y=0."""
    a, b, c = constraint
    points: List[Point] = []

    if a != 0:
        points.append((c / a, Fraction(0)))
    if b != 0:
        points.append((Fraction(0), c / b))

    return points


def compute_candidate_points(constraints: Sequence[Constraint]) -> List[Point]:
    """Genera candidatos: intersecciones entre líneas + intersecciones con ejes + origen."""
    candidates = {(Fraction(0), Fraction(0))}

    for c1, c2 in combinations(constraints, 2):
        p = line_intersection(c1, c2)
        if p is not None:
            candidates.add(p)

    for c in constraints:
        for p in axis_intersections(c):
            candidates.add(p)

    return list(candidates)


def is_feasible(point: Point, constraints: Sequence[Constraint]) -> bool:
    """Valida si un punto cumple todas las restricciones lineales."""
    x, y = point
    for a, b, c in constraints:
        if a * x + b * y > c:
            return False

    return True


def filter_feasible_vertices(
    candidates: Iterable[Point],
    constraints: Sequence[Constraint],
    enforce_nonnegativity: bool = True,
) -> List[Point]:
    """Filtra candidatos y devuelve vértices factibles únicos."""
    feasible: List[Point] = []
    for p in candidates:
        if enforce_nonnegativity and (p[0] < 0 or p[1] < 0):
            continue
        if is_feasible(p, constraints):
            feasible.append(p)
    return sorted(set(feasible), key=lambda p: (float(p[0]), float(p[1])))


def order_vertices(vertices: Sequence[Point]) -> List[Point]:
    """Ordena vértices para trazar el polígono usando ConvexHull (si aplica)."""
    if len(vertices) <= 2:
        return list(vertices)

    pts = np.array([[float(x), float(y)] for x, y in vertices])
    hull = ConvexHull(pts)
    ordered = [vertices[i] for i in hull.vertices]
    return ordered


def solve_feasible_region(
    matrix: Sequence[Sequence[float | int | str]],
    enforce_nonnegativity: bool = True,
) -> List[Point]:
    """Devuelve la lista de vértices (x, y) que delimitan la región factible."""
    constraints = normalize_constraints(matrix)
    candidates = compute_candidate_points(constraints)
    feasible_vertices = filter_feasible_vertices(
        candidates,
        constraints,
        enforce_nonnegativity=enforce_nonnegativity,
    )
    return order_vertices(feasible_vertices)


def format_vertices(vertices: Sequence[Point]) -> List[Tuple[str, str]]:
    """Formato amigable para imprimir coordenadas exactas racionales."""
    return [(str(x), str(y)) for x, y in vertices]

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from Metodo_Grafico.Matematico import Point, compute_candidate_points, normalize_constraints, order_vertices


@dataclass(frozen=True)
class PlotConfig:
    """Configurable plotting parameters to avoid scattered hardcoded values."""

    feasible_figsize: Tuple[float, float] = (10.0, 7.0)
    dpi: int = 150

    line_samples: int = 300
    constraint_linewidth: float = 1.8
    feasible_fill_color: str = "skyblue"
    feasible_fill_alpha: float = 0.35
    feasible_edge_color: str = "navy"
    feasible_edge_linewidth: float = 2.0
    feasible_vertex_color: str = "red"
    feasible_vertex_size: float = 65.0

    axis_color: str = "black"
    axis_linewidth: float = 1.0
    grid_alpha: float = 0.25

    axis_padding_ratio: float = 0.15
    min_padding: float = 1.0
    negative_origin_ratio: float = 0.35

    feasible_output_name: str = "region_factible.png"


def _compute_axis_limits(points: Sequence[Point], config: PlotConfig) -> Tuple[float, float, float, float]:
    """Compute axis limits with configurable padding and negative-space ratio."""
    all_x = [float(x) for x, _ in points]
    all_y = [float(y) for _, y in points]

    if not all_x:
        all_x = [0.0, 10.0]
    if not all_y:
        all_y = [0.0, 10.0]

    data_x_min, data_x_max = min(all_x), max(all_x)
    data_y_min, data_y_max = min(all_y), max(all_y)

    span_x = max(config.min_padding, data_x_max - data_x_min)
    span_y = max(config.min_padding, data_y_max - data_y_min)
    x_pad = span_x * config.axis_padding_ratio
    y_pad = span_y * config.axis_padding_ratio

    x_min = min(data_x_min - x_pad, -(data_x_max + x_pad) * config.negative_origin_ratio)
    y_min = min(data_y_min - y_pad, -(data_y_max + y_pad) * config.negative_origin_ratio)
    x_max = data_x_max + x_pad
    y_max = data_y_max + y_pad
    return x_min, x_max, y_min, y_max


def plot_feasible_region(
    matrix: Sequence[Sequence[float | int | str]],
    vertices: Sequence[Point],
    constraint_labels: Sequence[str] | None = None,
    output_path: str | None = None,
    config: PlotConfig | None = None,
) -> None:
    """Grafica restricciones, vertices y region factible sombreada."""
    cfg = config or PlotConfig()
    save_path = output_path or cfg.feasible_output_name
    constraints = normalize_constraints(matrix)

    all_points = compute_candidate_points(constraints)
    all_points.extend(vertices)

    x_min, x_max, y_min, y_max = _compute_axis_limits(all_points, cfg)

    fig, ax = plt.subplots(figsize=cfg.feasible_figsize)

    for i, (a, b, c) in enumerate(constraints, start=1):
        if constraint_labels and i - 1 < len(constraint_labels):
            label = f"R{i}: {constraint_labels[i - 1]}"
        else:
            label = f"R{i}: {float(a):g}x + {float(b):g}y <= {float(c):g}"
        if b != 0:
            x_values = np.linspace(x_min, x_max, cfg.line_samples)
            y_values = (float(c) - float(a) * x_values) / float(b)
            ax.plot(x_values, y_values, label=label, linewidth=cfg.constraint_linewidth)
        elif a != 0:
            x_vertical = float(c / a)
            ax.axvline(x=x_vertical, label=label, linewidth=cfg.constraint_linewidth)

    if len(vertices) >= 3:
        hull_ordered = order_vertices(vertices)
        polygon = np.array([[float(x), float(y)] for x, y in hull_ordered])
        closed_polygon = np.vstack([polygon, polygon[0]])

        ax.fill(
            closed_polygon[:, 0],
            closed_polygon[:, 1],
            color=cfg.feasible_fill_color,
            alpha=cfg.feasible_fill_alpha,
            label="Region factible",
        )
        ax.plot(
            closed_polygon[:, 0],
            closed_polygon[:, 1],
            color=cfg.feasible_edge_color,
            linewidth=cfg.feasible_edge_linewidth,
        )

    if vertices:
        vx = [float(x) for x, _ in vertices]
        vy = [float(y) for _, y in vertices]
        ax.scatter(vx, vy, color=cfg.feasible_vertex_color, s=cfg.feasible_vertex_size, zorder=5, label="Vertices validos")

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.axhline(0, color=cfg.axis_color, linewidth=cfg.axis_linewidth)
    ax.axvline(0, color=cfg.axis_color, linewidth=cfg.axis_linewidth)
    ax.grid(alpha=cfg.grid_alpha)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Programacion lineal 2D: region factible")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(save_path, dpi=cfg.dpi)
    plt.close(fig)

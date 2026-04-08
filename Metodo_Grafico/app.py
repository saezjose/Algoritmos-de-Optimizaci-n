from __future__ import annotations

from pathlib import Path
from tkinter import TclError
from tkinter import messagebox

import customtkinter as ctk

from Metodo_Grafico.Matematico import (
    format_vertices,
    solve_feasible_region,
)
from Grafico import plot_feasible_region


def parse_matrix(raw_text: str) -> list[list[float]]:
    """Convierte texto multilinea en matriz n x 3 (A, B, C)."""
    rows: list[list[float]] = []
    for idx, raw_line in enumerate(raw_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        clean = line.replace(",", " ").replace(";", " ")
        parts = [p for p in clean.split() if p]
        if len(parts) != 3:
            raise ValueError(f"Linea {idx}: debes ingresar exactamente 3 valores (A B C).")

        try:
            row = [float(parts[0]), float(parts[1]), float(parts[2])]
        except ValueError as exc:
            raise ValueError(f"Linea {idx}: todos los valores deben ser numericos.") from exc

        rows.append(row)

    if not rows:
        raise ValueError("No hay restricciones para procesar.")

    return rows


class LPApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Programacion Lineal 2D - CustomTkinter")
        self.geometry("950x620")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.output_image = Path("region_factible_gui.png")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_input_panel()
        self._build_output_panel()

    def _build_header(self) -> None:
        title = ctk.CTkLabel(
            self,
            text="Resolucion de Region Factible (2D)",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.grid(row=0, column=0, columnspan=2, padx=18, pady=(16, 8), sticky="w")

    def _build_input_panel(self) -> None:
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, padx=(18, 9), pady=10, sticky="nsew")
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        hint = (
            "Ingresa una restriccion por linea con formato A B C para Ax + By <= C.\n"
            "Tambien puedes usar comas o punto y coma."
        )
        label = ctk.CTkLabel(frame, text=hint, justify="left")
        label.grid(row=0, column=0, padx=14, pady=(14, 8), sticky="w")

        bounds_frame = ctk.CTkFrame(frame)
        bounds_frame.grid(row=1, column=0, padx=14, pady=(0, 8), sticky="ew")
        bounds_frame.grid_columnconfigure(0, weight=0)
        bounds_frame.grid_columnconfigure(1, weight=1)
        bounds_frame.grid_columnconfigure(2, weight=0)
        bounds_frame.grid_columnconfigure(3, weight=1)

        bounds_title = ctk.CTkLabel(
            bounds_frame,
            text="Condiciones de variables (editables)",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        bounds_title.grid(row=0, column=0, columnspan=4, padx=8, pady=(8, 6), sticky="w")

        x_label = ctk.CTkLabel(bounds_frame, text="x >=", width=60, anchor="w")
        x_label.grid(row=1, column=0, padx=(8, 4), pady=(2, 8), sticky="w")
        self.x_lower_entry = ctk.CTkEntry(bounds_frame)
        self.x_lower_entry.grid(row=1, column=1, padx=(4, 8), pady=(2, 8), sticky="ew")
        self.x_lower_entry.insert(0, "0")

        y_label = ctk.CTkLabel(bounds_frame, text="y >=", width=60, anchor="w")
        y_label.grid(row=1, column=2, padx=(8, 4), pady=(2, 8), sticky="w")
        self.y_lower_entry = ctk.CTkEntry(bounds_frame)
        self.y_lower_entry.grid(row=1, column=3, padx=(4, 8), pady=(2, 8), sticky="ew")
        self.y_lower_entry.insert(0, "0")

        objective_frame = ctk.CTkFrame(frame)
        objective_frame.grid(row=2, column=0, padx=14, pady=(0, 8), sticky="ew")
        objective_frame.grid_columnconfigure(0, weight=0)
        objective_frame.grid_columnconfigure(1, weight=1)
        objective_frame.grid_columnconfigure(2, weight=0)
        objective_frame.grid_columnconfigure(3, weight=1)
        objective_frame.grid_columnconfigure(4, weight=0)
        objective_frame.grid_columnconfigure(5, weight=1)
        objective_frame.grid_columnconfigure(6, weight=0)

        objective_title = ctk.CTkLabel(
            objective_frame,
            text="Funcion objetivo",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        objective_title.grid(row=0, column=0, columnspan=7, padx=8, pady=(8, 6), sticky="w")

        self.objective_mode = ctk.StringVar(value="Maximizar")
        mode_menu = ctk.CTkOptionMenu(
            objective_frame,
            values=["Maximizar", "Minimizar"],
            variable=self.objective_mode,
        )
        mode_menu.grid(row=1, column=0, padx=(8, 8), pady=(2, 8), sticky="w")

        self.obj_x_entry = ctk.CTkEntry(objective_frame, placeholder_text="coef x")
        self.obj_x_entry.grid(row=1, column=1, padx=(4, 8), pady=(2, 8), sticky="ew")
        self.obj_x_entry.insert(0, "1")

        plus_label = ctk.CTkLabel(objective_frame, text="x +")
        plus_label.grid(row=1, column=2, padx=(0, 0), pady=(2, 8), sticky="w")

        self.obj_y_entry = ctk.CTkEntry(objective_frame, placeholder_text="coef y")
        self.obj_y_entry.grid(row=1, column=3, padx=(4, 8), pady=(2, 8), sticky="ew")
        self.obj_y_entry.insert(0, "1")

        y_suffix = ctk.CTkLabel(objective_frame, text="y +")
        y_suffix.grid(row=1, column=4, padx=(0, 8), pady=(2, 8), sticky="w")

        self.obj_c_entry = ctk.CTkEntry(objective_frame, placeholder_text="const C")
        self.obj_c_entry.grid(row=1, column=5, padx=(4, 8), pady=(2, 8), sticky="ew")
        self.obj_c_entry.insert(0, "0")

        c_suffix = ctk.CTkLabel(objective_frame, text="(C)")
        c_suffix.grid(row=1, column=6, padx=(0, 8), pady=(2, 8), sticky="w")

        self.matrix_box = ctk.CTkTextbox(frame, width=400)
        self.matrix_box.grid(row=3, column=0, padx=14, pady=8, sticky="nsew")

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, padx=14, pady=(8, 14), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        solve_btn = ctk.CTkButton(btn_frame, text="Resolver y graficar", command=self.solve_and_plot)
        solve_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        clear_btn = ctk.CTkButton(btn_frame, text="Limpiar", command=self.clear_all)
        clear_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def _build_output_panel(self) -> None:
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=1, padx=(9, 18), pady=10, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(frame, text="Vertices factibles", font=ctk.CTkFont(size=18, weight="bold"))
        label.grid(row=0, column=0, padx=14, pady=(14, 8), sticky="w")

        self.vertices_box = ctk.CTkTextbox(frame, width=400)
        self.vertices_box.grid(row=1, column=0, padx=14, pady=8, sticky="nsew")

        self.status_label = ctk.CTkLabel(frame, text="Estado: listo", justify="left")
        self.status_label.grid(row=2, column=0, padx=14, pady=(8, 8), sticky="w")

        self.objective_result_label = ctk.CTkLabel(frame, text="Objetivo: sin calcular", justify="left")
        self.objective_result_label.grid(row=3, column=0, padx=14, pady=(0, 8), sticky="w")

        open_btn = ctk.CTkButton(frame, text="Abrir grafica PNG", command=self.open_image)
        open_btn.grid(row=4, column=0, padx=14, pady=(6, 14), sticky="ew")

    def clear_all(self) -> None:
        self.matrix_box.delete("1.0", "end")
        self.vertices_box.delete("1.0", "end")
        self.x_lower_entry.delete(0, "end")
        self.y_lower_entry.delete(0, "end")
        self.obj_x_entry.delete(0, "end")
        self.obj_y_entry.delete(0, "end")
        self.obj_c_entry.delete(0, "end")
        self.status_label.configure(text="Estado: campos limpiados")
        self.objective_result_label.configure(text="Objetivo: sin calcular")

    @staticmethod
    def _parse_bound(entry_value: str, label: str) -> float:
        value = entry_value.strip()
        if not value:
            raise ValueError(f"Debes ingresar un valor para {label}.")
        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(f"El valor de {label} debe ser numerico.") from exc

    def solve_and_plot(self) -> None:
        raw = self.matrix_box.get("1.0", "end")
        try:
            matrix = parse_matrix(raw)
            x_lower = self._parse_bound(self.x_lower_entry.get(), "x >=")
            y_lower = self._parse_bound(self.y_lower_entry.get(), "y >=")
            obj_x = self._parse_bound(self.obj_x_entry.get(), "coeficiente de x")
            obj_y = self._parse_bound(self.obj_y_entry.get(), "coeficiente de y")
            obj_c = self._parse_bound(self.obj_c_entry.get(), "constante C")
            mode = self.objective_mode.get()

            matrix_with_bounds = list(matrix)
            matrix_with_bounds.append([-1, 0, -x_lower])
            matrix_with_bounds.append([0, -1, -y_lower])

            constraint_labels = [f"{a:g}x + {b:g}y <= {c:g}" for a, b, c in matrix]
            constraint_labels.append(f"x >= {x_lower:g}")
            constraint_labels.append(f"y >= {y_lower:g}")

            vertices = solve_feasible_region(matrix_with_bounds, enforce_nonnegativity=False)
            plot_feasible_region(
                matrix_with_bounds,
                vertices,
                constraint_labels=constraint_labels,
                output_path=str(self.output_image),
            )

            self.vertices_box.delete("1.0", "end")
            if vertices:
                pretty = format_vertices(vertices)
                lines = [f"({x}, {y})" for x, y in pretty]
                self.vertices_box.insert("1.0", "\n".join(lines))

                values = [obj_x * float(x) + obj_y * float(y) + obj_c for x, y in vertices]
                if mode == "Maximizar":
                    best_idx = max(range(len(values)), key=lambda i: values[i])
                else:
                    best_idx = min(range(len(values)), key=lambda i: values[i])

                best_point = vertices[best_idx]
                best_value = values[best_idx]
                self.objective_result_label.configure(
                    text=(
                        f"Objetivo ({mode.lower()}): z = {obj_x:g}x + {obj_y:g}y + {obj_c:g}, "
                        f"z* = {best_value:g} en ({float(best_point[0]):g}, {float(best_point[1]):g})"
                    )
                )
            else:
                self.vertices_box.insert("1.0", "No se encontraron vertices factibles.")
                self.objective_result_label.configure(text="Objetivo: region factible vacia")

            self.status_label.configure(
                text=(
                    "Estado: calculo completado. "
                    f"x >= {x_lower:g}, y >= {y_lower:g}. "
                    f"Grafica: {self.output_image.name}"
                )
            )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            self.status_label.configure(text="Estado: error en la resolucion")
            self.objective_result_label.configure(text="Objetivo: error en calculo")

    def open_image(self) -> None:
        if not self.output_image.exists():
            messagebox.showinfo("Info", "Aun no existe una grafica. Ejecuta primero 'Resolver y graficar'.")
            return

        try:
            self.output_image.resolve().open("rb").close()
            import os

            os.startfile(self.output_image.resolve())
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo abrir la imagen: {exc}")


def main() -> None:
    try:
        app = LPApp()
        app.mainloop()
    except TclError as exc:
        print("No fue posible iniciar la interfaz grafica (Tcl/Tk no disponible).")
        print("Detalle:", exc)
        print("Instala una version estable de Python con Tcl/Tk (por ejemplo 3.12 o 3.13) y recrea el venv.")


if __name__ == "__main__":
    main()
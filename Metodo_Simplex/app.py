import tkinter as tk
from tkinter import ttk, messagebox
# Importamos la clase y la función de formateo desde tu archivo matemático
from simplex import SimplexSolver, to_frac

class SimplexApp(tk.Tk):
    """Interfaz Gráfica para el Método Simplex."""
    def __init__(self):
        super().__init__()
        self.title("Calculadora Simplex - Método 2 Fases")
        self.geometry("990x700")
        self.entries_c = []
        self.entries_A = []
        self.ops_A = []
        self.entries_b = []
        self._build_setup_frame()

    def _build_setup_frame(self):
        self.setup_frame = ttk.Frame(self, padding="10")
        self.setup_frame.pack(fill=tk.X)

        ttk.Label(self.setup_frame, text="Variables (n):").grid(row=0, column=0, padx=5)
        self.n_var = tk.IntVar(value=2)
        ttk.Entry(self.setup_frame, textvariable=self.n_var, width=5).grid(row=0, column=1)

        ttk.Label(self.setup_frame, text="Restricciones (m):").grid(row=0, column=2, padx=5)
        self.m_var = tk.IntVar(value=3)
        ttk.Entry(self.setup_frame, textvariable=self.m_var, width=5).grid(row=0, column=3)

        self.opt_type = tk.StringVar(value="Max")
        ttk.Combobox(self.setup_frame, textvariable=self.opt_type, values=["Max", "Min"], width=5).grid(row=0, column=4, padx=10)

        ttk.Button(self.setup_frame, text="Generar Cuadrícula", command=self._generate_grid).grid(row=0, column=5, padx=10)

        self.grid_frame = ttk.Frame(self, padding="10")
        self.grid_frame.pack(fill=tk.BOTH, expand=True)

    def _generate_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        n = self.n_var.get()
        m = self.m_var.get()
        self.entries_c.clear()
        self.entries_A.clear()
        self.ops_A.clear()
        self.entries_b.clear()

        ttk.Label(self.grid_frame, text="Z = ").grid(row=0, column=0)
        for j in range(n):
            e = ttk.Entry(self.grid_frame, width=10)
            e.grid(row=0, column=j*3+1)
            self.entries_c.append(e)
            ttk.Label(self.grid_frame, text=f"X{j+1} + " if j < n-1 else f"X{j+1}").grid(row=0, column=j*3+2)

        ttk.Separator(self.grid_frame, orient='horizontal').grid(row=1, columnspan=n*3+4, sticky='ew', pady=10)

        for i in range(m):
            row_entries = []
            for j in range(n):
                e = ttk.Entry(self.grid_frame, width=10)
                e.grid(row=i+2, column=j*3+1)
                row_entries.append(e)
                ttk.Label(self.grid_frame, text=f"X{j+1} + " if j < n-1 else f"X{j+1}").grid(row=i+2, column=j*3+2)
            self.entries_A.append(row_entries)
            
            op_var = tk.StringVar(value="<=")
            cb = ttk.Combobox(self.grid_frame, textvariable=op_var, values=["<=", ">=", "="], width=3, state="readonly")
            cb.grid(row=i+2, column=n*3)
            self.ops_A.append(op_var)
            
            b_e = ttk.Entry(self.grid_frame, width=10)
            b_e.grid(row=i+2, column=n*3+1, padx=5)
            self.entries_b.append(b_e)

        ttk.Button(self.grid_frame, text="Resolver Paso a Paso", command=self._solve).grid(row=m+3, column=0, columnspan=n*3+4, pady=15)
        
        self.text_log = tk.Text(self.grid_frame, height=22, width=140, font=("Consolas", 10))
        self.text_log.grid(row=m+4, column=0, columnspan=n*3+4)

    def _solve(self):
        try:
            c = [float(e.get()) for e in self.entries_c]
            A = [[float(e.get()) for e in row] for row in self.entries_A]
            b = [float(e.get()) for e in self.entries_b]
            ops = [op.get() for op in self.ops_A]
            maximize = self.opt_type.get() == "Max"
            
            # Instanciamos la clase que viene desde simplex.py
            solver = SimplexSolver(c, A, b, ops, maximize)
            success, msg = solver.solve()
            
            self.text_log.delete(1.0, tk.END)
            self.text_log.insert(tk.END, "=== RESOLUCIÓN MÉTODO SIMPLEX ===\n")
            
            for step in solver.history:
                headers = ["VB", "Z"] + step['vars'] + ["LD", "Cálculo"]
                header_str = " | ".join(f"{h:^7}" for h in headers)
                sep_line = "-" * len(header_str)
                
                self.text_log.insert(tk.END, f"\n{step['title']}\n")
                self.text_log.insert(tk.END, f"{sep_line}\n{header_str}\n{sep_line}\n")
                
                z_col_value = "1" if maximize else "-1" 
                
                z_row_vals = ["Z", z_col_value] + [to_frac(val) for val in step['tableau'][-1]]
                z_row_str = " | ".join(f"{val:^7}" for val in z_row_vals)
                self.text_log.insert(tk.END, f"{z_row_str} |\n{sep_line}\n")
                
                for i in range(solver.m):
                    vb = step['basis'][i]
                    row_str_vals = [vb, "0"] + [to_frac(val) for val in step['tableau'][i]]
                    calc_str = step['ratios'][i] if step['ratios'] else ""
                    row_str = " | ".join(f"{val:^7}" for val in row_str_vals)
                    self.text_log.insert(tk.END, f"{row_str} | {calc_str}\n")
                    
                self.text_log.insert(tk.END, f"{sep_line}\n")
                self.text_log.insert(tk.END, f"{step['msg']}\n")
                
            if success:
                self.text_log.insert(tk.END, "\n====================================\n")
                sol_str = ", ".join(f"x{i+1} = {val:.2f}" for i, val in enumerate(solver.solution))
                self.text_log.insert(tk.END, f"La solución es {sol_str}.\n")
                self.text_log.insert(tk.END, f"El valor de la función objetivo es Z = {solver.optimal_value:.2f}\n")
                self.text_log.insert(tk.END, "====================================\n")
            else:
                self.text_log.insert(tk.END, f"\nERROR: {msg}")

        except ValueError:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos en las casillas.")

if __name__ == "__main__":
    app = SimplexApp()
    app.mainloop()
# Método Simplex — Implementación y flujo (Metodo_Simplex)

Este archivo explica en detalle el flujo de la implementación del Método Simplex (2 fases) contenida en `Metodo_Simplex`.

Archivos relevantes

- `Simplex.py` — Contiene la clase `SimplexSolver` y la función `to_frac`.
- `app.py` — Interfaz gráfica (Tkinter) que construye la entrada, instancia el solver y muestra el historial paso a paso.

Flujo detallado

1. Entrada (UI)
   - El usuario define `n` (variables), `m` (restricciones), los coeficientes de la función objetivo (`c`), la matriz `A`, el vector `b` y el tipo de desigualdad por fila (`<=`, `>=`, `=`) desde `app.py`.
   - Se elige `Max` o `Min`.

2. Instanciación
   - `app.py` crea: `solver = SimplexSolver(c, A, b, ops, maximize)`.
   - El objeto `solver` guarda `A`, `b`, `c`, `tableau`, `basis`, `var_names`, `history`, `solution`, `optimal_value`.

3. Construcción de la tabla inicial (`_build_initial_tableau`)
   - Cuenta variables de holgura (`h`), exceso (`e`) y artificiales (`a`) según `ops`.
   - Crea `tableau` con `m+1` filas (m restricciones + fila objetivo) y columnas para variables originales y añadidas.
   - Para cada restricción:
     - `<=` → añade holgura `h` (+1) y la incluye en la base.
     - `>=` → añade exceso `e` (-1) y una artificial `a` (+1); la artificial entra en la base.
     - `=`  → añade artificial `a` en la base.

4. Fase 1 (si existen artificiales)
   - `_setup_phase1` ajusta la fila objetivo restando filas con artificiales (objetivo: eliminar artificiales).
   - `_run_simplex_loop("Fase 1")` ejecuta iteraciones:
     - Columna entrante: coeficiente más negativo en la fila objetivo.
     - Calcula razones `b_i / a_ij` para `a_ij > 0` y elige fila saliente por mínima razón.
     - Si todas las razones son `inf` → no acotado.
     - Aplica `_pivot` (normalizar fila pivote y eliminar columna en otras filas).
     - Guarda snapshots en `history` por iteración.
   - Al terminar, si `Z_phase1` no está ~0, el problema no es factible.

5. Preparación y Fase 2
   - `_setup_phase2` elimina columnas artificiales y coloca la función objetivo original (según `c` y `maximize`).
   - Ajusta la fila objetivo restando contribuciones de variables básicas actuales.
   - Ejecuta `_run_simplex_loop("Fase 2")` hasta optimalidad.

6. Extracción de la solución (`_extract_solution`)
   - Construye `solution` asignando a cada `x_i` el RHS si `xi` está en la base.
   - `optimal_value` es la entrada RHS de la fila objetivo (se corrige el signo si fue minimización).

7. Presentación en la UI (`app.py`)
   - Recorre `solver.history` y muestra cada snapshot: base, fila Z, tabla y razones.
   - Muestra `solution` y `optimal_value` al final.

Motivos para usar una clase

- Encapsula estado y operaciones relacionadas.
- Permite múltiples instancias y pruebas aisladas.
- Facilita mantener `history` para depuración/visualización.

Ejecución

Desde la raíz del proyecto (Windows):

```powershell
python Metodo_Simplex/app.py
```

Siguientes pasos sugeridos

- Agregar comentarios inline en `Simplex.py`.
- Añadir `examples/run_example.py` para ejecutar casos de prueba desde consola.
- Crear tests unitarios para vértices conocidos.

Si quieres, yo puedo añadir cualquiera de esos cambios.

---

Ejemplos de uso (código)

1) Uso directo de la clase `SimplexSolver` (script de ejemplo):

```python
from Metodo_Simplex.Simplex import SimplexSolver, to_frac

# Ejemplo: Max Z = 3 x1 + 2 x2
# s.a.  x1 + x2 <= 4
#       x1 + 2x2 >= 3
#       x1 - x2 = 1

c = [3, 2]
A = [[1, 1], [1, 2], [1, -1]]
b = [4, 3, 1]
ops = ['<=', '>=', '=']

solver = SimplexSolver(c, A, b, ops, maximize=True)
success, msg = solver.solve()

if not success:
   print('ERROR:', msg)
else:
   print('Solución:', solver.solution)
   print('Valor óptimo Z =', solver.optimal_value)

# Acceder al historial paso a paso
for step in solver.history:
   print('\n---', step['title'], '---')
   print(step['msg'])
   # `step['tableau']` es un numpy array con la tabla actual
   # `step['basis']` lista de variables básicas por fila
   # `step['ratios']` explicaciones de las razones por fila (si aplica)
   print('Base:', step['basis'])
   print(step['tableau'])
```

2) Formato y estructura de `history` (para mostrar en UI):

- `step['title']` — título del snapshot (ej. "Iteración 1 (Fase 1)").
- `step['tableau']` — numpy array de la tabla (filas: restricciones + fila objetivo).
- `step['basis']` — lista con la variable básica por fila (ej. `['h1', 'a1', 'x2']`).
- `step['ratios']` — lista de cadenas explicando las razones (o `None`).
- `step['vars']` — lista con los nombres de columnas de `tableau`.
- `step['msg']` — mensaje explicativo de la operación realizada.

3) Cómo renderizar la tabla en consola (ejemplo rápido):

```python
def render_step(step, m):
   headers = ['VB'] + step['vars'] + ['RHS']
   print(' | '.join(headers))
   # fila objetivo
   zrow = step['tableau'][-1]
   print('Z |', ' | '.join(to_frac(v) for v in zrow))
   for i in range(m):
      row = step['tableau'][i]
      print(step['basis'][i], '|', ' | '.join(to_frac(v) for v in row))

# Usar: render_step(solver.history[0], solver.m)
```

Explicación de métodos y atributos clave

- `solve()` — ejecuta todo el proceso (con Fase 1 si hay artificiales) y llena `history`.
- `_build_initial_tableau()` — construye la tabla inicial añadiendo columnas `h`, `e`, `a`.
- `_setup_phase1()` / `_setup_phase2()` — preparan la fila objetivo de cada fase.
- `_run_simplex_loop(phase_name)` — bucle principal que selecciona columna entrante, calcula razones, hace pivot y guarda snapshots.
- `_pivot(row, col)` — normaliza fila pivote y elimina la columna en otras filas; actualiza `basis`.
- `history` — lista de diccionarios para cada snapshot (útil para UI o debugging).


Consejos para explicar en una presentación oral

- Empieza por la idea central: una clase (`SimplexSolver`) agrupa estado (tabla, base, history) y comportamiento (construcción, pivoteo, extracción de solución).
- Usa los snippets de este README para mostrar cómo instanciar el solver y cómo leer `history` — no necesitas scripts adicionales.
- Resalta la distinción Fase 1 vs Fase 2:
   - Fase 1: se usan variables artificiales para encontrar una solución factible; objetivo de fase 1 es llevar la suma de artificiales a 0.
   - Fase 2: una vez factible, se elimina lo artificial y se optimiza la función objetivo real.
- Menciona cómo el código detecta condiciones especiales:
   - No acotado: cuando la columna entrante tiene coeficientes <= 0 en todas las filas, o las razones son todas `inf`.
   - No factible: si al acabar Fase 1 el valor objetivo de fase 1 no es ~0.

Puntos clave para explicar cada método (qué hace y por qué importa)

- `__init__`: guarda datos de entrada, crea nombres de variables y prepara contenedores (`tableau`, `basis`, `history`).
- `_build_initial_tableau`: convierte el sistema en una tabla Simplex con columnas adicionales (`h`, `e`, `a`) y establece la base inicial.
- `_setup_phase1`: construye la fila objetivo inicial para minimizar la suma de artificiales (sustrayendo filas con `a`).
- `_run_simplex_loop(phase_name)`: bucle iterativo. Explica la regla usada:
   - Selección de columna entrante: el índice del coeficiente más negativo en la fila objetivo.
   - Cálculo de razones: para cada fila i con a_ij > 0, ratio = b_i / a_ij; elegir la fila con ratio mínimo.
   - No acotado: si no hay coefficients positivos en la columna entrante -> todas las razones son inf -> termina con error.
   - Registro: cada iteración guarda un snapshot en `history` para mostrar al usuario.
- `_pivot`: normaliza la fila pivote (dividir por valor pivote) y elimina la columna pivote en las demás filas; actualiza `basis`.
- `_setup_phase2`: elimina columnas artificiales y restaura la función objetivo original; ajusta la fila objetivo usando la base actual.
- `_extract_solution`: lee la solución final desde la tabla y formatea `solution` y `optimal_value`.

Preguntas frecuentes (cómo responder y qué destacar)

- "¿Por qué hay una Fase 1?" — Respuesta corta: porque restricciones `>=` o `=` introducen variables artificiales necesarias para obtener una base inicial; Fase 1 busca eliminarlas y asegurar factibilidad.
- "¿Cómo detecta si el problema es no acotado o no factible?" — Explica las condiciones sobre razones (no acotado) y el valor final de Z en Fase 1 (no factible).
- "¿Por qué se usan nombres `h`, `e`, `a`?" — Conveniencia didáctica: `h` holgura, `e` exceso, `a` artificial; ayuda a identificar columnas y a construir la base.
- "¿Qué devuelve `solve()`?" — Devuelve `(success: bool, msg: str)`; además llena `solver.history`, `solver.solution` y `solver.optimal_value`.

Pequeña guía de demostración verbal (60s)

1. Presenta el problema (función objetivo y restricciones) y di que `app.py` o el snippet crea `SimplexSolver(c,A,b,ops)`.
2. Explica que `_build_initial_tableau` añade columnas y fija la `basis` inicial (muéstralo en una tabla breve).
3. Describe Fase 1: por qué existen las artificiales y qué significa terminar con Z_phase1 ~ 0.
4. Resume Fase 2: eliminar artificiales, restaurar objetivo, iterar hasta optimalidad.
5. Concluye mostrando `solver.solution` y `solver.optimal_value`.

Si quieres, lo resumo en una diapositiva o en una hoja de apuntes corta que puedas leer al presentar.


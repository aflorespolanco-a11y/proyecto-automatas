

import tkinter as tk
from tkinter import ttk, messagebox


ABRE = "([{"
CIERRA = ")]}"
PAREJA = {')': '(', ']': '[', '}': '{'}
COINCIDE = {'(': ')', '[': ']', '{': '}'}

def flecha(texto, i):
    return " " * i + "^"

def verificar_signos_detallado(expresion):
    pila = []  
    for i, c in enumerate(expresion):
        if c in ABRE:
            pila.append((c, i))
        elif c in CIERRA:
            if not pila:
                return {
                    "ok": False, "tipo": "cierre_sin_apertura",
                    "pos_error_1b": i+1, "pos_apertura_1b": None,
                    "apertura": None, "cierre_encontrado": c, "cierre_esperado": None,
                    "expr": expresion, "linea_flecha": flecha(expresion, i), "idx0": i
                }
            tope, j = pila.pop()
            if PAREJA[c] != tope:
                return {
                    "ok": False, "tipo": "desajuste",
                    "pos_error_1b": i+1, "pos_apertura_1b": j+1,
                    "apertura": tope, "cierre_encontrado": c, "cierre_esperado": COINCIDE[tope],
                    "expr": expresion, "linea_flecha": flecha(expresion, i), "idx0": i
                }
    if pila:
        tope, j = pila.pop()
        return {
            "ok": False, "tipo": "falta_cierre",
            "pos_error_1b": j+1, "pos_apertura_1b": j+1,
            "apertura": tope, "cierre_encontrado": None, "cierre_esperado": COINCIDE[tope],
            "expr": expresion, "linea_flecha": flecha(expresion, j), "idx0": j
        }
    return {"ok": True}

def normalizar_expresion(expresion):
    conv = str.maketrans({"[": "(", "]": ")", "{": "(", "}": ")"})
    return expresion.translate(conv).replace("^", "**")

def caracteres_validos(expresion):
    permitidos = set("0123456789.+-*/() ")
    return all(c in permitidos for c in expresion)

def calcular_expresion(expresion):
    expr = normalizar_expresion(expresion)
    if not caracteres_validos(expr):
        return "Error: hay caracteres no permitidos."
    try:
        valor = eval(expr, {"__builtins__": None}, {})
        if isinstance(valor, (int, float)):
            return str(int(round(valor))) if abs(valor - round(valor)) < 1e-12 else str(valor)
        return "Error: expresión no numérica."
    except ZeroDivisionError:
        return "Error: división entre cero."
    except Exception as e:
        return f"Error de sintaxis o formato: {e}"



PALETA_CLARA = {
    "bg": "#F7F7FB", "panel": "#FFFFFF", "borde": "#E6E6EF",
    "texto": "#1F2937", "suave": "#6B7280",
    "acento": "#4F46E5", "acento_fg": "#FFFFFF",
    "ok": "#2E7D32", "error": "#C62828"
}
PALETA_OSCURA = {
    "bg": "#0F172A", "panel": "#111827", "borde": "#1F2937",
    "texto": "#E5E7EB", "suave": "#9CA3AF",
    "acento": "#8B5CF6", "acento_fg": "#0B1020",
    "ok": "#22C55E", "error": "#EF4444"
}

class App(tk.Frame):   # <-- CAMBIO: hereda de tk.Frame
    def __init__(self, master):
        self.modo_oscuro = tk.BooleanVar(value=False)
        self.paleta = PALETA_CLARA.copy()

        super().__init__(master, bg=self.paleta["bg"])   # <-- ahora sí acepta background
        self.master: tk.Tk = master
        self.master.title("Autómatas | Validador de signos + Calculadora")
        self.master.geometry("930x540")
        self.master.minsize(780, 480)
        self.master.configure(bg=self.paleta["bg"])

        self._config_tema()
        self._build()

    def _config_tema(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Accent.TButton",
                        font=("Segoe UI", 10, "bold"),
                        padding=(14, 8),
                        foreground=PALETA_CLARA["acento_fg"],
                        background=PALETA_CLARA["acento"])
        style.map("Accent.TButton",
                  background=[("active", self._oscurecer(PALETA_CLARA["acento"], 0.9))])
        style.configure("Soft.TButton", padding=(12, 6))
        style.configure("Small.TLabel", foreground=self.paleta["suave"])

    def _recolorear(self):
        
        for w in (self, self.top, self.btns, self.estado, self.res):
            w.configure(background=self.paleta["bg"])
        self.panel.configure(bg=self.paleta["panel"], highlightbackground=self.paleta["borde"])
        for lbl in (self.lbl_valid, self.lbl_resultado, self.lbl_modo, self.lbl_expr, self.lbl_res):
            lbl.configure(bg=self.paleta["bg"], fg=self.paleta["texto"])
        self.lbl_hint.configure(background=self.paleta["bg"], foreground=self.paleta["suave"])
        self.entry.configure(bg=self.paleta["panel"], fg=self.paleta["texto"],
                             insertbackground=self.paleta["texto"], highlightbackground=self.paleta["borde"])
        self.detalle.configure(bg=self.paleta["panel"], fg=self.paleta["texto"], insertbackground=self.paleta["texto"])
        self.detalle.tag_configure("error", foreground=self.paleta["error"])
        self.detalle.tag_configure("ok", foreground=self.paleta["ok"])
        self.detalle.tag_configure("mono", font=("Consolas", 12))
        self.master.configure(bg=self.paleta["bg"])

    def _build(self):
        self.pack(fill="both", expand=True)

      
        self.top = tk.Frame(self, bg=self.paleta["bg"], padx=14, pady=10)
        self.top.pack(fill="x")

        self.lbl_expr = tk.Label(self.top, text="Expresión:", bg=self.paleta["bg"], fg=self.paleta["texto"])
        self.lbl_expr.pack(side="left")

        self.entry = tk.Entry(self.top, font=("Consolas", 12), relief="solid", bd=1)
        self.entry.pack(side="left", fill="x", expand=True, padx=10)
        self.entry.focus()

        # Botones
        self.btns = tk.Frame(self, bg=self.paleta["bg"])
        self.btns.pack(fill="x", padx=14)

        ttk.Button(self.btns, text="Analizar", style="Accent.TButton", command=self.analizar).pack(side="left")
        ttk.Button(self.btns, text="Limpiar", style="Soft.TButton", command=self.limpiar).pack(side="left", padx=6)
        ttk.Button(self.btns, text="Copiar reporte", style="Soft.TButton", command=self.copiar_reporte).pack(side="left", padx=6)

        # Modo oscuro
        self.lbl_modo = tk.Label(self.btns, text="Modo oscuro", bg=self.paleta["bg"], fg=self.paleta["texto"])
        self.lbl_modo.pack(side="right", padx=(0,6))
        ttk.Checkbutton(self.btns, variable=self.modo_oscuro, command=self.toggle_modo).pack(side="right")

        # Estado y resultado
        self.estado = tk.Frame(self, bg=self.paleta["bg"], padx=14, pady=4)
        self.estado.pack(fill="x")
        tk.Label(self.estado, text="Validación de signos:", bg=self.paleta["bg"], fg=self.paleta["texto"]).pack(side="left")
        self.lbl_valid = tk.Label(self.estado, text="—", font=("Segoe UI", 10, "bold"),
                                  bg=self.paleta["bg"], fg=self.paleta["suave"])
        self.lbl_valid.pack(side="left", padx=8)

        self.res = tk.Frame(self, bg=self.paleta["bg"], padx=14)
        self.res.pack(fill="x")
        self.lbl_res = tk.Label(self.res, text="Resultado:", bg=self.paleta["bg"], fg=self.paleta["texto"])
        self.lbl_res.pack(side="left")
        self.lbl_resultado = tk.Label(self.res, text="—", font=("Segoe UI", 10, "bold"),
                                      bg=self.paleta["bg"], fg=self.paleta["suave"])
        self.lbl_resultado.pack(side="left", padx=8)

        # Panel detalle
        self.panel = tk.Frame(self, bg=self.paleta["panel"], padx=12, pady=12, highlightthickness=1,
                              highlightbackground=self.paleta["borde"])
        self.panel.pack(fill="both", expand=True, padx=14, pady=(8,12))

        tk.Label(self.panel, text="Detalle / Línea señalada", bg=self.paleta["panel"],
                 fg=self.paleta["texto"], font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.detalle = tk.Text(self.panel, height=10, font=("Consolas", 12), relief="flat")
        self.detalle.pack(fill="both", expand=True, pady=(6,0))
        self.detalle.config(state="disabled")
        self.lbl_hint = ttk.Label(self.panel, text="Consejo: Enter = analizar, Esc = limpiar.",
                                  style="Small.TLabel")
        self.lbl_hint.pack(anchor="w", pady=(4,0))

        # Atajos
        self.master.bind("<Return>", lambda e: self.analizar())
        self.master.bind("<Escape>", lambda e: self.limpiar())

        self._recolorear()

    # -------- helpers --------
    def toggle_modo(self):
        self.paleta = PALETA_OSCURA.copy() if self.modo_oscuro.get() else PALETA_CLARA.copy()
        self._recolorear()

    def _oscurecer(self, hex_color, factor=0.9):
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16); g = int(hex_color[2:4], 16); b = int(hex_color[4:6], 16)
        r = int(r*factor); g = int(g*factor); b = int(b*factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def set_detalle(self, texto, marca_idx0=None):
        self.detalle.config(state="normal")
        self.detalle.delete("1.0", "end")
        self.detalle.insert("end", texto)
        self.detalle.tag_configure("mono", font=("Consolas", 12))
        self.detalle.tag_add("mono", "1.0", "end")
        if marca_idx0 is not None:
            self.detalle.tag_configure("error", foreground=self.paleta["error"])
            try:
                self.detalle.tag_add("error", f"1.{marca_idx0}", f"1.{marca_idx0+1}")
            except Exception:
                pass
        self.detalle.config(state="disabled")

    def limpiar(self):
        self.entry.delete(0, "end")
        self.lbl_valid.config(text="—", fg=self.paleta["suave"])
        self.lbl_resultado.config(text="—", fg=self.paleta["suave"])
        self.set_detalle("")
        self.entry.focus()

    # -------- Acciones --------
    def analizar(self):
        expr = self.entry.get().strip()
        if not expr:
            messagebox.showinfo("Atención", "Ingresa una expresión.")
            return

        info = verificar_signos_detallado(expr)
        if not info["ok"]:
            self.lbl_valid.config(text="❌ Signos incorrectos", fg=self.paleta["error"])
            tipo = {"cierre_sin_apertura":"Cierre sin apertura",
                    "desajuste":"Desajuste de signos",
                    "falta_cierre":"Falta cierre"}[info["tipo"]]
            partes = [
                f"Tipo de error: {tipo}",
                f"Carácter del error: {info['pos_error_1b']}",
            ]
            if info.get("pos_apertura_1b") is not None:
                partes.append(f"Carácter de la apertura: {info['pos_apertura_1b']}")
            if info.get("apertura") is not None:
                partes.append(f"Apertura: {info['apertura']}")
            if info.get("cierre_encontrado") is not None:
                partes.append(f"Cierre encontrado: {info['cierre_encontrado']}")
            if info.get("cierre_esperado") is not None:
                partes.append(f"Cierre esperado: {info['cierre_esperado']}")
            partes += ["", info["expr"], info["linea_flecha"]]
            self.set_detalle("\n".join(partes), marca_idx0=info.get("idx0"))
            self.lbl_resultado.config(text="—", fg=self.paleta["suave"])
            return

        self.lbl_valid.config(text="✅ Signos correctos", fg=self.paleta["ok"])
        res = calcular_expresion(expr)
        if res.startswith("Error"):
            self.lbl_resultado.config(text=f"❌ {res}", fg=self.paleta["error"])
            self.set_detalle(expr + "\n" + flecha(expr, 0).replace("^",""))
        else:
            self.lbl_resultado.config(text=res, fg=self.paleta["ok"])
            self.set_detalle(expr + "\n" + flecha(expr, 0).replace("^",""))

    def copiar_reporte(self):
        expr = self.entry.get().strip()
        info = verificar_signos_detallado(expr) if expr else {"ok": None}
        texto = ["=== Reporte ===", f"Expresión: {expr or '(vacío)'}"]
        if info.get("ok") is True:
            texto.append("Validación: ✅ correcta")
            texto.append("Resultado: " + calcular_expresion(expr))
        elif info.get("ok") is False:
            texto.append("Validación: ❌ incorrecta")
            texto.append(f"Tipo: {info['tipo']}")
            texto.append(f"Carácter error: {info['pos_error_1b']}")
            if info.get("pos_apertura_1b") is not None:
                texto.append(f"Apertura en: {info['pos_apertura_1b']}")
            if info.get("apertura") is not None:
                texto.append(f"Apertura: {info['apertura']}")
            if info.get("cierre_encontrado") is not None:
                texto.append(f"Cierre encontrado: {info['cierre_encontrado']}")
            if info.get("cierre_esperado") is not None:
                texto.append(f"Cierre esperado: {info['cierre_esperado']}")
            texto += [info["expr"], info["linea_flecha"]]
        else:
            texto.append("Validación: —")
    
        self.master.clipboard_clear()
        self.master.clipboard_append("\n".join(texto))
        messagebox.showinfo("Copiado", "Reporte copiado al portapapeles.")

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()

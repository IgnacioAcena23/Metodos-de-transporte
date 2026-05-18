import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import groq_client

def _penalidad_fila(costos, fila, cols_activas):
    vals = sorted(costos[fila][c] for c in cols_activas)
    if len(vals) >= 2:
        return vals[1] - vals[0]
    return 0

def _penalidad_col(costos, col, filas_activas):
    vals = sorted(costos[f][col] for f in filas_activas)
    if len(vals) >= 2:
        return vals[1] - vals[0]
    return 0

def vogel(costos_orig, oferta_orig, demanda_orig):
    n_orig = len(oferta_orig)
    n_dest = len(demanda_orig)

    of  = list(oferta_orig)
    dem = list(demanda_orig)
    costos = [list(f) for f in costos_orig]

    total_of  = sum(of)
    total_dem = sum(dem)
    fic_orig = fic_dest = False

    if total_of > total_dem:
        dem.append(total_of - total_dem)
        for fila in costos:
            fila.append(0)
        fic_dest = True
    elif total_dem > total_of:
        of.append(total_dem - total_of)
        costos.append([0] * len(dem))
        fic_orig = True

    rows = len(of)
    cols = len(dem)

    asig = [[0.0] * cols for _ in range(rows)]
    pasos = []

    filas_activas = list(range(rows))
    cols_activas  = list(range(cols))

    while filas_activas and cols_activas:
        pen_filas = {
            i: _penalidad_fila(costos, i, cols_activas)
            for i in filas_activas
        }
        pen_cols = {
            j: _penalidad_col(costos, j, filas_activas)
            for j in cols_activas
        }

        max_pen_f = max(pen_filas.values())
        max_pen_c = max(pen_cols.values())

        if max_pen_f >= max_pen_c:
            fila = max(pen_filas, key=lambda i: pen_filas[i])
            col = min(cols_activas, key=lambda j: costos[fila][j])
            pen_tipo = "F"
            pen_idx  = fila
            pen_val  = max_pen_f
        else:
            col = max(pen_cols, key=lambda j: pen_cols[j])
            fila = min(filas_activas, key=lambda i: costos[i][col])
            pen_tipo = "C"
            pen_idx  = col
            pen_val  = max_pen_c

        cantidad = min(of[fila], dem[col])
        asig[fila][col] = cantidad
        cu = costos[fila][col]

        pasos.append({
            "row": fila, "col": col,
            "cantidad": cantidad,
            "pen_tipo": pen_tipo,
            "pen_idx":  pen_idx,
            "pen_val":  pen_val,
            "costo_unitario": cu,
            "subtotal": cantidad * cu,
        })

        of[fila]  -= cantidad
        dem[col]  -= cantidad

        if of[fila] == 0 and fila in filas_activas:
            filas_activas.remove(fila)
        if dem[col] == 0 and col in cols_activas:
            cols_activas.remove(col)

    costo_total = sum(
        asig[r][c] * costos_orig[r][c]
        for r in range(n_orig)
        for c in range(n_dest)
    )
    return asig, costo_total, pasos, fic_orig, fic_dest

BG        = "#0f1117"
SURFACE   = "#1a1d27"
CARD      = "#21253a"
ACCENT    = "#f59e0b"
ACCENT2   = "#fbbf24"
TEXT      = "#e2e8f0"
MUTED     = "#64748b"
SUCCESS   = "#22c55e"
WARNING   = "#f59e0b"
DANGER    = "#ef4444"
ALLOC_BG  = "#3b2000"
HEADER_BG = "#2d1b00"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Método de Aproximación de Vogel")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.geometry("1100x720")
        self.state('zoomed')

        self._setup_styles()
        self._build_header()
        self._build_config_bar()
        self._build_main()
        self._build_footer()

        self.n_orig = 0
        self.n_dest = 0
        self.entries_costo    = []
        self.entries_oferta   = []
        self.entries_demanda  = []
        self.entries_row_name = []
        self.entries_col_name = []

    def _setup_styles(self):
        self.base_font  = tkfont.Font(family="Segoe UI", size=10)
        self.bold_font  = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.title_font = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        self.small_font = tkfont.Font(family="Segoe UI", size=9)

        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame",      background=BG)
        s.configure("Card.TFrame", background=CARD)
        s.configure("TLabel",      background=BG,      foreground=TEXT, font=self.base_font)
        s.configure("Card.TLabel", background=CARD,    foreground=TEXT, font=self.base_font)
        s.configure("TEntry",      fieldbackground=SURFACE, foreground=TEXT,
                    insertcolor=TEXT, relief="flat", borderwidth=0)
        s.configure("Accent.TButton",
                    background=ACCENT, foreground="#0f1117",
                    font=self.bold_font, relief="flat", borderwidth=0, padding=(16, 8))
        s.map("Accent.TButton",
              background=[("active", ACCENT2), ("pressed", "#b45309")])
        s.configure("Secondary.TButton",
                    background=CARD, foreground=TEXT,
                    font=self.base_font, relief="flat", borderwidth=0, padding=(12, 6))
        s.map("Secondary.TButton",
              background=[("active", SURFACE), ("pressed", BG)])

    def _build_header(self):
        hdr = tk.Frame(self, bg=SURFACE, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="◈  Método de Vogel",
                 font=self.title_font, bg=SURFACE, fg=ACCENT2).pack(side="left", padx=24)
        tk.Label(hdr, text="Método de Aproximación de Vogel (VAM) – solución inicial óptima",
                 font=self.small_font, bg=SURFACE, fg=MUTED).pack(side="left", padx=4)

    def _build_config_bar(self):
        bar = tk.Frame(self, bg=CARD, pady=12, padx=20)
        bar.pack(fill="x")

        tk.Label(bar, text="Orígenes:", bg=CARD, fg=TEXT,
                 font=self.base_font).pack(side="left")
        self.spin_orig = tk.Spinbox(bar, from_=2, to=8, width=4,
                                    bg=SURFACE, fg=TEXT,
                                    buttonbackground=SURFACE,
                                    relief="flat", font=self.base_font,
                                    insertbackground=TEXT)
        self.spin_orig.delete(0, "end"); self.spin_orig.insert(0, "3")
        self.spin_orig.pack(side="left", padx=(4, 20))

        tk.Label(bar, text="Destinos:", bg=CARD, fg=TEXT,
                 font=self.base_font).pack(side="left")
        self.spin_dest = tk.Spinbox(bar, from_=2, to=8, width=4,
                                    bg=SURFACE, fg=TEXT,
                                    buttonbackground=SURFACE,
                                    relief="flat", font=self.base_font,
                                    insertbackground=TEXT)
        self.spin_dest.delete(0, "end"); self.spin_dest.insert(0, "3")
        self.spin_dest.pack(side="left", padx=(4, 20))

        ttk.Button(bar, text="⟳  Generar tabla",
                   style="Accent.TButton",
                   command=self.generar_tabla).pack(side="left", padx=8)
        ttk.Button(bar, text="▶  Resolver (Vogel)",
                   style="Accent.TButton",
                   command=self.resolver).pack(side="left", padx=4)
        ttk.Button(bar, text="↺  Limpiar",
                   style="Secondary.TButton",
                   command=self.limpiar).pack(side="left", padx=4)
        ttk.Button(bar, text="🤖  Analizar con Groq",
                   style="Accent.TButton",
                   command=self.analizar_ia).pack(side="left", padx=8)

    def _build_main(self):
        self.paned = tk.PanedWindow(self, orient="horizontal", bg=BG,
                                    sashwidth=6, sashrelief="flat")
        self.paned.pack(fill="both", expand=True)
        self.left_frame = tk.Frame(self.paned, bg=BG)

        self.paned.add(self.left_frame, minsize=520, stretch="always")
        self.left_frame.rowconfigure(0, weight=1)
        self.left_frame.rowconfigure(1, weight=0)
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.columnconfigure(1, weight=0)

        self.canvas = tk.Canvas(self.left_frame, bg=BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        v_scroll = tk.Scrollbar(self.left_frame, orient="vertical",
                                command=self.canvas.yview, bg=SURFACE)
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll = tk.Scrollbar(self.left_frame, orient="horizontal",
                                command=self.canvas.xview, bg=SURFACE)
        h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=v_scroll.set,
                              xscrollcommand=h_scroll.set)

        self.table_frame = tk.Frame(self.canvas, bg=BG)
        self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        self.table_frame.bind("<Configure>",
                              lambda e: self.canvas.configure(
                                  scrollregion=self.canvas.bbox("all")))

        self.right_frame = tk.Frame(self.paned, bg=SURFACE, width=360)
        self.paned.add(self.right_frame, minsize=300)
        self._build_results_panel()

    def _build_results_panel(self):
        tk.Label(self.right_frame, text="Resultados",
                 font=self.bold_font, bg=SURFACE, fg=ACCENT2,
                 pady=12).pack(fill="x", padx=16)
        tk.Frame(self.right_frame, bg=ACCENT, height=2).pack(fill="x", padx=16)

        self.result_text = tk.Text(
            self.right_frame, bg=SURFACE, fg=TEXT,
            font=self.small_font, relief="flat", wrap="word",
            state="disabled", insertbackground=TEXT,
            selectbackground=ACCENT, pady=8, padx=12)
        self.result_text.pack(fill="both", expand=True, padx=4, pady=8)

        rt = self.result_text
        rt.tag_config("title",   foreground=ACCENT2,  font=self.bold_font)
        rt.tag_config("success", foreground=SUCCESS,  font=self.bold_font)
        rt.tag_config("warn",    foreground=WARNING)
        rt.tag_config("muted",   foreground=MUTED,    font=self.small_font)
        rt.tag_config("value",   foreground=ACCENT2)
        rt.tag_config("pen",     foreground="#94a3b8", font=self.small_font)
        rt.tag_config("ia",      foreground="#a5f3fc", font=self.small_font)
        rt.tag_config("ia_title",foreground="#38bdf8", font=self.bold_font)
        self._ultimo_resultado = None

    def _build_footer(self):
        foot = tk.Frame(self, bg=SURFACE, pady=6)
        foot.pack(fill="x", side="bottom")
        tk.Label(foot,
                 text="ℹ El método de Vogel evalúa las penalidades por fila y columna para priorizar las rutas con menores costos relativos.",
                 font=self.small_font, bg=SURFACE, fg=MUTED).pack()

    def generar_tabla(self):
        try:
            n_orig = int(self.spin_orig.get())
            n_dest = int(self.spin_dest.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos.")
            return
        if not (2 <= n_orig <= 8 and 2 <= n_dest <= 8):
            messagebox.showerror("Error", "Rango válido: entre 2 y 8.")
            return

        self.n_orig = n_orig
        self.n_dest = n_dest

        for w in self.table_frame.winfo_children():
            w.destroy()

        self.entries_costo    = []
        self.entries_oferta   = []
        self.entries_demanda  = []
        self.entries_row_name = []
        self.entries_col_name = []

        PAD = 4

        tk.Label(self.table_frame, text="", bg=BG, width=14
                 ).grid(row=0, column=0, padx=PAD, pady=PAD)

        for j in range(n_dest):
            e = self._entry(self.table_frame, 100, f"Destino {j+1}",
                            HEADER_BG, ACCENT2, bold=True)
            e.grid(row=0, column=j+1, padx=PAD, pady=PAD)
            self.entries_col_name.append(e)

        tk.Label(self.table_frame, text="Oferta",
                 bg=HEADER_BG, fg=SUCCESS,
                 font=self.bold_font, width=10,
                 relief="flat").grid(row=0, column=n_dest+1, padx=PAD, pady=PAD)

        for i in range(n_orig):
            e_name = self._entry(self.table_frame, 100, f"Origen {i+1}",
                                 HEADER_BG, ACCENT2, bold=True)
            e_name.grid(row=i+1, column=0, padx=PAD, pady=PAD)
            self.entries_row_name.append(e_name)

            fila = []
            for j in range(n_dest):
                e = self._entry(self.table_frame, 80, "0", CARD, TEXT)
                e.grid(row=i+1, column=j+1, padx=PAD, pady=PAD)
                fila.append(e)
            self.entries_costo.append(fila)

            e_of = self._entry(self.table_frame, 90, "0", "#0f2d1a", SUCCESS)
            e_of.grid(row=i+1, column=n_dest+1, padx=PAD, pady=PAD)
            self.entries_oferta.append(e_of)

        tk.Label(self.table_frame, text="Demanda",
                 bg=HEADER_BG, fg=WARNING,
                 font=self.bold_font, width=14,
                 relief="flat").grid(row=n_orig+1, column=0, padx=PAD, pady=PAD)

        for j in range(n_dest):
            e = self._entry(self.table_frame, 80, "0", "#2d1b00", WARNING)
            e.grid(row=n_orig+1, column=j+1, padx=PAD, pady=PAD)
            self.entries_demanda.append(e)

        tk.Label(self.table_frame, text="—", bg=BG, fg=MUTED
                 ).grid(row=n_orig+1, column=n_dest+1, padx=PAD, pady=PAD)

        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._write_plain("Tabla generada.\nIngrese los valores y presione ▶ Resolver.")

    def _entry(self, parent, px_width, default, bg, fg, bold=False):
        f = tkfont.Font(family="Segoe UI", size=10,
                        weight="bold" if bold else "normal")
        e = tk.Entry(parent, width=max(int(px_width // 8), 6),
                     bg=bg, fg=fg, font=f, relief="flat", bd=0,
                     insertbackground=fg, justify="center",
                     highlightthickness=1,
                     highlightbackground=MUTED,
                     highlightcolor=ACCENT)
        e.insert(0, default)
        return e

    def resolver(self):
        if not self.entries_costo:
            messagebox.showwarning("Aviso", "Primero genera la tabla.")
            return
        try:
            nombres_orig = [e.get().strip() or f"O{i+1}"
                            for i, e in enumerate(self.entries_row_name)]
            nombres_dest = [e.get().strip() or f"D{j+1}"
                            for j, e in enumerate(self.entries_col_name)]
            costos  = [[float(self.entries_costo[i][j].get())
                        for j in range(self.n_dest)]
                       for i in range(self.n_orig)]
            oferta  = [float(e.get()) for e in self.entries_oferta]
            demanda = [float(e.get()) for e in self.entries_demanda]
        except ValueError:
            messagebox.showerror("Error", "Todos los campos deben ser números válidos.")
            return

        asig, costo, pasos, fic_orig, fic_dest = vogel(costos, oferta, demanda)

        self._reset_cells()
        for p in pasos:
            r, c = p["row"], p["col"]
            if r < self.n_orig and c < self.n_dest:
                self.entries_costo[r][c].configure(bg=ALLOC_BG, fg=ACCENT2)

        self._show_results(nombres_orig, nombres_dest,
                           costos, pasos, oferta, demanda,
                           costo, fic_orig, fic_dest)

        self._ultimo_resultado = {
            "nombres_orig": nombres_orig,
            "nombres_dest": nombres_dest,
            "costos":       costos,
            "oferta":       oferta,
            "demanda":      demanda,
            "pasos":        pasos,
            "costo":        costo,
            "fic_orig":     fic_orig,
            "fic_dest":     fic_dest,
        }

    def _reset_cells(self):
        for fila in self.entries_costo:
            for e in fila:
                e.configure(bg=CARD, fg=TEXT)

    def _write_plain(self, text):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", text)
        self.result_text.configure(state="disabled")

    def _show_results(self, n_orig, n_dest, costos,
                      pasos, oferta, demanda,
                      costo_total, fic_orig, fic_dest):
        rt = self.result_text
        rt.configure(state="normal")
        rt.delete("1.0", "end")

        ins = rt.insert

        ins("end", "═" * 38 + "\n", "muted")
        ins("end", " MÉTODO DE APROXIMACIÓN DE VOGEL\n", "title")
        ins("end", "═" * 38 + "\n\n", "muted")

        total_of  = sum(oferta)
        total_dem = sum(demanda)

        if fic_orig:
            ins("end", "⚠ Problema desbalanceado\n", "warn")
            ins("end", f"  Oferta  : {total_of}\n", "muted")
            ins("end", f"  Demanda : {total_dem}\n", "muted")
            ins("end", f"  → Origen ficticio ({total_dem - total_of})\n\n", "warn")
        elif fic_dest:
            ins("end", "⚠ Problema desbalanceado\n", "warn")
            ins("end", f"  Oferta  : {total_of}\n", "muted")
            ins("end", f"  Demanda : {total_dem}\n", "muted")
            ins("end", f"  → Destino ficticio ({total_of - total_dem})\n\n", "warn")
        else:
            ins("end", "✔ Problema balanceado\n\n", "success")

        ins("end", "Iteraciones:\n", "title")
        ins("end", "─" * 38 + "\n", "muted")

        for k, p in enumerate(pasos, 1):
            r, c = p["row"], p["col"]
            if r >= len(n_orig) or c >= len(n_dest):
                continue          # celdas ficticias, omitir
            tipo   = "Fila" if p["pen_tipo"] == "F" else "Col."
            nombre = n_orig[p["pen_idx"]] if p["pen_tipo"] == "F" \
                     else n_dest[p["pen_idx"]]
            ins("end", f" Iter {k}\n", "value")
            ins("end", f"  Penalidad máx → {tipo}: {nombre} = {p['pen_val']:.0f}\n", "pen")
            ins("end", f"  Asignación: {n_orig[r]} → {n_dest[c]}\n", "")
            ins("end", f"  Cantidad  : {p['cantidad']:.0f}\n", "")
            ins("end",
                f"  Costo     : {p['costo_unitario']} × {p['cantidad']:.0f} "
                f"= {p['subtotal']:.2f}\n", "muted")
            ins("end", "  " + "·" * 34 + "\n", "muted")

        ins("end", "\n" + "═" * 38 + "\n", "muted")
        ins("end", " Costo total estimado:\n", "title")
        ins("end", f" $ {costo_total:.2f}\n", "success")
        ins("end", "═" * 38 + "\n", "muted")

        rt.configure(state="disabled")

    def analizar_ia(self):
        if self._ultimo_resultado is None:
            messagebox.showwarning("Aviso", "Primero resuelve el problema para analizarlo.")
            return

        d = self._ultimo_resultado

        asignaciones_txt = []
        for p in d["pasos"]:
            r, c = p["row"], p["col"]
            if r < self.n_orig and c < self.n_dest:
                oname = d["nombres_orig"][r]
                dname = d["nombres_dest"][c]
                pen   = p["pen_val"]
                tipo  = "fila" if p["pen_tipo"] == "F" else "columna"
                cu    = p["costo_unitario"]
                cant  = p["cantidad"]
                asignaciones_txt.append(
                    f"  {oname} → {dname}: {cant:.0f} uds @ costo {cu}, "
                    f"penalidad {tipo} = {pen:.0f} (subtotal {p['subtotal']:.2f})"
                )

        balance = (
            f"Origen ficticio añadido ({sum(d['demanda'])-sum(d['oferta'])})"
            if d["fic_orig"]
            else f"Destino ficticio añadido ({sum(d['oferta'])-sum(d['demanda'])})"
            if d["fic_dest"]
            else "Problema balanceado"
        )

        prompt = (
            "Eres un experto en programación matemática y métodos de transporte.\n"
            "Se resolvió un problema de transporte usando el Método de Aproximación de Vogel (VAM).\n\n"
            f"Orígenes: {d['nombres_orig']}\n"
            f"Destinos: {d['nombres_dest']}\n"
            f"Oferta:   {d['oferta']}\n"
            f"Demanda:  {d['demanda']}\n"
            f"Balance:  {balance}\n\n"
            "Iteraciones (con penalidades):\n" + "\n".join(asignaciones_txt) + "\n\n"
            f"Costo total de la solución inicial: ${d['costo']:.2f}\n\n"
            "Por favor:\n"
            "1. Explica brevemente cómo Vogel eligió cada asignación (penalidades).\n"
            "2. Comenta si la solución parece de buena calidad.\n"
            "3. Indica si se recomienda verificar optimalidad con MODI.\n"
            "Responde en español, de forma concisa (máx. 200 palabras)."
        )

        try:
            respuesta = groq_client.consultar_groq(prompt, max_tokens=400)
            self._mostrar_ia(respuesta, error=False)
        except RuntimeError as e:
            self._mostrar_ia(str(e), error=True)

    def _mostrar_ia(self, texto: str, error: bool):
        rt = self.result_text
        rt.configure(state="normal")
        if error:
            rt.insert("end", f"\n Error: {texto}\n", "warn")
        else:
            rt.insert("end", "\n", "")
            for linea in texto.splitlines():
                rt.insert("end", linea + "\n", "ia")
        rt.insert("end", "─" * 38 + "\n", "muted")
        rt.configure(state="disabled")
        rt.see("end")

    def limpiar(self):
        for fila in self.entries_costo:
            for e in fila:
                e.delete(0, "end"); e.insert(0, "0")
                e.configure(bg=CARD, fg=TEXT)
        for e in self.entries_oferta:
            e.delete(0, "end"); e.insert(0, "0")
        for e in self.entries_demanda:
            e.delete(0, "end"); e.insert(0, "0")
        self._ultimo_resultado = None
        self._write_plain("Tabla limpiada.")


if __name__ == "__main__":
    App().mainloop()

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import groq_client

def esquina_noroeste(costos, oferta, demanda):
    n_orig = len(oferta)
    n_dest = len(demanda)

    of = list(oferta)
    dem = list(demanda)
    total_of = sum(of)
    total_dem = sum(dem)

    ficticio_origen = ficticio_destino = False

    if total_of > total_dem:
        dem.append(total_of - total_dem)
        for fila in costos:
            fila.append(0)
        ficticio_destino = True
    elif total_dem > total_of:
        of.append(total_dem - total_of)
        costos.append([0] * len(dem))
        ficticio_origen = True

    rows = len(of)
    cols = len(dem)
    asig = [[0.0] * cols for _ in range(rows)]
    pasos = []

    i = j = 0
    while i < rows and j < cols:
        cantidad = min(of[i], dem[j])
        asig[i][j] = cantidad
        pasos.append((i, j, cantidad))
        of[i] -= cantidad
        dem[j] -= cantidad
        if of[i] == 0:
            i += 1
        if dem[j] == 0:
            j += 1

    costo = sum(
        asig[r][c] * costos[r][c]
        for r in range(rows) for c in range(cols)
        if not (ficticio_destino and c == cols - 1)
        and not (ficticio_origen and r == rows - 1)
    )
    return asig, costo, pasos, ficticio_origen, ficticio_destino


BG        = "#0f1117"
SURFACE   = "#1a1d27"
CARD      = "#21253a"
ACCENT    = "#6c63ff"
ACCENT2   = "#a78bfa"
TEXT      = "#e2e8f0"
MUTED     = "#64748b"
SUCCESS   = "#22c55e"
WARNING   = "#f59e0b"
DANGER    = "#ef4444"
ALLOC_BG  = "#1e3a5f"
HEADER_BG = "#2d1b69"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Método Esquina Noroeste")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.geometry("1050x700")
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
        self.base_font   = tkfont.Font(family="Segoe UI", size=10)
        self.bold_font   = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.title_font  = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        self.small_font  = tkfont.Font(family="Segoe UI", size=9)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame",      background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel",      background=BG, foreground=TEXT,
                        font=self.base_font)
        style.configure("Card.TLabel", background=CARD, foreground=TEXT,
                        font=self.base_font)
        style.configure("TEntry",      fieldbackground=SURFACE, foreground=TEXT,
                        insertcolor=TEXT, relief="flat", borderwidth=0)
        style.configure("Accent.TButton",
                        background=ACCENT, foreground="white",
                        font=self.bold_font, relief="flat", borderwidth=0,
                        padding=(16, 8))
        style.map("Accent.TButton",
                  background=[("active", ACCENT2), ("pressed", "#4c46b0")])
        style.configure("Secondary.TButton",
                        background=CARD, foreground=TEXT,
                        font=self.base_font, relief="flat", borderwidth=0,
                        padding=(12, 6))
        style.map("Secondary.TButton",
                  background=[("active", SURFACE), ("pressed", BG)])

    def _build_header(self):
        hdr = tk.Frame(self, bg=SURFACE, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="✦  Esquina Noroeste",
                 font=self.title_font, bg=SURFACE, fg=ACCENT2).pack(side="left", padx=24)
        tk.Label(hdr, text="Método de solución básica factible inicial",
                 font=self.small_font, bg=SURFACE, fg=MUTED).pack(side="left", padx=4)

    def _build_config_bar(self):
        bar = tk.Frame(self, bg=CARD, pady=12, padx=20)
        bar.pack(fill="x")

        tk.Label(bar, text="Orígenes:", bg=CARD, fg=TEXT,
                 font=self.base_font).pack(side="left")
        self.spin_orig = tk.Spinbox(bar, from_=2, to=8, width=4,
                                    bg=SURFACE, fg=TEXT, buttonbackground=SURFACE,
                                    relief="flat", font=self.base_font,
                                    insertbackground=TEXT)
        self.spin_orig.delete(0, "end"); self.spin_orig.insert(0, "3")
        self.spin_orig.pack(side="left", padx=(4, 20))

        tk.Label(bar, text="Destinos:", bg=CARD, fg=TEXT,
                 font=self.base_font).pack(side="left")
        self.spin_dest = tk.Spinbox(bar, from_=2, to=8, width=4,
                                    bg=SURFACE, fg=TEXT, buttonbackground=SURFACE,
                                    relief="flat", font=self.base_font,
                                    insertbackground=TEXT)
        self.spin_dest.delete(0, "end"); self.spin_dest.insert(0, "3")
        self.spin_dest.pack(side="left", padx=(4, 20))

        ttk.Button(bar, text="⟳  Generar tabla",
                   style="Accent.TButton",
                   command=self.generar_tabla).pack(side="left", padx=8)

        ttk.Button(bar, text="▶  Resolver",
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
        self.paned.pack(fill="both", expand=True, padx=0, pady=0)

        self.left_frame = tk.Frame(self.paned, bg=BG)
        self.paned.add(self.left_frame, minsize=500, stretch="always")

        self.left_frame.rowconfigure(0, weight=1)
        self.left_frame.rowconfigure(1, weight=0)
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.columnconfigure(1, weight=0)

        self.canvas = tk.Canvas(self.left_frame, bg=BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.v_scroll = tk.Scrollbar(self.left_frame, orient="vertical",
                                     command=self.canvas.yview, bg=SURFACE)
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll = tk.Scrollbar(self.left_frame, orient="horizontal",
                                     command=self.canvas.xview, bg=SURFACE)
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=self.v_scroll.set,
                              xscrollcommand=self.h_scroll.set)

        self.table_frame = tk.Frame(self.canvas, bg=BG)
        self.table_win = self.canvas.create_window((0, 0), window=self.table_frame,
                                                   anchor="nw")
        self.table_frame.bind("<Configure>", self._on_table_resize)

        self.right_frame = tk.Frame(self.paned, bg=SURFACE, width=340)
        self.paned.add(self.right_frame, minsize=300)
        self._build_results_panel()

    def _on_table_resize(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _build_results_panel(self):
        tk.Label(self.right_frame, text="Resultados",
                 font=self.bold_font, bg=SURFACE, fg=ACCENT2,
                 pady=12).pack(fill="x", padx=16)

        sep = tk.Frame(self.right_frame, bg=ACCENT, height=2)
        sep.pack(fill="x", padx=16)

        self.result_text = tk.Text(self.right_frame, bg=SURFACE, fg=TEXT,
                                   font=self.small_font, relief="flat",
                                   wrap="word", state="disabled",
                                   insertbackground=TEXT,
                                   selectbackground=ACCENT,
                                   pady=8, padx=12)
        self.result_text.pack(fill="both", expand=True, padx=4, pady=8)

        self.result_text.tag_config("title",   foreground=ACCENT2,   font=self.bold_font)
        self.result_text.tag_config("success", foreground=SUCCESS,   font=self.bold_font)
        self.result_text.tag_config("warn",    foreground=WARNING)
        self.result_text.tag_config("muted",   foreground=MUTED,     font=self.small_font)
        self.result_text.tag_config("value",   foreground=ACCENT2)
        self.result_text.tag_config("ia",      foreground="#a5f3fc", font=self.small_font)
        self.result_text.tag_config("ia_title",foreground="#38bdf8", font=self.bold_font)

        self._ultimo_resultado = None

    def _build_footer(self):
        foot = tk.Frame(self, bg=SURFACE, pady=6)
        foot.pack(fill="x", side="bottom")
        tk.Label(foot,
                 text="ℹ El método de la Esquina Noroeste asigna la máxima cantidad posible a la celda superior izquierda y avanza de forma secuencial.",
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

        PAD  = 4
        CW   = 80
        HW   = 100
        RW   = 90
        CH   = 34
        tk.Label(self.table_frame, text="",
                 bg=BG, width=14).grid(row=0, column=0, padx=PAD, pady=PAD)

        for j in range(n_dest):
            e = self._make_entry(self.table_frame, HW,
                                 f"Destino {j+1}", HEADER_BG, ACCENT2, bold=True)
            e.grid(row=0, column=j+1, padx=PAD, pady=PAD)
            self.entries_col_name.append(e)

        tk.Label(self.table_frame, text="Oferta",
                 bg=HEADER_BG, fg=SUCCESS,
                 font=self.bold_font, width=10,
                 relief="flat").grid(row=0, column=n_dest+1, padx=PAD, pady=PAD)

        for i in range(n_orig):
            e_name = self._make_entry(self.table_frame, HW,
                                      f"Origen {i+1}", HEADER_BG, ACCENT2, bold=True)
            e_name.grid(row=i+1, column=0, padx=PAD, pady=PAD)
            self.entries_row_name.append(e_name)

            fila_costos = []
            for j in range(n_dest):
                e = self._make_entry(self.table_frame, CW, "0", CARD, TEXT)
                e.grid(row=i+1, column=j+1, padx=PAD, pady=PAD)
                fila_costos.append(e)
            self.entries_costo.append(fila_costos)

            e_of = self._make_entry(self.table_frame, RW, "0", "#0f2d1a", SUCCESS)
            e_of.grid(row=i+1, column=n_dest+1, padx=PAD, pady=PAD)
            self.entries_oferta.append(e_of)
        tk.Label(self.table_frame, text="Demanda",
                 bg=HEADER_BG, fg=WARNING,
                 font=self.bold_font, width=14,
                 relief="flat").grid(row=n_orig+1, column=0, padx=PAD, pady=PAD)

        for j in range(n_dest):
            e = self._make_entry(self.table_frame, CW, "0", "#2d1b00", WARNING)
            e.grid(row=n_orig+1, column=j+1, padx=PAD, pady=PAD)
            self.entries_demanda.append(e)

        tk.Label(self.table_frame, text="—",
                 bg=BG, fg=MUTED).grid(row=n_orig+1, column=n_dest+1,
                                       padx=PAD, pady=PAD)

        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self._write_results("Tabla generada. Ingrese los valores y presione ▶ Resolver.\n",
                            tags=[])

    def _make_entry(self, parent, width, default, bg, fg, bold=False):
        f = tkfont.Font(family="Segoe UI", size=10,
                        weight="bold" if bold else "normal")
        e = tk.Entry(parent, width=int(width//8),
                     bg=bg, fg=fg, font=f,
                     relief="flat", bd=0,
                     insertbackground=fg,
                     justify="center",
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

            costos = [[float(self.entries_costo[i][j].get())
                       for j in range(self.n_dest)]
                      for i in range(self.n_orig)]

            oferta  = [float(e.get()) for e in self.entries_oferta]
            demanda = [float(e.get()) for e in self.entries_demanda]

        except ValueError:
            messagebox.showerror("Error", "Todos los campos deben ser números válidos.")
            return

        asig, costo, pasos, fic_orig, fic_dest = esquina_noroeste(
            [list(f) for f in costos], list(oferta), list(demanda)
        )

        self._reset_cell_colors()
        for (r, c, _) in pasos:
            if r < self.n_orig and c < self.n_dest:
                self.entries_costo[r][c].configure(bg=ALLOC_BG, fg="white")

        self._write_results_rich(nombres_orig, nombres_dest,
                                  costos, asig, pasos,
                                  oferta, demanda, costo,
                                  fic_orig, fic_dest)
        self._ultimo_resultado = {
            "nombres_orig": nombres_orig,
            "nombres_dest": nombres_dest,
            "costos":       costos,
            "oferta":       oferta,
            "demanda":      demanda,
            "asig":         asig,
            "pasos":        pasos,
            "costo":        costo,
            "fic_orig":     fic_orig,
            "fic_dest":     fic_dest,
        }

    def _reset_cell_colors(self):
        for fila in self.entries_costo:
            for e in fila:
                e.configure(bg=CARD, fg=TEXT)

    def _write_results(self, text, tags=None):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        if tags:
            self.result_text.insert("end", text, tags)
        else:
            self.result_text.insert("end", text)
        self.result_text.configure(state="disabled")

    def _write_results_rich(self, nombres_orig, nombres_dest,
                             costos, asig, pasos,
                             oferta, demanda, costo,
                             fic_orig, fic_dest):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")

        ins = self.result_text.insert

        ins("end", "═" * 36 + "\n", "muted")
        ins("end", " SOLUCIÓN BÁSICA FACTIBLE INICIAL\n", "title")
        ins("end", " Método de la Esquina Noroeste\n", "muted")
        ins("end", "═" * 36 + "\n\n", "muted")

        if fic_orig:
            total_of  = sum(oferta)
            total_dem = sum(demanda)
            ins("end", f"⚠ Problema desbalanceado\n", "warn")
            ins("end", f"  Oferta total  : {total_of}\n", "muted")
            ins("end", f"  Demanda total : {total_dem}\n", "muted")
            ins("end", f"  Origen ficticio añadido ({total_dem - total_of})\n\n", "warn")
        elif fic_dest:
            total_of  = sum(oferta)
            total_dem = sum(demanda)
            ins("end", f"⚠ Problema desbalanceado\n", "warn")
            ins("end", f"  Oferta total  : {total_of}\n", "muted")
            ins("end", f"  Demanda total : {total_dem}\n", "muted")
            ins("end", f"  Destino ficticio añadido ({total_of - total_dem})\n\n", "warn")
        else:
            ins("end", "✔ Problema balanceado\n\n", "success")

        ins("end", "Asignaciones:\n", "title")
        ins("end", "─" * 36 + "\n", "muted")

        step_num = 1
        for (r, c, cant) in pasos:
            orig_name = nombres_orig[r] if r < len(nombres_orig) else f"Ficticio"
            dest_name = nombres_dest[c] if c < len(nombres_dest) else f"Ficticio"
            if r < self.n_orig and c < self.n_dest:
                cst = costos[r][c]
                subtotal = cant * cst
                ins("end", f" {step_num:>2}. ", "muted")
                ins("end", f"{orig_name} → {dest_name}\n", "value")
                ins("end", f"     Cantidad : {cant:.0f}\n", "")
                ins("end", f"     Costo    : {cst} × {cant:.0f} = {subtotal:.2f}\n", "muted")
                step_num += 1

        ins("end", "\n" + "═" * 36 + "\n", "muted")
        ins("end", f" Costo total estimado:\n", "title")
        ins("end", f" $ {costo:.2f}\n", "success")
        ins("end", "═" * 36 + "\n", "muted")

        self.result_text.configure(state="disabled")

    def analizar_ia(self):
        if self._ultimo_resultado is None:
            messagebox.showwarning("Aviso", "Primero resuelve el problema para analizarlo.")
            return

        d = self._ultimo_resultado

        asignaciones_txt = []
        for (r, c, cant) in d["pasos"]:
            if r < self.n_orig and c < self.n_dest:
                oname = d["nombres_orig"][r]
                dname = d["nombres_dest"][c]
                cu    = d["costos"][r][c]
                asignaciones_txt.append(
                    f"  {oname} → {dname}: {cant:.0f} unidades @ costo {cu} (subtotal {cant*cu:.2f})"
                )
        balance = (
            f"Origen ficticio añadido ({sum(d['demanda'])-sum(d['oferta'])})" if d["fic_orig"]
            else f"Destino ficticio añadido ({sum(d['oferta'])-sum(d['demanda'])})" if d["fic_dest"]
            else "Problema balanceado"
        )

        prompt = (
            "Eres un experto en programación matemática y métodos de transporte.\n"
            "Se resolvió un problema de transporte usando el Método de la Esquina Noroeste.\n\n"
            f"Orígenes: {d['nombres_orig']}\n"
            f"Destinos: {d['nombres_dest']}\n"
            f"Oferta:   {d['oferta']}\n"
            f"Demanda:  {d['demanda']}\n"
            f"Balance:  {balance}\n\n"
            f"Asignaciones realizadas:\n" + "\n".join(asignaciones_txt) + "\n\n"
            f"Costo total de la solución inicial: ${d['costo']:.2f}\n\n"
            "Por favor:\n"
            "1. Explica brevemente qué hizo el método paso a paso.\n"
            "2. Interpreta si la solución parece razonable.\n"
            "3. Indica si se recomienda optimizar con MODI o Stepping-Stone.\n"
            "Responde en español, de forma concisa (máx. 200 palabras)."
        )

        try:
            respuesta = groq_client.consultar_groq(prompt, max_tokens=400)
            self._mostrar_ia(respuesta, error=False)
        except RuntimeError as e:
            self._mostrar_ia(str(e), error=True)

    def _mostrar_ia(self, texto: str, error: bool):
        self.result_text.configure(state="normal")
        if error:
            self.result_text.insert("end", f"\n Error: {texto}\n", "warn")
        else:
            self.result_text.insert("end", "\n", "")
            for linea in texto.splitlines():
                self.result_text.insert("end", linea + "\n", "ia")
        self.result_text.insert("end", "─" * 36 + "\n", "muted")
        self.result_text.configure(state="disabled")
        self.result_text.see("end")

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
        self._write_results("Tabla limpiada.\n")

if __name__ == "__main__":
    app = App()
    app.mainloop()

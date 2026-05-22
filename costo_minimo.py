import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import groq_client

def costo_minimo(costos, oferta, demanda):
    oferta_actual  = list(oferta)
    demanda_actual = list(demanda)
    filas    = len(costos)
    columnas = len(costos[0])
    asignaciones   = [[0]*columnas for _ in range(filas)]
    filas_tachadas = set()
    cols_tachadas  = set()
    pasos = []

    while len(filas_tachadas) < filas and len(cols_tachadas) < columnas:
        min_costo = float('inf')
        for f in range(filas):
            if f in filas_tachadas:
                continue
            for c in range(columnas):
                if c in cols_tachadas:
                    continue
                if costos[f][c] < min_costo:
                    min_costo = costos[f][c]

        f_min = c_min = -1
        mejor_q = -1
        mejor_peso = -1
        for f in range(filas):
            if f in filas_tachadas:
                continue
            for c in range(columnas):
                if c in cols_tachadas:
                    continue
                if costos[f][c] != min_costo:
                    continue
                q = min(oferta_actual[f], demanda_actual[c])
                peso = max(oferta_actual[f], demanda_actual[c])
                if q > mejor_q or (q == mejor_q and peso > mejor_peso):
                    mejor_q = q
                    mejor_peso = peso
                    f_min, c_min = f, c
        if f_min == -1:
            break
        cantidad = min(oferta_actual[f_min], demanda_actual[c_min])
        asignaciones[f_min][c_min] = cantidad
        pasos.append((f_min, c_min, cantidad, min_costo))
        oferta_actual[f_min]  -= cantidad
        demanda_actual[c_min] -= cantidad
        if oferta_actual[f_min] == 0 and demanda_actual[c_min] == 0:
            filas_tachadas.add(f_min)
        elif oferta_actual[f_min] == 0:
            filas_tachadas.add(f_min)
        else:
            cols_tachadas.add(c_min)

    costo_total = sum(asignaciones[f][c]*costos[f][c]
                      for f in range(filas) for c in range(columnas))
    return asignaciones, costo_total, pasos

BG        = "#0f1117"
SURFACE   = "#1a1d27"
CARD      = "#21253a"
ACCENT    = "#10b981"  
ACCENT2   = "#34d399"
TEXT      = "#e2e8f0"
MUTED     = "#64748b"
SUCCESS   = "#22c55e"
WARNING   = "#f59e0b"
HEADER_BG = "#0d2b1f"
ALLOC_BG  = "#0d2b1f"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Método de Costo Mínimo")
        self.configure(bg=BG)
        self.geometry("1120x740")
        self.resizable(True, True)
        try:
            self.state('zoomed')
        except tk.TclError:
            try:
                self.attributes('-zoomed', True)
            except tk.TclError:
                pass

        self.base_font  = tkfont.Font(family="Segoe UI", size=10)
        self.bold_font  = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.title_font = tkfont.Font(family="Segoe UI", size=17, weight="bold")
        self.small_font = tkfont.Font(family="Segoe UI", size=9)

        self._styles()
        self._header()
        self._config_bar()
        self._main_area()
        self._footer()

        self.n_orig = self.n_dest = 0
        self.e_costos = []
        self.e_oferta = []
        self.e_demanda = []
        self.e_rnames = []
        self.e_cnames = []

    def _styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame",      background=BG)
        s.configure("TLabel",      background=BG,   foreground=TEXT, font=self.base_font)
        s.configure("Accent.TButton", background=ACCENT, foreground="#0f1117",
                    font=self.bold_font, relief="flat", padding=(14, 7))
        s.map("Accent.TButton", background=[("active", ACCENT2)])
        s.configure("Sec.TButton", background=CARD, foreground=TEXT,
                    font=self.base_font, relief="flat", padding=(10, 5))
        s.map("Sec.TButton", background=[("active", SURFACE)])

    def _header(self):
        f = tk.Frame(self, bg=SURFACE, pady=14)
        f.pack(fill="x")
        tk.Label(f, text="◆  Método de Costo Mínimo", font=self.title_font,
                 bg=SURFACE, fg=ACCENT2).pack(side="left", padx=22)
        tk.Label(f, text="Solución básica factible inicial por menor costo global",
                 font=self.small_font, bg=SURFACE, fg=MUTED).pack(side="left")

    def _config_bar(self):
        bar = tk.Frame(self, bg=CARD, pady=10, padx=18)
        bar.pack(fill="x")

        for lbl, attr, default in [("Orígenes:", "spin_orig", "3"),
                                    ("Destinos:", "spin_dest", "3")]:
            tk.Label(bar, text=lbl, bg=CARD, fg=TEXT, font=self.base_font).pack(side="left")
            sp = tk.Spinbox(bar, from_=2, to=8, width=4, bg=SURFACE, fg=TEXT,
                            buttonbackground=SURFACE, relief="flat",
                            font=self.base_font, insertbackground=TEXT)
            sp.delete(0, "end"); sp.insert(0, default)
            sp.pack(side="left", padx=(3, 16))
            setattr(self, attr, sp)

        ttk.Button(bar, text="⟳  Generar tabla", style="Accent.TButton",
                   command=self.generar).pack(side="left", padx=6)
        ttk.Button(bar, text="▶  Resolver", style="Accent.TButton",
                   command=self.resolver).pack(side="left", padx=4)
        ttk.Button(bar, text="↺  Limpiar", style="Sec.TButton",
                   command=self.limpiar).pack(side="left", padx=4)
        ttk.Button(bar, text="🤖  Analizar con Groq", style="Accent.TButton",
                   command=self.analizar_ia).pack(side="left", padx=6)

    def _main_area(self):
        self.paned = tk.PanedWindow(self, orient="horizontal", bg=BG,
                                    sashwidth=5, sashrelief="flat")
        self.paned.pack(fill="both", expand=True)

        left = tk.Frame(self.paned, bg=BG)
        self.paned.add(left, minsize=520, stretch="always")

        left.rowconfigure(0, weight=1)
        left.rowconfigure(1, weight=0)
        left.columnconfigure(0, weight=1)
        left.columnconfigure(1, weight=0)

        self.canvas = tk.Canvas(left, bg=BG, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vs = tk.Scrollbar(left, orient="vertical",   command=self.canvas.yview, bg=SURFACE)
        hs = tk.Scrollbar(left, orient="horizontal", command=self.canvas.xview, bg=SURFACE)
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.tbl = tk.Frame(self.canvas, bg=BG)
        self.canvas.create_window((0, 0), window=self.tbl, anchor="nw")
        self.tbl.bind("<Configure>",
                      lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        right = tk.Frame(self.paned, bg=SURFACE, width=360)
        self.paned.add(right, minsize=300)
        self._results_panel(right)

    def _results_panel(self, parent):
        tk.Label(parent, text="Resultados", font=self.bold_font,
                 bg=SURFACE, fg=ACCENT2, pady=10).pack(fill="x", padx=14)
        tk.Frame(parent, bg=ACCENT, height=2).pack(fill="x", padx=14)
        self.rtxt = tk.Text(parent, bg=SURFACE, fg=TEXT, font=self.small_font,
                            relief="flat", wrap="word", state="disabled",
                            insertbackground=TEXT, selectbackground=ACCENT,
                            pady=8, padx=10)
        self.rtxt.pack(fill="both", expand=True, padx=4, pady=6)
        self.rtxt.tag_config("title",   foreground=ACCENT2, font=self.bold_font)
        self.rtxt.tag_config("success", foreground=SUCCESS, font=self.bold_font)
        self.rtxt.tag_config("warn",    foreground=WARNING)
        self.rtxt.tag_config("muted",   foreground=MUTED,  font=self.small_font)
        self.rtxt.tag_config("value",   foreground=ACCENT2)
        self.rtxt.tag_config("ia",      foreground="#a5f3fc", font=self.small_font)
        self.rtxt.tag_config("ia_title",foreground="#38bdf8", font=self.bold_font)

        self._ultimo_resultado = None

    def _footer(self):
        f = tk.Frame(self, bg=SURFACE, pady=5)
        f.pack(fill="x", side="bottom")
        tk.Label(f, text="ℹ El método de Costo Mínimo selecciona siempre la celda de menor costo global disponible.",
                 font=self.small_font, bg=SURFACE, fg=MUTED).pack()

    def generar(self):
        try:
            no = int(self.spin_orig.get())
            nd = int(self.spin_dest.get())
        except ValueError:
            messagebox.showerror("Error", "Valores numéricos requeridos."); return
        if not (2 <= no <= 8 and 2 <= nd <= 8):
            messagebox.showerror("Error", "Rango: 2–8."); return

        self.n_orig, self.n_dest = no, nd
        for w in self.tbl.winfo_children():
            w.destroy()
        self.e_costos = []
        self.e_oferta = []
        self.e_demanda = []
        self.e_rnames = []
        self.e_cnames = []

        P = 4
        tk.Label(self.tbl, text="", bg=BG, width=13).grid(row=0, column=0, padx=P, pady=P)
        for j in range(nd):
            e = self._entry(100, f"Destino {j+1}", HEADER_BG, ACCENT2, bold=True)
            e.grid(row=0, column=j+1, padx=P, pady=P)
            self.e_cnames.append(e)
        tk.Label(self.tbl, text="Oferta", bg=HEADER_BG, fg=SUCCESS,
                 font=self.bold_font, width=10).grid(row=0, column=nd+1, padx=P, pady=P)

        for i in range(no):
            e = self._entry(100, f"Origen {i+1}", HEADER_BG, ACCENT2, bold=True)
            e.grid(row=i+1, column=0, padx=P, pady=P)
            self.e_rnames.append(e)
            fila = []
            for j in range(nd):
                ec = self._entry(78, "0", CARD, TEXT)
                ec.grid(row=i+1, column=j+1, padx=P, pady=P)
                fila.append(ec)
            self.e_costos.append(fila)
            eo = self._entry(88, "0", "#0f2d1a", SUCCESS)
            eo.grid(row=i+1, column=nd+1, padx=P, pady=P)
            self.e_oferta.append(eo)

        tk.Label(self.tbl, text="Demanda", bg=HEADER_BG, fg=WARNING,
                 font=self.bold_font, width=13).grid(row=no+1, column=0, padx=P, pady=P)
        for j in range(nd):
            ed = self._entry(78, "0", "#2d1b00", WARNING)
            ed.grid(row=no+1, column=j+1, padx=P, pady=P)
            self.e_demanda.append(ed)
        tk.Label(self.tbl, text="—", bg=BG, fg=MUTED).grid(
            row=no+1, column=nd+1, padx=P, pady=P)

        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._write("Tabla lista. Ingresa los valores y presiona ▶ Resolver.\n")

    def _entry(self, px, default, bg, fg, bold=False):
        f = tkfont.Font(family="Segoe UI", size=10, weight="bold" if bold else "normal")
        e = tk.Entry(self.tbl, width=max(int(px//8), 6), bg=bg, fg=fg, font=f,
                     relief="flat", bd=0, insertbackground=fg, justify="center",
                     highlightthickness=1, highlightbackground=MUTED,
                     highlightcolor=ACCENT)
        e.insert(0, default)
        return e

    def _leer_datos(self):
        nombres_o = [e.get().strip() or f"O{i+1}" for i,e in enumerate(self.e_rnames)]
        nombres_d = [e.get().strip() or f"D{j+1}" for j,e in enumerate(self.e_cnames)]
        costos  = [[float(self.e_costos[i][j].get()) for j in range(self.n_dest)]
                   for i in range(self.n_orig)]
        oferta  = [float(e.get()) for e in self.e_oferta]
        demanda = [float(e.get()) for e in self.e_demanda]
        return nombres_o, nombres_d, costos, oferta, demanda

    def resolver(self):
        if not self.e_costos:
            messagebox.showwarning("Aviso", "Primero genera la tabla."); return
        try:
            no, nd, costos, oferta, demanda = self._leer_datos()
        except ValueError:
            messagebox.showerror("Error", "Todos los campos deben ser números."); return

        tot_o, tot_d = sum(oferta), sum(demanda)
        costos_bal = [list(f) for f in costos]
        oferta_bal = list(oferta)
        demanda_bal = list(demanda)
        fic_orig = fic_dest = False

        if tot_o > tot_d:
            for fila in costos_bal:
                fila.append(0)
            demanda_bal.append(tot_o - tot_d)
            fic_dest = True
        elif tot_d > tot_o:
            costos_bal.append([0] * len(demanda_bal))
            oferta_bal.append(tot_d - tot_o)
            fic_orig = True

        asig, total, pasos = costo_minimo(costos_bal, oferta_bal, demanda_bal)

        for f in self.e_costos:
            for e in f: e.configure(bg=CARD, fg=TEXT)
        for (r, c, _, _) in pasos:
            if r < self.n_orig and c < self.n_dest:
                self.e_costos[r][c].configure(bg=ALLOC_BG, fg=ACCENT2)

        rt = self.rtxt
        rt.configure(state="normal"); rt.delete("1.0","end")
        ins = rt.insert
        ins("end","═"*38+"\n","muted")
        ins("end","MÉTODO DE COSTO MÍNIMO\n","title")
        ins("end","═"*38+"\n\n","muted")
        if fic_orig:
            ins("end",f"⚠ Origen ficticio añadido ({tot_d-tot_o})\n\n","warn")
        elif fic_dest:
            ins("end",f"⚠ Destino ficticio añadido ({tot_o-tot_d})\n\n","warn")
        else:
            ins("end","✔ Problema balanceado\n\n","success")

        ins("end","Iteraciones:\n","title")
        ins("end","─"*38+"\n","muted")
        for k,(r,c,cant,cu) in enumerate(pasos,1):
            if r>=self.n_orig or c>=self.n_dest: continue
            ins("end",f" Iter {k}\n","value")
            ins("end",f"  Celda mín: {no[r]} → {nd[c]}  (costo={cu})\n","muted")
            ins("end",f"  Asignado : {cant:.0f} unidades\n","")
            ins("end",f"  Subtotal : {cant*cu:.2f}\n","muted")
            ins("end","  "+"·"*34+"\n","muted")

        ins("end","\n"+"═"*38+"\n","muted")
        ins("end"," Costo total:\n","title")
        ins("end",f" $ {total:.2f}\n","success")
        ins("end","═"*38+"\n","muted")
        rt.configure(state="disabled")

        self._ultimo_resultado = {
            "nombres_orig": no,
            "nombres_dest": nd,
            "costos":       costos,
            "oferta":       oferta,
            "demanda":      demanda,
            "pasos":        pasos,
            "costo":        total,
            "fic_orig":     fic_orig,
            "fic_dest":     fic_dest,
        }

    def limpiar(self):
        for f in self.e_costos:
            for e in f: e.delete(0,"end"); e.insert(0,"0"); e.configure(bg=CARD,fg=TEXT)
        for e in self.e_oferta+self.e_demanda:
            e.delete(0,"end"); e.insert(0,"0")
        self._ultimo_resultado = None
        self._write("Tabla limpiada.\n")

    def _write(self, txt):
        self.rtxt.configure(state="normal")
        self.rtxt.delete("1.0","end")
        self.rtxt.insert("end", txt)
        self.rtxt.configure(state="disabled")

    def analizar_ia(self):
        if self._ultimo_resultado is None:
            messagebox.showwarning("Aviso", "Primero resuelve el problema para analizarlo.")
            return

        d = self._ultimo_resultado

        asignaciones_txt = []
        for (r, c, cant, cu) in d["pasos"]:
            if r < self.n_orig and c < self.n_dest:
                oname = d["nombres_orig"][r]
                dname = d["nombres_dest"][c]
                asignaciones_txt.append(
                    f"  {oname} → {dname}: {cant:.0f} unidades @ costo {cu:.2f} (subtotal {cant*cu:.2f})"
                )
        balance = (
            f"Origen ficticio añadido ({sum(d['demanda'])-sum(d['oferta'])})" if d["fic_orig"]
            else f"Destino ficticio añadido ({sum(d['oferta'])-sum(d['demanda'])})" if d["fic_dest"]
            else "Problema balanceado"
        )

        prompt = (
            "Eres un experto en programación matemática y métodos de transporte.\n"
            "Se resolvió un problema de transporte usando el Método de Costo Mínimo (menor costo global).\n\n"
            f"Orígenes: {d['nombres_orig']}\n"
            f"Destinos: {d['nombres_dest']}\n"
            f"Oferta:   {d['oferta']}\n"
            f"Demanda:  {d['demanda']}\n"
            f"Balance:  {balance}\n\n"
            f"Asignaciones realizadas (por orden de menor costo global):\n" + "\n".join(asignaciones_txt) + "\n\n"
            f"Costo total de la solución inicial: ${d['costo']:.2f}\n\n"
            "Por favor:\n"
            "1. Explica brevemente cómo el método seleccionó las celdas paso a paso.\n"
            "2. Interpreta si la solución obtenida es de buena calidad comparada con otros métodos iniciales.\n"
            "3. Indica si se recomienda optimizar con MODI o Stepping-Stone.\n"
            "Responde en español, de forma concisa (máx. 200 palabras)."
        )

        rt = self.rtxt
        rt.configure(state="normal")
        rt.insert("end", "\n\n" + "─" * 38 + "\n", "muted")
        rt.insert("end", " 🤖 Analizando con Groq AI...\n", "ia_title")
        rt.insert("end", " (llama-3.1-8b-instant)\n", "muted")
        rt.configure(state="disabled")
        rt.see("end")

        try:
            respuesta = groq_client.consultar_groq(prompt, max_tokens=400)
            self._mostrar_ia(respuesta, error=False)
        except RuntimeError as e:
            self._mostrar_ia(str(e), error=True)

    def _mostrar_ia(self, texto: str, error: bool):
        rt = self.rtxt
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

if __name__ == "__main__":
    App().mainloop()

import customtkinter as ctk
import pandas as pd
from procyclingstats import Team, Rider, Race
from tkinter import ttk
import utilidades as herramientas

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Cycling Team Viewer")
        self.geometry("800x600")
        # Obtener listado de carreras desde utilidades.cargar_excell_carreras()
        df_carreras = herramientas.cargar_lista_carreras()
        df_carreras = df_carreras.copy() if isinstance(df_carreras, pd.DataFrame) else pd.DataFrame(columns=["valor","hipervinculo"])
        df_carreras.sort_values(by="carrera", inplace=True)
        # Si devuelve un DataFrame directamente
        if "carrera" in df_carreras.columns:
            specialities = df_carreras["carrera"].dropna().astype(str).tolist()
        elif "url" in df_carreras.columns:
            specialities = df_carreras["url"].dropna().astype(str).tolist()

        # fallback si no hay nada
        if not specialities: # type: ignore
            specialities = ["(sin carreras)"]
        self.specialities = specialities

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.controls_frame = ctk.CTkFrame(self.main_frame)
        self.controls_frame.pack(pady=10, padx=10, fill="x")

        self.specialty_label = ctk.CTkLabel(self.controls_frame, text="Select carrera:")
        self.specialty_label.pack(side="left", padx=5)

        self.specialty_var = ctk.StringVar(value=self.specialities[0])
        self.specialty_menu = ctk.CTkOptionMenu(self.controls_frame, variable=self.specialty_var, values=self.specialities)
        self.specialty_menu.pack(side="left", padx=5)

        # No ejecutar load_riders al construir el botón. Si la función existe, la llamamos al pulsar.
        self.load_button = ctk.CTkButton(self.controls_frame, text="cargar", command=self.on_cargar)
        self.load_button.pack(side="left", padx=20)

        self.tree_frame = ctk.CTkFrame(self.main_frame)
        self.tree_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill="both", expand=True)


    def on_cargar(self):
        """
        Obtiene el valor seleccionado, busca su hipervínculo en self.df_carreras,
        pide a utilidades.buscar_resultados_carrera() los resultados y los muestra en el Treeview.
        """
        seleccionado = self.specialty_var.get()
        # buscar primera fila cuyo 'valor' coincida
        df = self.df_carreras # type: ignore
        fila = df[df["nombre"].astype(str) == str(seleccionado)]
        hiperv = None
        if not fila.empty:
            hiperv = fila.iloc[0]["url"]
        # si no hay hipervínculo, pasar el texto seleccionado (puede ser slug)
        consulta = hiperv if hiperv else seleccionado   
        
        resultados = herramientas.buscar_resultados_carrera(consulta[32:len(consulta)])
        df_results = pd.DataFrame(resultados)
       
        # limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
         
        if resultados is None or resultados.empty:
            # mostrar una fila simple con mensaje
            self.tree["columns"] = ("mensaje",)
            self.tree.heading("mensaje", text="Mensaje")
           #self.tree.column("mensaje", width=600)
            self.tree.insert("", "end", values=("No se han obtenido resultados.",))
            return

        # poblar columnas desde DataFrame
        cols = list(resultados.columns)
       
        self.tree["columns"] = cols
        # quitar el column #0
        self.tree["show"] = "headings"
        for c in cols:
            #self.tree.heading(c, text=c)
            self.tree.column(c, width=120)
        # insertar filas
        
        for _, row in resultados.iterrows():
            values = [row.get(c, "") for c in cols]
            self.tree.insert("", "end", values=values)
        

if __name__ == "__main__":
    app = App()
    app.mainloop()

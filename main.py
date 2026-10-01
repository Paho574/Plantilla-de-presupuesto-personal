import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from data_manager import DataManager
from ui_components import (
    TarjetaMetrica, FormularioTransaccion, 
    TablaTransacciones, FormularioTopes, VisualizadorMetas, FiltroFechas, BuscadorTabla
)

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión de Presupuesto Personal y Metas")
        self.setMinimumSize(1000, 750)

        self.data_manager = DataManager("data.json")
        self.presupuesto = self.data_manager.cargar()
        
        # Variables de estado para los filtros de fecha
        self.filtro_inicio = None
        self.filtro_fin = None
        
        # Variables de estado para la búsqueda rápida en tabla
        self.filtro_texto = ""
        self.filtro_tipo = "Todos"
        self.filtro_categoria = "Todas"

        self.init_ui()
        self.actualizar_interfaz()

    def init_ui(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setSpacing(14)
        layout_principal.setContentsMargins(18, 18, 18, 18)

        # Panel de Filtros por fecha
        self.filtro_fechas = FiltroFechas(self.aplicar_filtro_fechas)
        layout_principal.addWidget(self.filtro_fechas)

        # Panel superior: Métricas
        layout_metricas = QHBoxLayout()
        self.tarjeta_ingresos = TarjetaMetrica("TOTAL INGRESOS", "$0.00")
        self.tarjeta_gastos = TarjetaMetrica("TOTAL GASTOS", "$0.00")
        self.tarjeta_balance = TarjetaMetrica("BALANCE NETO", "$0.00")

        layout_metricas.addWidget(self.tarjeta_ingresos)
        layout_metricas.addWidget(self.tarjeta_gastos)
        layout_metricas.addWidget(self.tarjeta_balance)
        layout_principal.addLayout(layout_metricas)

        # Panel para configurar topes por categoría
        categorias_gasto = ["Alimentación", "Servicios", "Transporte", "Ocio", "Educación", "Salud"]
        self.formulario_topes = FormularioTopes(categorias_gasto, self.establecer_tope)
        layout_principal.addWidget(self.formulario_topes)

        # Semáforo de metas e indicadores visuales
        self.visualizador_metas = VisualizadorMetas()
        layout_principal.addWidget(self.visualizador_metas)

        # Formulario de entrada de transacciones
        self.formulario_tx = FormularioTransaccion(self.agregar_transaccion)
        layout_principal.addWidget(self.formulario_tx)

        # Buscador y filtros rápidos de tabla
        self.buscador_tabla = BuscadorTabla(self.aplicar_busqueda_tabla)
        layout_principal.addWidget(self.buscador_tabla)

        # Tabla de transacciones
        self.tabla = TablaTransacciones(self.eliminar_transaccion)
        layout_principal.addWidget(self.tabla)

    def aplicar_filtro_fechas(self, inicio, fin):
        self.filtro_inicio = inicio
        self.filtro_fin = fin
        self.actualizar_interfaz()

    def aplicar_busqueda_tabla(self, texto, tipo, categoria):
        self.filtro_texto = texto
        self.filtro_tipo = tipo
        self.filtro_categoria = categoria
        self.actualizar_interfaz()

    def agregar_transaccion(self, transaccion):
        self.presupuesto.agregar_transaccion(transaccion)
        self.data_manager.guardar(self.presupuesto)
        self.actualizar_interfaz()

    def eliminar_transaccion(self, id_transaccion):
        exito = self.presupuesto.eliminar_transaccion(id_transaccion)
        if exito:
            self.data_manager.guardar(self.presupuesto)
            self.actualizar_interfaz()

    def establecer_tope(self, categoria, monto):
        self.presupuesto.establecer_tope(categoria, monto)
        self.data_manager.guardar(self.presupuesto)
        self.actualizar_interfaz()

    def actualizar_interfaz(self):
        # 0. Extraer transacciones con base en todos los filtros activos (fechas + buscador)
        txs_filtradas = self.presupuesto.obtener_transacciones_filtradas(
            self.filtro_inicio, 
            self.filtro_fin,
            self.filtro_texto,
            self.filtro_tipo,
            self.filtro_categoria
        )

        # 1. Tabla de transacciones (muestra únicamente lo que coincide con los filtros)
        self.tabla.poblar_tabla(txs_filtradas)

        # 2. Métricas globales calculadas con la data filtrada
        balances = self.presupuesto.calcular_balance(txs_filtradas)
        self.tarjeta_ingresos.actualizar_valor(f"${balances['ingresos']:.2f}", "#36B37E")
        self.tarjeta_gastos.actualizar_valor(f"${balances['gastos']:.2f}", "#FF5630")

        color_balance = "#36B37E" if balances["balance"] >= 0 else "#FF5630"
        self.tarjeta_balance.actualizar_valor(f"${balances['balance']:.2f}", color_balance)

        # 3. Semáforo y barras de progreso por tope de categoría
        estados = self.presupuesto.obtener_estado_topes(txs_filtradas)
        self.visualizador_metas.actualizar_panel(estados)

def cargar_estilos(app, ruta_qcss="styles.qcss"):
    if os.path.exists(ruta_qcss):
        with open(ruta_qcss, "r", encoding="utf-8") as f:
            estilo = f.read()
            app.setStyleSheet(estilo)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    cargar_estilos(app, "styles.qcss")

    ventana = VentanaPrincipal()
    ventana.show()

    sys.exit(app.exec_())

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QFrame, QMessageBox,
    QProgressBar, QScrollArea, QGroupBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from models import Transaccion
from datetime import datetime, timedelta

class TarjetaMetrica(QFrame):
    def __init__(self, titulo, valor_inicial="0.00 $"):
        super().__init__()
        self.setObjectName("tarjetaMetrica")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setObjectName("etiquetaMetricaTitulo")

        self.lbl_valor = QLabel(valor_inicial)
        self.lbl_valor.setObjectName("etiquetaMetricaValor")

        layout.addWidget(self.lbl_titulo)
        layout.addWidget(self.lbl_valor)

    def actualizar_valor(self, nuevo_valor, color=None):
        self.lbl_valor.setText(str(nuevo_valor))
        if color:
            self.lbl_valor.setStyleSheet(f"color: {color};")

class FiltroFechas(QGroupBox):
    def __init__(self, callback_aplicar):
        super().__init__("Filtros y Métricas de Tiempo")
        self.callback_aplicar = callback_aplicar
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems([
            "Todos los tiempos", 
            "Mes actual", 
            "Mes anterior", 
            "Año actual", 
            "Rango personalizado"
        ])
        self.combo_periodo.currentIndexChanged.connect(self.cambio_periodo)
        
        # Calendario Inicio
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDate(QDate.currentDate())
        self.date_inicio.setVisible(False)
        
        # Calendario Fin
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate())
        self.date_fin.setVisible(False)
        
        self.lbl_hasta = QLabel(" hasta ")
        self.lbl_hasta.setVisible(False)
        
        self.btn_aplicar = QPushButton("Filtrar")
        self.btn_aplicar.clicked.connect(self.aplicar)
        
        layout.addWidget(QLabel("Visualizar período:"))
        layout.addWidget(self.combo_periodo)
        layout.addWidget(self.date_inicio)
        layout.addWidget(self.lbl_hasta)
        layout.addWidget(self.date_fin)
        layout.addWidget(self.btn_aplicar)
        layout.addStretch()

    def cambio_periodo(self):
        texto = self.combo_periodo.currentText()
        es_personalizado = (texto == "Rango personalizado")
        self.date_inicio.setVisible(es_personalizado)
        self.date_fin.setVisible(es_personalizado)
        self.lbl_hasta.setVisible(es_personalizado)

    def aplicar(self):
        texto = self.combo_periodo.currentText()
        hoy = datetime.now()
        
        if texto == "Todos los tiempos":
            inicio, fin = None, None
        elif texto == "Mes actual":
            inicio = datetime(hoy.year, hoy.month, 1)
            fin = datetime.now()
        elif texto == "Mes anterior":
            primer_dia_mes_actual = datetime(hoy.year, hoy.month, 1)
            ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
            inicio = datetime(ultimo_dia_mes_anterior.year, ultimo_dia_mes_anterior.month, 1)
            fin = datetime(ultimo_dia_mes_anterior.year, ultimo_dia_mes_anterior.month, ultimo_dia_mes_anterior.day, 23, 59, 59)
        elif texto == "Año actual":
            inicio = datetime(hoy.year, 1, 1)
            fin = datetime.now()
        else: # Rango personalizado
            q_inicio = self.date_inicio.date()
            q_fin = self.date_fin.date()
            inicio = datetime(q_inicio.year(), q_inicio.month(), q_inicio.day())
            fin = datetime(q_fin.year(), q_fin.month(), q_fin.day(), 23, 59, 59)
            
        self.callback_aplicar(inicio, fin)

class FormularioTransaccion(QWidget):
    def __init__(self, callback_agregar):
        super().__init__()
        self.callback_agregar = callback_agregar
        self.categorias_gasto = ["Alimentación", "Servicios", "Transporte", "Ocio", "Educación", "Salud"]
        self.categorias_ingreso = ["Salario", "Inversiones", "Freelance", "Venta", "Otros"]
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.input_concepto = QLineEdit()
        self.input_concepto.setPlaceholderText("Concepto o descripción...")

        self.input_monto = QLineEdit()
        self.input_monto.setPlaceholderText("Monto (ej. 45.50)...")

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Gasto", "Ingreso"])
        self.combo_tipo.currentIndexChanged.connect(self.actualizar_categorias)

        self.combo_categoria = QComboBox()
        self.actualizar_categorias()

        self.btn_guardar = QPushButton("Registrar")
        self.btn_guardar.clicked.connect(self.enviar_datos)

        layout.addWidget(self.input_concepto, 3)
        layout.addWidget(self.input_monto, 2)
        layout.addWidget(self.combo_tipo, 2)
        layout.addWidget(self.combo_categoria, 2)
        layout.addWidget(self.btn_guardar, 2)

    def actualizar_categorias(self):
        self.combo_categoria.clear()
        if self.combo_tipo.currentText() == "Gasto":
            self.combo_categoria.addItems(self.categorias_gasto)
        else:
            self.combo_categoria.addItems(self.categorias_ingreso)

    def enviar_datos(self):
        concepto = self.input_concepto.text().strip()
        monto_str = self.input_monto.text().strip()
        tipo = self.combo_tipo.currentText().lower()
        categoria = self.combo_categoria.currentText()

        if not concepto:
            QMessageBox.warning(self, "Validación", "El concepto no puede estar vacío.")
            return

        try:
            monto = float(monto_str)
            if monto <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Validación", "Ingrese un valor numérico positivo para el monto.")
            return

        nueva_tx = Transaccion(concepto, monto, categoria, tipo)
        self.callback_agregar(nueva_tx)

        self.input_concepto.clear()
        self.input_monto.clear()
        self.input_concepto.setFocus()

class FormularioTopes(QWidget):
    def __init__(self, categorias_disponibles, callback_guardar_tope):
        super().__init__()
        self.callback_guardar_tope = callback_guardar_tope
        self.categorias_disponibles = categorias_disponibles
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_info = QLabel("Definir Tope Mensual:")
        self.lbl_info.setStyleSheet("font-weight: bold; color: #8C9BAE;")

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(self.categorias_disponibles)

        self.input_tope = QLineEdit()
        self.input_tope.setPlaceholderText("Límite máx ($)...")

        self.btn_fijar = QPushButton("Establecer Tope")
        self.btn_fijar.clicked.connect(self.enviar_tope)

        layout.addWidget(self.lbl_info)
        layout.addWidget(self.combo_categoria, 2)
        layout.addWidget(self.input_tope, 2)
        layout.addWidget(self.btn_fijar, 2)

    def enviar_tope(self):
        cat = self.combo_categoria.currentText()
        valor_str = self.input_tope.text().strip()

        try:
            monto = float(valor_str)
            if monto <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Validación", "Ingrese un monto límite numérico mayor a 0.")
            return

        self.callback_guardar_tope(cat, monto)
        self.input_tope.clear()

class VisualizadorMetas(QGroupBox):
    def __init__(self):
        super().__init__("Control de Presupuesto y Semáforo de Alertas")
        self.layout_contenedor = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.widget_interior = QWidget()
        self.layout_items = QVBoxLayout(self.widget_interior)
        self.layout_items.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.widget_interior)
        self.layout_contenedor.addWidget(self.scroll_area)

    def actualizar_panel(self, estados_topes):
        while self.layout_items.count():
            hijo = self.layout_items.takeAt(0)
            if hijo.widget():
                hijo.widget().deleteLater()

        if not estados_topes:
            lbl_vacio = QLabel("No hay topes presupuestarios asignados o no hay gastos en este período.")
            lbl_vacio.setStyleSheet("color: #626F86; font-style: italic; padding: 10px;")
            self.layout_items.addWidget(lbl_vacio)
            return

        for categoria, info in estados_topes.items():
            card = QFrame()
            card.setObjectName("itemTope")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(8, 8, 8, 8)

            top_layout = QHBoxLayout()
            lbl_nombre = QLabel(f"<b>{categoria}</b>")
            lbl_status = QLabel(f"[{info['estado_texto'].upper()}]")
            lbl_status.setStyleSheet(f"color: {info['color']}; font-weight: bold;")
            
            lbl_consumo = QLabel(f"${info['gastado']:.2f} / ${info['tope']:.2f} ({info['porcentaje']}%)")
            lbl_consumo.setStyleSheet("color: #A6C5E2;")

            top_layout.addWidget(lbl_nombre)
            top_layout.addWidget(lbl_status)
            top_layout.addStretch()
            top_layout.addWidget(lbl_consumo)

            barra = QProgressBar()
            barra.setRange(0, 100)
            valor_barra = min(int(info['porcentaje']), 100)
            barra.setValue(valor_barra)
            barra.setFormat(f"{info['porcentaje']}%")
            barra.setStyleSheet(f"""
                QProgressBar::chunk {{
                    background-color: {info['color']};
                }}
            """)

            card_layout.addLayout(top_layout)
            card_layout.addWidget(barra)
            self.layout_items.addWidget(card)

# NUEVA CLASE PARA BUSCADOR Y FILTROS RÁPIDOS
class BuscadorTabla(QWidget):
    def __init__(self, callback_buscar):
        super().__init__()
        self.callback_buscar = callback_buscar
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por concepto (ej. pago del aceite)...")
        # Real-time search: se actualiza conforme el usuario escribe
        self.input_buscar.textChanged.connect(self.notificar_cambio)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos", "Ingreso", "Gasto"])
        self.combo_tipo.currentIndexChanged.connect(self.notificar_cambio)

        self.combo_categoria = QComboBox()
        # Se añaden todas las categorías posibles más la opción "Todas"
        self.combo_categoria.addItems([
            "Todas", "Alimentación", "Servicios", "Transporte", "Ocio", 
            "Educación", "Salud", "Salario", "Inversiones", "Freelance", 
            "Venta", "Otros"
        ])
        self.combo_categoria.currentIndexChanged.connect(self.notificar_cambio)

        layout.addWidget(QLabel("Buscar en tabla:"))
        layout.addWidget(self.input_buscar, 3)
        layout.addWidget(QLabel("Tipo:"))
        layout.addWidget(self.combo_tipo, 1)
        layout.addWidget(QLabel("Categoría:"))
        layout.addWidget(self.combo_categoria, 1)

    def notificar_cambio(self):
        texto = self.input_buscar.text().strip()
        tipo = self.combo_tipo.currentText()
        cat = self.combo_categoria.currentText()
        self.callback_buscar(texto, tipo, cat)

class TablaTransacciones(QTableWidget):
    def __init__(self, callback_eliminar):
        super().__init__()
        self.callback_eliminar = callback_eliminar
        self.columnas = ["ID", "Fecha", "Concepto", "Categoría", "Tipo", "Monto", "Acción"]
        self.init_ui()

    def init_ui(self):
        self.setColumnCount(len(self.columnas))
        self.setHorizontalHeaderLabels(self.columnas)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.verticalHeader().setVisible(False)

    def poblar_tabla(self, transacciones):
        self.setRowCount(0)
        for fila, tx in enumerate(transacciones):
            self.insertRow(fila)

            item_id = QTableWidgetItem(tx.id_transaccion)
            item_fecha = QTableWidgetItem(tx.fecha)
            item_concepto = QTableWidgetItem(tx.concepto)
            item_cat = QTableWidgetItem(tx.categoria)
            item_tipo = QTableWidgetItem(tx.tipo.capitalize())
            
            simbolo = "+" if tx.tipo == "ingreso" else "-"
            item_monto = QTableWidgetItem(f"{simbolo} ${tx.monto:.2f}")

            item_monto.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            if tx.tipo == "ingreso":
                item_monto.setForeground(Qt.green)
            else:
                item_monto.setForeground(Qt.red)

            self.setItem(fila, 0, item_id)
            self.setItem(fila, 1, item_fecha)
            self.setItem(fila, 2, item_concepto)
            self.setItem(fila, 3, item_cat)
            self.setItem(fila, 4, item_tipo)
            self.setItem(fila, 5, item_monto)

            btn_del = QPushButton("Eliminar")
            btn_del.setObjectName("btnEliminar")
            btn_del.clicked.connect(lambda _, id_tx=tx.id_transaccion: self.callback_eliminar(id_tx))
            self.setCellWidget(fila, 6, btn_del)
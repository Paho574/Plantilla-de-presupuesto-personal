import math
import time
import random

class Transaccion:
    def __init__(self, concepto, monto, categoria, tipo, fecha=None, id_transaccion=None):
        self.concepto = str(concepto)
        self.monto = float(monto)
        self.categoria = str(categoria)
        self.tipo = str(tipo).lower()  # "ingreso" o "gasto"
        self.id_transaccion = id_transaccion if id_transaccion else self.generar_id()
        self.fecha = fecha if fecha else time.strftime("%Y-%m-%d %H:%M:%S")

    def generar_id(self):
        semilla = int(time.time())
        aleatorio = random.randint(1000, 9999)
        return f"TX-{semilla}-{aleatorio}"

    def to_dict(self):
        return {
            "id": self.id_transaccion,
            "concepto": self.concepto,
            "monto": self.monto,
            "categoria": self.categoria,
            "tipo": self.tipo,
            "fecha": self.fecha
        }

    @staticmethod
    def from_dict(data):
        return Transaccion(
            concepto=data.get("concepto", ""),
            monto=data.get("monto", 0.0),
            categoria=data.get("categoria", ""),
            tipo=data.get("tipo", "gasto"),
            fecha=data.get("fecha"),
            id_transaccion=data.get("id")
        )

class Presupuesto:
    def __init__(self):
        self.transacciones = []
        self.metas_ahorro = {}
        self.topes_categorias = {}  # Formato: {"Alimentación": 250.0, "Servicios": 100.0}

    def agregar_transaccion(self, transaccion):
        if isinstance(transaccion, Transaccion):
            self.transacciones.append(transaccion)

    def eliminar_transaccion(self, id_transaccion):
        longitud_inicial = len(self.transacciones)
        self.transacciones = [t for t in self.transacciones if t.id_transaccion != id_transaccion]
        return len(self.transacciones) < longitud_inicial

    def establecer_tope(self, categoria, monto_tope):
        monto = float(monto_tope)
        if monto > 0:
            self.topes_categorias[categoria] = round(monto, 2)
        elif categoria in self.topes_categorias:
            del self.topes_categorias[categoria]

    def calcular_balance(self):
        total_ingresos = 0.0
        total_gastos = 0.0

        for t in self.transacciones:
            if t.tipo == "ingreso":
                total_ingresos += t.monto
            elif t.tipo == "gasto":
                total_gastos += t.monto

        balance_neto = total_ingresos - total_gastos
        return {
            "ingresos": round(total_ingresos, 2),
            "gastos": round(total_gastos, 2),
            "balance": round(balance_neto, 2)
        }

    def resumen_por_categoria(self):
        resumen = {"ingreso": {}, "gasto": {}}

        for t in self.transacciones:
            tipo = t.tipo
            cat = t.categoria
            if cat not in resumen[tipo]:
                resumen[tipo][cat] = 0.0
            resumen[tipo][cat] += t.monto

        for tipo in resumen:
            for cat in resumen[tipo]:
                resumen[tipo][cat] = round(resumen[tipo][cat], 2)

        return resumen

    def calcular_porcentajes_gastos(self):
        totales = self.calcular_balance()
        gasto_total = totales["gastos"]
        porcentajes = {}

        if gasto_total > 0:
            resumen_gastos = self.resumen_por_categoria()["gasto"]
            for cat, monto in resumen_gastos.items():
                ratio = monto / gasto_total
                porcentajes[cat] = math.floor(ratio * 100 * 100) / 100
        return porcentajes

    def obtener_estado_topes(self):
        """
        Calcula el consumo actual de cada categoría con tope configurado.
        Reglas de semáforo:
        - Verde (#36B37E): < 80%
        - Amarillo (#FFAB00): 80% a 100% (alerta de proximidad)
        - Rojo (#FF5630): > 100% (sobrepasado)
        """
        gastos_por_cat = self.resumen_por_categoria().get("gasto", {})
        estados = {}

        for cat, tope in self.topes_categorias.items():
            gastado = gastos_por_cat.get(cat, 0.0)
            porcentaje = (gastado / tope) * 100 if tope > 0 else 0.0
            porcentaje_redondeado = math.floor(porcentaje * 10) / 10

            if porcentaje < 80.0:
                color = "#36B37E"  # Verde
                estado_texto = "Normal"
            elif porcentaje <= 100.0:
                color = "#FFAB00"  # Amarillo
                estado_texto = "Alerta (Cerca del límite)"
            else:
                color = "#FF5630"  # Rojo
                estado_texto = "Excedido"

            estados[cat] = {
                "tope": tope,
                "gastado": gastado,
                "restante": round(tope - gastado, 2),
                "porcentaje": porcentaje_redondeado,
                "color": color,
                "estado_texto": estado_texto
            }

        return estados
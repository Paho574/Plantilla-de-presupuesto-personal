import json
import os
from models import Transaccion, Presupuesto

class DataManager:
    def __init__(self, ruta_archivo="data.json"):
        self.ruta_archivo = ruta_archivo

    def guardar(self, presupuesto):
        datos_serializables = {
            "configuracion": {
                "moneda": "USD",
                "version": 1.1
            },
            "topes_presupuesto": presupuesto.topes_categorias,
            "transacciones": []
        }

        for t in presupuesto.transacciones:
            datos_serializables["transacciones"].append(t.to_dict())

        try:
            with open(self.ruta_archivo, "w", encoding="utf-8") as f:
                json.dump(datos_serializables, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al persistir la data en JSON: {e}")
            return False

    def cargar(self):
        presupuesto = Presupuesto()

        if not os.path.exists(self.ruta_archivo):
            return presupuesto

        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                contenido = json.load(f)

            # Cargar topes/metas configuradas
            presupuesto.topes_categorias = contenido.get("topes_presupuesto", {})

            # Cargar transacciones
            lista_datos = contenido.get("transacciones", [])
            for item in lista_datos:
                obj_transaccion = Transaccion.from_dict(item)
                presupuesto.agregar_transaccion(obj_transaccion)

        except Exception as e:
            print(f"Error al recuperar la data de JSON: {e}")

        return presupuesto
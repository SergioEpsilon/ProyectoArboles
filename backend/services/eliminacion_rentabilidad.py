from models.node import Node


# ------------------------------------------------------------
# Calcula la rentabilidad de un nodo
# ------------------------------------------------------------
# Usa metadata del nodo:
# rentabilidad = pasajeros * precioFinal - promoción + penalización
#
# Nota:
# - promoción es booleana → se convierte a valor fijo (50)
# - si no hay precioFinal, usa precioBase
def calcular_rentabilidad(nodo):
    metadata = nodo.getMetadata()

    pasajeros = metadata.get("pasajeros", 0)
    precio_final = metadata.get("precioFinal", metadata.get("precioBase", 0))

    promocion_activa = metadata.get("promocion", False)
    valor_promocion = 50 if promocion_activa else 0

    penalizacion = metadata.get("penalizacion", 0)

    return (pasajeros * precio_final) - valor_promocion + penalizacion


# ------------------------------------------------------------
# Compara dos nodos y decide cuál es peor candidato
# ------------------------------------------------------------
# Reglas:
# 1. Menor rentabilidad
# 2. Mayor profundidad
# 3. Mayor código (value)
def es_mejor_candidato(actual, mejor):
    if mejor is None:
        return True

    if actual["rentabilidad"] < mejor["rentabilidad"]:
        return True

    if actual["rentabilidad"] == mejor["rentabilidad"]:
        if actual["profundidad"] > mejor["profundidad"]:
            return True

        if actual["profundidad"] == mejor["profundidad"]:
            if actual["nodo"].getValue() > mejor["nodo"].getValue():
                return True

    return False


# ------------------------------------------------------------
# Recorre el árbol y encuentra el peor nodo
# ------------------------------------------------------------
# Guarda:
# - nodo
# - profundidad
# - rentabilidad
def buscar_menor_rentabilidad(raiz):
    mejor = None

    def recorrer(nodo, padre=None, profundidad=0):
        nonlocal mejor

        if nodo is None:
            return

        actual = {
            "nodo": nodo,
            "padre": padre,
            "profundidad": profundidad,
            "rentabilidad": calcular_rentabilidad(nodo)
        }

        if es_mejor_candidato(actual, mejor):
            mejor = actual

        recorrer(nodo.getLeftChild(), nodo, profundidad + 1)
        recorrer(nodo.getRightChild(), nodo, profundidad + 1)

    recorrer(raiz)
    return mejor


# ------------------------------------------------------------
# Cuenta cuántos nodos tiene una subrama
# ------------------------------------------------------------
def contar_nodos_subarbol(nodo):
    if nodo is None:
        return 0

    return (
        1
        + contar_nodos_subarbol(nodo.getLeftChild())
        + contar_nodos_subarbol(nodo.getRightChild())
    )


# ------------------------------------------------------------
# Recorre el árbol y guarda nodos excepto la subrama eliminada
# ------------------------------------------------------------
def recolectar_nodos_excluyendo_subrama(nodo_actual, nodo_excluir, lista):
    if nodo_actual is None:
        return

    # Si es el nodo a eliminar, se ignora toda la rama
    if nodo_actual == nodo_excluir:
        return

    recolectar_nodos_excluyendo_subrama(
        nodo_actual.getLeftChild(),
        nodo_excluir,
        lista
    )

    lista.append({
        "value": nodo_actual.getValue(),
        "metadata": nodo_actual.getMetadata()
    })

    recolectar_nodos_excluyendo_subrama(
        nodo_actual.getRightChild(),
        nodo_excluir,
        lista
    )


# ------------------------------------------------------------
# Devuelve lista de nodos que sobreviven
# ------------------------------------------------------------
def obtener_nodos_restantes_excluyendo_subrama(raiz, nodo_excluir):
    lista = []
    recolectar_nodos_excluyendo_subrama(raiz, nodo_excluir, lista)
    return lista


# ------------------------------------------------------------
# Reconstruye el AVL con los nodos restantes
# ------------------------------------------------------------
# Se reinicia el árbol y se insertan de nuevo los nodos
def reconstruir_arbol_desde_lista(avl, datos):
    avl.root = None

    for item in datos:
        nuevo_nodo = Node(item["value"], item["metadata"])
        avl.insert(nuevo_nodo)


# ------------------------------------------------------------
# Función principal del punto 8
# ------------------------------------------------------------
# Flujo:
# 1. Buscar nodo peor
# 2. Contar nodos eliminados
# 3. Obtener nodos restantes
# 4. Reconstruir árbol
# 5. Retornar resultado
def cancelar_subrama_menor_rentabilidad(avl):
    candidato = buscar_menor_rentabilidad(avl.root)

    if candidato is None:
        return {
            "exito": False,
            "mensaje": "El árbol está vacío."
        }

    nodo_objetivo = candidato["nodo"]
    cantidad_eliminaciones = contar_nodos_subarbol(nodo_objetivo)

    datos_restantes = obtener_nodos_restantes_excluyendo_subrama(
        avl.root,
        nodo_objetivo
    )

    reconstruir_arbol_desde_lista(avl, datos_restantes)

    return {
        "exito": True,
        "mensaje": "Subrama cancelada con éxito.",
        "codigo_eliminado": nodo_objetivo.getValue(),
        "rentabilidad": candidato["rentabilidad"],
        "profundidad": candidato["profundidad"],
        "nodos_eliminados": cantidad_eliminaciones
    }
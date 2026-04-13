# ------------------------------------------------------------
# 1. Auditar recursivamente el árbol
# ------------------------------------------------------------
# Esta función recorre todo el árbol en postorden:
# primero izquierda, luego derecha y al final el nodo actual.
#
# ¿Por qué postorden?
# Porque para saber si la altura y el balance de un nodo son correctos,
# primero necesitamos conocer las alturas reales de sus hijos.
#
# Parámetros:
# - avl: instancia del árbol AVL
# - nodo: nodo actual que se está auditando
# - inconsistencias: lista donde se guardan los errores encontrados
#
# Retorna:
# - la altura real calculada del nodo actual
def auditar_avl(avl, nodo, inconsistencias):
    # En este AVL, un nodo None tiene altura -1
    # para que una hoja tenga altura 0
    if nodo is None:
        return -1

    # Obtener hijos izquierdo y derecho usando los getters del Node
    hijo_izq = nodo.getLeftChild()
    hijo_der = nodo.getRightChild()

    # Auditar recursivamente ambos subárboles
    altura_izq = auditar_avl(avl, hijo_izq, inconsistencias)
    altura_der = auditar_avl(avl, hijo_der, inconsistencias)

    # Calcular altura real del nodo actual
    altura_real = 1 + max(altura_izq, altura_der)

    # Calcular balance real del nodo actual
    balance_real = altura_izq - altura_der

    # Obtener los valores que reporta el AVL base
    # para compararlos con los que calculamos manualmente
    altura_avl = avl.getHeightNode(nodo)
    balance_avl = avl.getBalanceFactor(nodo)

    # Verificar si el balance cumple la regla AVL
    error_balance = balance_real not in (-1, 0, 1)

    # Verificar si la altura calculada coincide con la del AVL
    error_altura = altura_avl != altura_real

    # Si hay cualquier inconsistencia, la guardamos en la lista
    if error_balance or error_altura:
        inconsistencias.append({
            "codigo": nodo.getValue(),
            "balance_calculado": balance_real,
            "balance_avl": balance_avl,
            "altura_calculada": altura_real,
            "altura_avl": altura_avl
        })

    # Retornar altura real al padre
    return altura_real


# ------------------------------------------------------------
# 2. Función principal de verificación
# ------------------------------------------------------------
# Esta función es la que debe llamar el sistema o la interfaz.
#
# Flujo:
# 1. Crear lista vacía de inconsistencias
# 2. Auditar desde la raíz del AVL
# 3. Retornar un reporte limpio
#
# Retorna:
# - un diccionario con:
#   * valido: True/False
#   * mensaje: resumen del resultado
#   * inconsistencias: lista de errores encontrados
def verificar_propiedad_avl(avl):
    inconsistencias = []

    # Iniciar auditoría desde la raíz del árbol
    auditar_avl(avl, avl.root, inconsistencias)

    # Si no hay inconsistencias, el árbol cumple la propiedad AVL
    if len(inconsistencias) == 0:
        return {
            "valido": True,
            "mensaje": "El árbol AVL es válido.",
            "inconsistencias": []
        }

    # Si hay inconsistencias, devolver reporte con detalle
    return {
        "valido": False,
        "mensaje": f"El árbol AVL tiene {len(inconsistencias)} inconsistencias.",
        "inconsistencias": inconsistencias
    }
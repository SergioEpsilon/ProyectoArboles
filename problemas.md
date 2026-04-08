# Problemas del Código SkyBalance

## Resumen por Severidad

| Severidad | Cantidad |
|----------|----------|
| Grave    | 2       |
| Mayor    | 6       |
| Mediano  | 5       |
| Menor    | 12      |

**Total**: 25 problemas

---

## GRAVE (Críticos - afectan comportamiento incorrecto)

### 1. parseTreeInput lógica invertida
- **Archivo**: `frontend/js/main.js` línea 30
- **Descripción**: La lógica `return Number.isNaN(asNumber) ? text : asNumber` está invertida. Cuando `asNumber` ES NaN, retorna text (correcto), pero cuando NO es NaN, retorna el número. Pero en realidad el problema es que debería ser `!Number.isNaN(asNumber)` para retornar el número.
- **Solución**: Cambiar a `return !Number.isNaN(asNumber) ? asNumber : text;`

### 2. FlightFactory precioFinal trata 0 como falsy
- **Archivo**: `backend/services/flight_factory.py` líneas 50-51
- **Descripción**: `if not metadata["precioFinal"]` trata 0 como falsy, entonces establecer precioFinal a 0 explícitamente será sobrescrito con precioBase. Esto previene vuelos legítimos de $0.
- **Solución**: Usar `if metadata.get("precioFinal") is None:` en lugar de `if not metadata["precioFinal"]`

---

## MAYOR (Significativos - afectan funcionalidad)

### 3. Altura AVL/BST inconsistencia
- **Archivo**: `backend/models/avl.py` líneas 289-302, `backend/models/bst.py` líneas 278-297
- **Descripción**: `getHeightNode()` retorna 0 para nodos None, mientras `__getHeightNode()` retorna -1. Esta inconsistencia puede causar errores de off-by-one en cálculos de balance.
- **Solución**: Normalizar ambos métodos para retornar -1 para None (altura de hijo hoja) o ambos retornar 0.

### 4. Queue processing rebalance ineficiente
- **Archivo**: `backend/app.py` líneas 559-560
- **Descripción**: `_rebalance()` se llama después de CADA inserción individual durante el procesamiento de queue. Esto es extremadamente ineficiente - debería insertar todos los nodos y rebalancear una sola vez al final.
- **Solución**: Mover `_rebalance()` fuera del ciclo for, llamar una vez después de todas las inserciones.

### 5. Queue processed array memory bloat
- **Archivo**: `backend/app.py` líneas 564-576
- **Descripción**: Cada iteración incluye el estado completo del árbol (`step.arbol`) en el array processed. Para árboles grandes con muchos items, esto crea uso masivo de memoria.
- **Solución**: Incluir solo resumen/snapshot en cada paso, no el árbol completo. Obtener árbol final solo al final.

### 6. Demo tree nunca persiste
- **Archivo**: `frontend/js/main.js` líneas 221-228
- **Descripción**: `loadDemo()` crea una estructura de árbol local pero nunca la envía al backend. El demo se renderiza visualmente pero no tiene estado de backend, causando comportamiento inconsistente.
- **Solución**: O eliminar demo o hacer que llame `apiInsert` para cada valor.

### 7. API endpoint hardcodeado
- **Archivo**: `frontend/js/api.js` línea 4
- **Descripción**: `API_BASE` está hardcodeado a `http://127.0.0.1:5000` sin opción de configuración. Fallará en diferentes puertos, hosts o entornos de producción.
- **Solución**: Hacer API_BASE configurable vía variable window o entorno.

### 8. TreeService detect_key_field retorna None
- **Archivo**: `backend/services/tree_service.py` líneas 78, 198
- **Descripción**: `detect_key_field` puede retornar None, pero línea 198 usa el resultado directamente sin chequeo de null. Cuando key_field es None y el input es valores primitivos puede funcionar, pero para objetos podría fallar.
- **Solución**: Agregar chequeo de null explícito y manejar el caso gracefulmente.

---

## MEDIANO (Moderados - afectan calidad de código)

### 9. _contains_value maneja excepciones silenciosamente
- **Archivo**: `backend/app.py` líneas 91-96
- **Descripción**: Atrapa TODAS las excepciones y retorna False, lo cual puede ocultar errores legítimos (ej. errores de tipo, errores de atributo) y hacer difícil el debugging.
- **Solución**: Atrapar excepciones específicas (TypeError, AttributeError) y registrar las inesperadas.

### 10. Riesgo de stack overflow en recursión
- **Archivo**: `backend/models/avl.py` líneas 52, 70-71
- **Descripción**: `__checkBalance` usa recursión que puede desbordar en árboles extremadamente profundos (miles de nodos). No hay tail-call optimization en Python.
- **Solución**: Convertir a enfoque iterativo usando stack explícito.

### 11. History stack O(n) deletion
- **Archivo**: `backend/services/history_service.py` línea 30
- **Descripción**: `self._stack.pop(0)` es O(n) para Python lists. Con max_size=50 esto es menor, pero el patrón es ineficiente.
- **Solución**: Usar `collections.deque` con maxlen para operaciones O(1).

### 12. Render metrics network spam
- **Archivo**: `frontend/js/render.js` líneas 185-194
- **Descripción**: `loadServerMetrics()` se llama en cada render, causando spam de requests de red. Esto puede ralentizar la UI y crear carga innecesaria al backend.
- **Solución**: Cachear métricas y refrescar solo en mutaciones del árbol o cada X segundos.

### 13. Frontend/Backend balance factor mismatch
- **Archivo**: `frontend/js/render.js` línea 171
- **Descripción**: `bf(root)` se calcula localmente en frontend usando lógica diferente al `getBalanceFactor()` del backend. Los valores pueden diferir, confuse Users.
- **Solución**: Obtener factor de balance del backend en lugar de calcular localmente.

### 14. parseFloat sin chequeo de NaN
- **Archivo**: `frontend/js/main.js` líneas 68-70
- **Descripción**: `parseFloat()` puede retornar NaN para input inválido pero se usa directamente sin validación, potencialmente causando errores de cálculo.
- **Solución**: Agregar validación: `if (Number.isNaN(val)) val = 0;`

---

## MENOR (Code smells y temas de estilo)

### 15. Acceso directo a atributo privado
- **Archivo**: `backend/app.py` línea 63
- **Descripción**: `avl_tree._metrics = metrics_service` accede directamente a atributo privado en lugar de usar un método setter, rompiendo encapsulamiento.
- **Solución**: Agregar método público `set_metrics_service()` en clase AVL.

### 16. hasattr checks innecesarios
- **Archivo**: `backend/app.py` línea 204, `backend/services/tree_serializer.py` líneas 30, 46
- **Descripción**: Usar `hasattr(node, "getMetadata")` cuando la clase Node siempre tiene este método. Coding defensiva innecesaria.
- **Solución**: Remover chequeo hasattr y llamar método directamente.

### 17. hasOwnProperty-like checks innecesarios
- **Archivo**: `frontend/js/render.js` línea 132
- **Descripción**: `(typeof nodeDataMap !== 'undefined')` es innecesario - nodeDataMap siempre está definido en ese scope.
- **Solución**: Remover type checks, usar directamente.

### 18. Duplicate codigo en FlightFactory Merge
- **Archivo**: `backend/services/flight_factory.py` línea 67
- **Descripción**: `codigo` está incluido tanto explícitamente como vía `*FlightFactory.DEFAULTS.keys()`, causando duplicación en iteración.
- **Solución**: Remover `codigo` de la tupla explícita ya que ya está en DEFAULTS.

### 19. BST print_tree dead code
- **Archivo**: `backend/models/bst.py` línea 28
- **Descripción**: Método `print_tree` existe en BST pero probablemente se hereda de BaseTree. Definición redundante.
- **Solución**: Remover el método si la implementación heredada es idéntica.

### 20. Mezcla Español/Inglés en código
- **Archivo**: `backend/models/node.py` líneas 56-62
- **Descripción**: Comentarios dicen "Compatibilidad con implementaciones antiguas" (Español) mientras el resto del codebase usa Inglés. Inconsistente.
- **Solución**: Usar lenguaje consistente en todos los comentarios.

### 21. Métodos de cálculo de balance inconsistentes
- **Archivo**: `backend/app.py` líneas 77-88
- **Descripción**: `_root_balance()` llama métodos diferentes para AVL vs BST (getBalanceFactor vs getHeightNode difference). Comportamiento asimétrico.
- **Solución**: Crear helper `_compute_balance(tree)` consistente.

### 22. Flight modal reset incompleto
- **Archivo**: `frontend/js/main.js` línea 47
- **Descripción**: `resetFlightModal()` no limpia el select de prioridad a su valor por defecto (línea 56 establece a '2' pero podría no coincidir con el default real).
- **Solución**: Asegurar consistencia entre HTML default y JS reset.

### 23. apiModify spread todos los campos de flight
- **Archivo**: `frontend/js/api.js` líneas 22-23
- **Descripción**: Spread todo el objeto `flight` en el request, potencialmente incluyendo campos inesperados.
- **Solución**: Seleccionar explícitamente solo los campos requeridos.

### 24. LocalTree stressMode reference
- **Archivo**: `frontend/js/render.js` líneas 91-94
- **Descripción**: Accede a variable global `stressMode` para indicador de UI. Si la variable no está inicializada, el comportamiento es undefined.
- **Solución**: Agregar default: `const isStress = typeof stressMode !== 'undefined' && stressMode;`

### 25. Tipo inconsistente para valores de nodos
- **Archivo**: `frontend/js/render.js` línea 99
- **Descripción**: `Object.keys(pos)` retorna strings pero los valores del árbol podrían ser números. Inconsistencia de tipo entre backend (Python) y frontend (JS).
- **Solución**: Asegurar conversión string consistente en ambos lados.

---

## Prioridad de Arreglos

### Inmediato (Grave):
1. Fix `parseTreeInput` NaN logic (main.js línea 30)
2. Fix `FlightFactory` precioFinal 0 handling (flight_factory.py líneas 50-51)

### Pronto (Mayor):
3. Fix queue processing rebalance efficiency (app.py líneas 559-560)
4. Fix demo tree persistence (main.js líneas 221-228)
5. Fix API_BASE hardcodeado (api.js línea 4)
6. Fix detect_key_field null handling (tree_service.py líneas 78, 198)

### Después (Mediano):
7. Fix exception handling en _contains_value (app.py líneas 91-96)
8. Convertir __checkBalance a iterativo (avl.py líneas 52, 70-71)
9. Usar collections.deque en history_service (history_service.py línea 30)
10. Cachear loadServerMetrics (render.js líneas 185-194)

### Cuando haya tiempo (Menor):
11. Agregar setter método para _metrics
12. Remover hasattr innecesarios
13. Fix FlightFactory merge duplicación
14. Consistencia de comentarios idioma
15. Fix default values consistency
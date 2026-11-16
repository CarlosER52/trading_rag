# MANUAL OPERATIVO DE DESPLIEGUE Y RESPUESTA A INCIDENTES

## 1. Protocolo de Despliegue de Nuevos Algoritmos en Producción
Todo modelo cuantitativo antes de pasar a cuentas reales debe superar las siguientes fases de validación en entorno de pruebas (Paper Trading):
- **Fase de Backtest OOS (Out-of-Sample):** Mínimo 3 años de datos históricos con comisiones reales simuladas.
- **Fase de Forward Testing:** 30 días naturales de ejecución en tiempo real sin intervención humana, con un desvío máximo del 15% respecto al Sharpe esperado.
- **Validación de Kill-Switch:** Prueba obligatoria de desconexión forzosa ante cortes de latencia superiores a 500ms.

## 2. Procedimiento de Emergencia: Parada Total (Kill-Switch)
Si el sistema de supervisión detecta una anomalía sistémica (desconexión con el broker, latencia excesiva o bucle de órdenes erróneas), se ejecutará el siguiente procedimiento de emergencia:
1. **Desactivación de Celery Beat:** Suspender inmediatamente el despachador de tareas periódicas para evitar nuevas señales de entrada.
2. **Cancelación Masiva de Órdenes Pendientes:** Envío de comando API `CancelAllOpenOrders` a la pasarela del bróker.
3. **Evaluación de Posiciones Abiertas:** Las posiciones con stop-loss activo se mantienen bajo custodia del servidor del bróker; las posiciones desprotegidas se cierran a mercado de forma inmediata.
4. **Notificación de Auditoría:** Registro automático del evento en logs centralizados y alerta crítica al administrador.
# Power BI: un tablero que ayude a tomar decisiones

## La historia en tres preguntas

**1. ¿Dónde está la carga de trabajo y cuánto tarda en atenderse?** → panorama ejecutivo.

**2. ¿En qué agencias, tipos y zonas se concentra el problema?** → diagnóstico operativo.

**3. ¿Qué perfiles encontró K-Means y cómo se usaría el árbol para priorizar?** → minería integrada; no confundir segmentación con causalidad.

## Storyboard recomendado — 3 páginas reales

### Página 1 — Panorama de NYC311

- Encabezado: "NYC311 | Desempeño de solicitudes" y subtítulo que indique **abril–julio 2026** y fecha de corte verificada.
- **Fila de KPIs:** Total de solicitudes; Solicitudes con tiempo observado; % demora alta entre clasificadas; mediana de resolución (horas) y sin tiempo final (separado).
- **Tendencia temporal**: solicitudes por mes/semana, con fecha de creación y eje temporal correcto. No usar promedios sin etiqueta.
- **Gráfico de barras ordenado**: top 8–10 tipos de queja por volumen o demora; opción de conmutador volumen/demora solo si agrega valor y funciona.
- Segmentadores compartidos: fecha, agencia, borough y tipo de queja. Un estado "Restablecer filtros" si puede implementarse de verdad.
- Insight textual específico basado en cifras **reales**; si no está validado, omitirlo.

### Página 2 — Diagnóstico operativo

- Barras horizontales por agencia o tipo; tooltip con **volumen y tasa de demora**, no solo uno.
- Matriz agencia × tipo o borough con formato discreto, con opción de drill-down desde agencia → tipo.
- Mapa **solo si** geocoordenadas confiables y una vista agregada razonable; preferir densidad/conteo, no 1.3M puntos ni exposición de direcciones individuales. Si el mapa no ayuda a decidir, usar otro gráfico.
- Comparación de duración mediana entre agencias: declarar población "con duración observada" y no confundir con cumplimiento de SLA, ya que P75 no es SLA.

### Página 3 — Segmentación y priorización

- Segmentador de **tres clústeres F2**, con opción visible "Sin perfil K-Means" si el nivel lo permite; mostrar **cobertura**.
- Tarjetas por clúster: perfiles, solicitudes cubiertas, mediana de duración, % sin tiempo final, tasa de demora (definición ponderada/no ponderada explícita).
- Comparación de perfiles con **barras** o matriz legible, con volumen para dar contexto. No gráficos 3D.
- Zona "Árbol de decisión": propósito, predictores válidos y sus métricas de **prueba** (Recall 95.15%, F1 78.37%, AUC 0.952) como **contexto histórico**; no ponerlas como KPIs dinámicos dependientes de un slicer de tickets.
- Solo si hay export real de scores: riesgo estimado por ticket y segmentación de alertas, con disclaimer de datos/versión y alcance; no generar alertas inventadas.
- Recomendaciones de negocio específicas: revisar rezagos críticos y volumen en resolución prolongada; mantener revisión humana.

## Reglas visuales anti-slop

- Estilo ejecutivo con **blanco/grises neutros** y **un azul oscuro** primario; acento de alerta restringido a riesgo, no al adorno.
- Máximo 4–5 tarjetas importantes arriba por página; aire entre bloques, márgenes constantes y alineación. Preferir 16:9. Si hay una sola pantalla de exposición, letras deben leerse desde el fondo del aula.
- Fondo limpio, sin gradientes de lujo, iconos gratuitos inconexos, emojis, sombras excesivas o tarjetas por puro relleno.
- Título de cada visual debe decir **qué** mide y **en qué unidades** (p. ej. "Mediana de resolución por agencia · horas").
- Gráficos: barras para categorías; líneas para tiempo; matrices para cruces; mapa para pregunta espacial real. No pastel con 12 categorías, ejes truncados engañosos o 100 colores sin semántica.
- Mostrar `N`, cobertura, período, diferencia de casos sin clasificar. Un filtro oculto por valor 0 que esconde casos no es aceptable.
- Interacciones: al filtrar un clúster las tarjetas y los gráficos correspondientes cambian; los indicadores fijos del experimento F2 **no** simulan interactividad.

## Modelado y medidas DAX — patrones, no copiar sin ajustar

Los siguientes ejemplos **suponen** una tabla importada `Solicitudes` con una fila/ticket, `codigo_solicitud`, `minutos_resolucion` y `demora_alta` con el contrato F2. Codex debe adaptar nombres y validar con datos reales; no son medidas ya ejecutadas.

```dax
Solicitudes = DISTINCTCOUNT(Solicitudes[codigo_solicitud])

Solicitudes con tiempo =
CALCULATE(
    DISTINCTCOUNT(Solicitudes[codigo_solicitud]),
    NOT ISBLANK(Solicitudes[minutos_resolucion])
)

Sin tiempo observado =
CALCULATE(
    DISTINCTCOUNT(Solicitudes[codigo_solicitud]),
    ISBLANK(Solicitudes[minutos_resolucion])
)

Demoras altas =
CALCULATE(
    DISTINCTCOUNT(Solicitudes[codigo_solicitud]),
    Solicitudes[demora_alta] = 1
)

Porcentaje de demora alta =
DIVIDE([Demoras altas], [Solicitudes con tiempo])

Mediana de resolución (horas) =
DIVIDE(MEDIAN(Solicitudes[minutos_resolucion]), 60)
```

**Importante:** DAX anterior supone que `demora_alta` está calculada con el P75/ventana original y que la columna de duración es numérica; no trasladar una columna calculada con un umbral diferente. Evitar agregación por `SUM` de claves o promedios de promedios. Si cambia fecha de creación por fecha de cierre, definir claramente relaciones/medidas para no presentar tendencias confusas.

## Flujo real para construirlo

1. Crear **un primer informe mínimo**: tabla de tickets, total y segmentador; confirmación de que filtra.
2. Extender página 1 → abrir Power BI Desktop → inspeccionar; luego página 2 y página 3.
3. Guardar en **PBIP/PBIR/TMDL** si la versión instalada lo admite; es revisable en Git. Si no, `.pbix` válido con medidas documentadas.
4. Exportar evidencias REALES de las tres páginas con datos; no sustituir por render HTML.
5. Pedir revisión humana sobre 3 preguntas: ¿qué decisión tomaría?, ¿qué cifra respalda esa decisión?, ¿puedo reproducirla con el mismo filtro?

## Contrato de éxito visual

Se presenta una pantalla que **abre**, permite seleccionar agencia/mes/barrio/clúster, cambia al menos dos visuales, conserva integridad de conteos y explica una acción concreta basada en los resultados F2. Eso vale más que 30 gráficas vistosas.

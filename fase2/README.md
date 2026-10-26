# Fase 2 — Minería de datos NYC311

Este repositorio contiene la entrega final de la Fase 2. La raíz se dejó deliberadamente corta: aquí están el informe, la presentación y los notebooks; todo el material de apoyo quedó archivado en `tmp/`.

## Entregables

- `informe_fase2_DMD_NYC311.docx`: informe editable y listo para entregar.
- `informe_fase2_DMD_NYC311.pdf`: versión final del informe.
- `presentacion_fase2_DMD_NYC311.pptx`: presentación editable con notas del expositor.
- `presentacion_fase2_DMD_NYC311.pdf`: copia lista para proyectar o compartir.
- `notebooks/fase2_dmd_nyc311.ipynb`: notebook fuente con explicación pedagógica antes de cada bloque.
- `notebooks/fase2_dmd_nyc311_ejecutado.ipynb`: evidencia de una ejecución completa.

## Qué se analizó

Se trabajó con **1,293,816 solicitudes de NYC311**, registradas entre abril y julio de 2026. El análisis responde dos preguntas:

1. ¿Qué solicitudes tienen mayor probabilidad de terminar con demora alta?
2. ¿Qué perfiles operativos combinan volumen, demora y falta de resolución?

La demora alta se define con el percentil 75 del tiempo observado: **4,329 minutos**, aproximadamente 72 horas. Los 63,079 casos sin tiempo final permanecen sin clasificar para no inventar una duración todavía desconocida.

## Resultados que conviene defender

- Árbol de Decisión optimizado: **Recall 95.15%**, **F1 78.37%** y **ROC-AUC 0.952**.
- El modelo detectó **58,549** demoras reales y dejó **2,982** demoras sin alerta.
- Agencia y tipo de reclamo concentran la mayor importancia predictiva; esto **no demuestra causalidad**.
- K-Means seleccionó **K = 3**, con Silhouette **0.421**, una separación útil pero moderada.
- Los tres perfiles encontrados son: resolución rápida, resolución prolongada y rezago crítico.

La recomendación principal es usar el árbol como filtro de priorización con revisión humana, no como decisión automática. Los grupos de K-Means sirven para orientar dónde investigar y asignar capacidad.

## Cómo ejecutar el notebook

El CSV completo está en `tmp/data/resultados.csv`. El notebook lo detecta automáticamente desde esa ubicación, desde la raíz o desde `/content` en Google Colab.

Para una reproducción local se requiere Python 3.11 o superior y `uv`. Desde la raíz del repositorio ejecuta:

```powershell
.\notebooks\abrir_lab.ps1
```

El lanzador encuentra `tmp/codigo/pyproject.toml`, instala todas las dependencias en `tmp/entorno/notebook` y abre Jupyter Lab desde la raíz. Para comprobar el entorno sin abrir Jupyter:

```powershell
.\notebooks\abrir_lab.ps1 -Verificar
```

El resultado correcto comienza con `ENTORNO_OK`. El comando manual equivalente es:

```powershell
$env:UV_PROJECT_ENVIRONMENT = "$PWD\tmp\entorno\notebook"
uv run --project tmp/codigo jupyter lab
```

No uses únicamente `uv run --with jupyter jupyter lab`: `--with jupyter` agrega Jupyter, pero fuera del proyecto no instala por sí solo pandas, seaborn, scikit-learn y las demás librerías del análisis.

En Google Colab basta con subir el notebook y `resultados.csv`, y luego ejecutar todas las celdas. La variable `RUN_GRID_SEARCH` controla el costo del ajuste:

- `True`: ejecuta la búsqueda completa de 18 configuraciones con validación cruzada de 3 particiones.
- `False`: usa los hiperparámetros ya validados para una demostración más rápida.

## Guion breve para la defensa

1. Presente el problema y las dos preguntas de minería.
2. Explique el umbral P75 y por qué los valores sin cierre no se imputaron.
3. Muestre que el ajuste priorizó Recall para reducir falsos negativos.
4. Interprete la matriz de confusión y reconozca el costo de más alertas preventivas.
5. Explique que K=3 fue la mejor separación evaluada, sin exagerar un Silhouette moderado.
6. Cierre con las prioridades operativas y las limitaciones.

La última diapositiva del archivo editable incluye respuestas sugeridas para preguntas probables del jurado.

## Estructura

```text
.
├── README.md
├── informe_fase2_DMD_NYC311.docx
├── informe_fase2_DMD_NYC311.pdf
├── presentacion_fase2_DMD_NYC311.pptx
├── presentacion_fase2_DMD_NYC311.pdf
├── notebooks/
│   ├── fase2_dmd_nyc311.ipynb
│   ├── fase2_dmd_nyc311_ejecutado.ipynb
│   └── abrir_lab.ps1
└── tmp/
    ├── data/          CSV completo
    ├── referencias/   premisa, Fase 1 y borradores anteriores
    ├── codigo/        vista SQL y configuración reproducible
    ├── entorno/       entorno y cachés locales
    └── qa/            renders y pruebas de control de calidad
```

`tmp/` conserva el material auxiliar para que nada se pierda, pero no es necesario recorrerlo para leer o defender la entrega. En Git se versionan solamente el CSV, la vista SQL y la configuración necesaria; entornos, renders y controles locales quedan excluidos. El CSV se almacena mediante Git LFS.

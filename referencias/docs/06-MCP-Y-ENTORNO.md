# MCP, Power BI y entorno de Codex — ruta realista

**Consulta oficial realizada el 25-10-2026**. Los nombres y comandos pueden cambiar: verificar versión y licencia antes de ejecutar. Ninguna instalación queda hecha por descargar este ZIP.

## Recomendación concreta

Para este proyecto, usar **Power BI Desktop en Windows** + **Power BI Authoring MCP local (Microsoft)** + habilidades oficiales **Skills for Fabric** si funcionan con la versión instalada de Codex. El MCP **modela tablas, relaciones, medidas y DAX**; la creación de páginas visuales se apoya en habilidades y CLI de Power BI Report/PBIR o directamente en Desktop. **El MCP de modelado, por sí solo, NO dibuja páginas ni edita automáticamente el layout de visuales.**

**No necesitas otro harness.** Solo este AGENTS.md, dos skills locales, el MCP y un plan pequeño. Evita instalar simultáneamente dos MCP que hacen lo mismo.

## Herramientas por necesidad

| Necesidad | Herramienta recomendada | Condición |
|---|---|---|
| Leer F1/F2 y código | repos hermanos / GitHub | No clonar dentro de `dmd-fase-3` |
| Consultar DWH | SQL Server Management Studio / `sqlcmd` o Python `pyodbc` | conexión de solo lectura preferentemente |
| Inspeccionar/editar modelo semántico, DAX | **Power BI Authoring MCP local** | Power BI Desktop abierto, permisos y servidor funcionando |
| Crear páginas, slicers y tema PBIR | **Power BI Report skill/CLI (Microsoft)** o Desktop | compatibilidad de instalación; confirmar report renderizado |
| Fuente editable versionable | Power BI Project `.pbip` (PBIR + TMDL) | abrir/guardar en Power BI Desktop; validar esquema |
| Memoria / presentación | DOCX/PPTX local + export PDF | revisión visual humana |

## Ruta A: Codex con MCP de Power BI local

Microsoft publica el paquete `@microsoft/powerbi-modeling-mcp`. En el entorno **que hospeda Codex y puede hablar con Power BI Desktop**, y teniendo Node.js/npm disponibles, registrar en Codex CLI:

```powershell
codex mcp add powerbi-authoring-local -- npx -y @microsoft/powerbi-modeling-mcp@latest --start
codex mcp list
```

Este comando es **un ejemplo de registro**; comprobar en `codex mcp add --help` si tu versión usa esa sintaxis. Alternativamente, configurar `~/.codex/config.toml` (Windows: el `config.toml` del usuario real de Codex) con:

```toml
[mcp_servers.powerbi-authoring-local]
command = "npx"
args = ["-y", "@microsoft/powerbi-modeling-mcp@latest", "--start"]
```

**El proceso ejecutado es el único que puede usar las herramientas;** si registra el MCP en Codex para Linux/WSL, no asuma que automáticamente detectará el Power BI Desktop de Windows. Probar conexión **real**. Prioriza Codex nativo de Windows o puente local comprobado. Si trabajas en WSL Debian, no intentes reparar a ciegas rutas Linux/Windows con symlinks infinitos: construye la parte SQL/Python/PBIR ahí, y valida Power BI en Windows.

**Antes de editar:** respalda proyecto; abre el modelo, confirma nombre y la lista de tablas; prueba **una lectura** y **una medida de bajo riesgo**. No lanzar cambios masivos sin guardar copia y revisar el objetivo. No registrar hosts no confiables ni secretos en Git.

## Ruta B: Skills de Microsoft para crear el reporte, no solo el modelo

Microsoft documenta **`microsoft/skills-for-fabric` / plugin `powerbi-authoring`** que agrupa habilidades de modelado y reporte (`powerbi-report-cli`, descripción actual) con herramientas MCP y puente hacia Power BI Desktop. Está optimizado para GitHub Copilot CLI y anuncia compatibilidad para Codex mediante shims. **No confundir esa compatibilidad declarada con una instalación ya verificada de tu Codex.**

- Página oficial: https://learn.microsoft.com/en-us/power-bi/developer/agentic/power-bi-agentic-overview
- Repositorio: https://github.com/microsoft/skills-for-fabric
- Guía reportes PBIR: https://learn.microsoft.com/en-us/power-bi/developer/agentic/power-bi-report-skill-overview
- Servidor MCP: https://learn.microsoft.com/en-us/power-bi/developer/mcp/power-bi-authoring-mcp

Si puedes instalar directamente habilidades de Microsoft para Codex y detectar el CLI/bridge, **úsalas**; de lo contrario crear el proyecto en Desktop y editar fuente PBIR/TMDL solo sobre un proyecto abierto y reconocido. No inventar JSON de visuales complejos desde cero sin verificar schema/preview.

## Ruta C: si solo hay texto/código y no acceso a Power BI

Codex puede dejar **SQL de vistas, proceso de perfiles, medidas DAX, especificación de páginas, tema de colores y guion exacto de construcción**. Eso es un avance real, pero NO etiquetarlo como Power BI terminado. El integrante con Windows/Power BI debe abrirlo, crear/ajustar visuales, validar interactuación y guardar el `.pbip`/`.pbix` verdadero.

## Sobre PBIP, PBIR y TMDL

- **PBIP** es el proyecto de Power BI Desktop; **PBIR** el reporte visual editable por archivos (JSON estructurado); **TMDL** el modelo semántico. Crear un esqueleto de archivos sin Desktop no prueba que abra.
- Power BI Desktop valida archivos PBIR al abrir; trabajar en copia y revisar antes de entregar. Fuente oficial: https://learn.microsoft.com/en-us/power-bi/developer/embedded/projects-enhanced-report-format
- **Import** es perfectamente válido para la rúbrica: copia datos del DW y requiere actualización. **DirectQuery** consulta al servidor en cada interacción, pero depende del rendimiento y conexión. Fuente: https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-use-directquery
- La conexión SQL Server Desktop ofrece ambos modos: https://learn.microsoft.com/en-us/power-query/connectors/sql-server
- Si publicas un DirectQuery contra SQL Server local hacia el servicio, puede requerir gateway; no volver obligatoria la publicación cloud si el docente acepta Desktop.

## Seguridad y enfoque

No guardar usuarios ni contraseñas en Markdown, TOML, SQL, PBIP o capturas. No instalar MCPs no oficiales aleatorios ni darles acceso amplio a bases con escritura. **No dedicar días a configurar herramientas:** si el MCP no funciona, pasar al camino manual práctico y mantener el objetivo final.

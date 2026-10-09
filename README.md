# Cubanos en Nicaragua · APBN / LBPN

Repositorio independiente para Pelota Cubana Estadísticas. No lee ni modifica Serie Nacional, efemérides ni sus repositorios, credenciales o horarios.

Fuente: https://www.laprofesionalapbn.com.ni/es

- Archivo oficial recuperado desde 2020–2021 hasta 2025–2026; 2026–2027 empieza el 27 de noviembre de 2026.
- `data.json` es el feed público; el sitio lo consulta sin necesidad de republicarse.
- Consulta cada seis horas (01:17, 07:17, 13:17 y 19:17 UTC), además de ejecución manual en Actions. GitHub puede retrasar tareas programadas.
- `registry.json` conserva identidades y alias revisados. Nuevos cubanos se añaden aquí con evidencia; no se asigna nacionalidad por parecido de apellidos.
- Se consultan completas las tablas de bateo, pitcheo y defensa de las dos últimas ediciones configuradas. Una temporada no se reemplaza si falla una tabla, el recuento o la validación. No se suman dos veces acumulados.
- `source.json` conserva los valores publicados; `data.json` recalcula los promedios con sus denominadores y outs, y registra discrepancias en `ratioReviews`.
- 2020–2021: reportes por equipo hasta el 8 de enero (incluyen las rondas previas a la final) y Serie Final, separados. 2021–2026: opción oficial All Rounds. No confundir estos totales con premios de la ronda clasificatoria.
- Se incluyen participaciones documentadas, no contrataciones sin actuaciones. El índice oficial no ofrece ediciones anteriores a 2020–2021; el alcance no equivale a toda la historia del béisbol profesional nicaragüense.

La primera importación fue revisada el 9 de octubre de 2026. `status.json` identifica la última consulta y los fallos; una consulta fallida conserva los datos anteriores y no se presenta como actualización completa.

Estado de puesta en marcha: las dos primeras pruebas en GitHub recibieron HTTP 403 de CloudFront en la fuente oficial. El horario está guardado, pero la actualización automática no está comprobada operativa. Se conserva la importación revisada y el estado de error.

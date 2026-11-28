## Comandos MCP y Perfiles en Hermes Agent

| Comando | Descripción |
| :--- | :--- |
| `hermes mcp` | Abre el selector interactivo en terminal para gestionar o instalar servidores del catálogo. |
| `hermes mcp catalog` | Lista los servidores MCP preconfigurados disponibles en el catálogo oficial. |
| `hermes mcp install <nombre>` | Instala directamente un servidor desde el catálogo integrado. |
| `hermes mcp add <nombre> --command <cmd> --args <args...>` | Añade un servidor MCP local (por `stdio`). |
| `hermes mcp add <nombre> --url <endpoint>` | Añade un servidor MCP remoto (por `HTTP`). Admite `--auth oauth` si requiere OAuth. |
| `hermes mcp login <nombre>` | Completa el flujo de autenticación OAuth en el navegador para un servidor remoto. |
| `hermes mcp list` | Muestra los servidores MCP configurados y su estado. |
| `hermes mcp test <nombre>` | Prueba la conexión con el servidor y lista las herramientas (`tools`) que expone. |
| `hermes --profile <perfil> mcp list` | Muestra los servidores MCP configurados en un perfil específico. |
| `hermes --profile <perfil> mcp add <nombre> --url <endpoint>` | Añade un servidor MCP remoto directamente a un perfil específico. |
| `hermes --profile <perfil> mcp test <nombre>` | Prueba la conexión de un servidor MCP desde un perfil específico. |
| `/reload-mcp` *(en el chat)* | Recarga la configuración de los servidores MCP en una sesión activa sin reiniciarla. |

> **Nota sobre perfiles:** Cualquier subcomando de `hermes mcp` (como `install`, `login` o `add --command`) admite `--profile <perfil>` justo después de `hermes` para aplicarlo sobre ese perfil en lugar de `default`.
`).

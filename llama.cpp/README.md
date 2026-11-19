# llama.cpp - Docker Setup

Este proyecto utiliza Docker para facilitar la ejecución de llama.cpp. Sigue las instrucciones a continuación para comenzar y gestionar el servicio.

## Requisitos
- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/)

## Comenzando
1. Clona este repositorio:
   ```bash
git clone https://github.com/tu-usuario/llama.cpp.git
```
2. Asegúrate de tener un archivo `docker-compose.yml` en la raíz del proyecto. Si no existe, créalo con la siguiente configuración:

```yaml
version: '3'
services:
  llama:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./data:/data
    environment:
      - MODEL_PATH=/data/model.bin
```

## Uso
### Iniciar el servicio
```bash
docker compose up -d
```
- El parámetro `-d` ejecuta el contenedor en segundo plano.
- El servicio estará disponible en http://localhost:8080.

### Detener el servicio
```bash
docker compose down
```
- Esto elimina los contenedores, redes y volúmenes asociados.

## Consejos útiles
1. **Logs en tiempo real**:
   ```bash
docker compose logs -f
```
   Muestra los registros del contenedor en tiempo real.

2. **Variables de entorno**:
   - `MODEL_PATH`: Ruta al modelo dentro del contenedor.
   - `MAX_CONTEXT_SIZE`: Tamaño máximo de contexto para el modelo.

3. **Persistencia de datos**:
   Usa volúmenes para mantener datos como modelos y configuraciones:
   ```yaml
   volumes:
     - ./data:/data
   ```

4. **Reconstruir la imagen**:
   Si modificas el código o el Dockerfile, reconstruye la imagen:
   ```bash
docker compose build
```

5. **Puertos personalizados**:
   Cambia el puerto en `docker-compose.yml` si necesitas usar otro (ej: `8000:8080`).

## Solución de problemas
- **Error de conexión**: Asegúrate de que el puerto esté expuesto correctamente en `docker-compose.yml`.
- **Modelo no encontrado**: Verifica que `MODEL_PATH` apunte a la ruta correcta dentro del contenedor.
- **Espacio en disco insuficiente**: Usa `docker system prune` para limpiar imágenes no utilizadas.
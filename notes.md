# APACHE AIRFLOW CONFIGURACIÓN

En este documento, vamos a agregar las diferentes especificaciones que consitutyen el fichero `docker-compose.yaml`.

## Variables de entorno (enviroment):

- `AIRFLOW__CORE__EXECUTOR: CeleryExecutor`
    - Define el tipo de ejecutor que Airflow utilizará. `CeleryExecutor` permite la ejecución distribuida de tareas.
- `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow`
    - La cadena de conexión a la base de datos que Airflow utilizará para almacenar metadatos.
- `AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow`
    - La URL de la base de datos donde Celery almacenará los resultados de las tareas.
- `AIRFLOW__CELERY__BROKER_URL: redis://:@redis:6379/0`
    - La URL del broker que Celery utilizará para enviar y recibir mensajes.
- `AIRFLOW__CORE__FERNET_KEY: ''`
    - La clave Fernet utilizada para encriptar datos sensibles en la base de datos.
- `AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'`
    - Indica si los DAGs deben estar pausados al ser creados.
- `AIRFLOW__CORE__LOAD_EXAMPLES: 'true'`
    - Indica si se deben cargar los DAGs de ejemplo proporcionados por Airflow.
- `AIRFLOW__API__AUTH_BACKENDS: 'airflow.api.auth.backend.basic_auth,airflow.api.auth.backend.session'`
    - Define los métodos de autenticación que se utilizarán para acceder a la API de Airflow.


> *Celery* es una biblioteca de Python que actua como cliente de gestor de colas. Utiliza un broker de mensajes (como **RabbitMQ o Redis**)

## Volumenes (volumes)
Vienen a ser las carpetas donde se va a almacenar la información. Estas carpetas van a estar sincronizadas entre los contenedores que creemos y la máquina donde se alojen dichos contenedores.

- `${AIRFLOW_PROJ_DIR:-.}/dags:/opt/airflow/dags`
    - Carpeta donde se almacenan los DAGs (Directed Acyclic Graphs) de Airflow.
- `${AIRFLOW_PROJ_DIR:-.}/logs:/opt/airflow/logs`
    - Carpeta donde se almacenan los logs generados por Airflow.
- `${AIRFLOW_PROJ_DIR:-.}/config:/opt/airflow/config`
    - Carpeta donde se almacenan los archivos de configuración de Airflow.
- `${AIRFLOW_PROJ_DIR:-.}/plugins:/opt/airflow/plugins`
    - Carpeta donde se almacenan los plugins personalizados de Airflow.

## Servicios (Services):
Vienen a ser todos los servicios necesarios por **Apache-Airflow** para que funcione.

- **Postgres.**: Base de datos.
- **Redis.**: Broker
- **Airflow-webserver.**
- **Airflow-scheduler.**
- **Airflow-worker.**
- **Airflow-init**: Servicio encargado de lanzar la instancia airflow.
- **Flower**.


## Lanzar contenedor


```
docker compose up
```

Una vez termine de lanzarse el contenedor para acceder a la página principal de **Apache Airflow** lo hacemos a la URL [http://localhost:8080](http://localhost:8080) y introducimos las creedenciales.

* USUARIO: airflow
* CONTRASEÑA: airflow

Ya estaríamos dentro de la página.
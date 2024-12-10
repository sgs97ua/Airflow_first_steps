# APACHE AIRFLOW CONFIGURACIÓN

## Configuración  Airflow docker
### Prerequisitos


```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.3/docker-compose.yaml'

```

Crear los directorios donde se montarán los volúmenes y el fichero de variables de entorno.

```bash
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env
```


En este documento, vamos a agregar las diferentes especificaciones que consitutyen el fichero `docker-compose.yaml`.

### Variables de entorno (enviroment):

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

### Volumenes (volumes)
Vienen a ser las carpetas donde se va a almacenar la información. Estas carpetas van a estar sincronizadas entre los contenedores que creemos y la máquina donde se alojen dichos contenedores.

- `${AIRFLOW_PROJ_DIR:-.}/dags:/opt/airflow/dags`
    - Carpeta donde se almacenan los DAGs (Directed Acyclic Graphs) de Airflow.
- `${AIRFLOW_PROJ_DIR:-.}/logs:/opt/airflow/logs`
    - Carpeta donde se almacenan los logs generados por Airflow.
- `${AIRFLOW_PROJ_DIR:-.}/config:/opt/airflow/config`
    - Carpeta donde se almacenan los archivos de configuración de Airflow.
- `${AIRFLOW_PROJ_DIR:-.}/plugins:/opt/airflow/plugins`
    - Carpeta donde se almacenan los plugins personalizados de Airflow.

### Servicios (Services):
Vienen a ser todos los servicios necesarios por **Apache-Airflow** para que funcione.

- **Postgres.**: Base de datos.
- **Redis.**: Broker
- **Airflow-webserver.**
- **Airflow-scheduler.**
- **Airflow-worker.**
- **Airflow-init**: Servicio encargado de lanzar la instancia airflow.
- **Flower**.


### Lanzar contenedor

En primer lugar hay que inicializar la base de datos para que funcione.

```
docker compose up airflow-init
```
Una vez configurada la base de datos ya podemos utilizarlo.
```
docker compose up
```

Una vez termine de lanzarse el contenedor para acceder a la página principal de **Apache Airflow** lo hacemos a la URL [http://localhost:8080](http://localhost:8080) y introducimos las creedenciales.

* USUARIO: airflow
* CONTRASEÑA: airflow

Ya estaríamos dentro de la página.

## Creación primer DAG.

**DAG** o también conocido como *gráfo acíclo dirigido* es la estructura de datos utilizada por Apache Airflow para definir la lógica de nuestros flujos de trabajo de manera visual y programada.

Para crear un **DAG** tenemos que crear un **fichero .py** en la la carpeta [./dags](./dags).
En nuestro caso vamos a crear el fichero `MI_PRIMER_DAG.py`.

Dependencias de Python:
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
```

- datetime: Para trabajar con fechas.
- airflow: Importamos la estructura DAG y operadores *Empty*(para tareas dummy) y *Python* (para ejecutar código en python)

A continuación, definimos una serie de *variables* para configurar nuestro *Operator*.

```py
TAGS  = ["PythonDataFlow"]
DAG_ID = "MI_PRIMER_DAG"
DAG_DESCRIPTION = "Mi primer DAG en Airflow"
DAG_SCHEDULE = "0 9 * * *"
default_args = {
    "start_date":datetime(2024,12,10),
}
retries = 4
retry_delay = timedelta(minutes=5)
```

- **TAGS**: para agrupar el DAG por etiquetas y facilitar a la hora de filtrar.
- **DAG_ID**: el nombre con el que aparecerá en el entorno.
- **DAG_DESCRIPTION**: descripción del dag.
- **DAG_SCHEDULE**: Intervalo de tiempo que se establece mediante chrone y que hace que se ejecute todos los días a las 9 de la mañana.
- **default_args**: vienen a ser parámetros adicionales, en este caso en concreto nosotros especificamos que su primera ejecución sea el 10 de diciembre.
- **retries**: variable de reintentos para especificar cuantas veces tiene que lanzar el operador si falla.


Una vez definida variables que van a ser utilizadas para constituir nuestro DAG, lo que hacemos es construir el objeto DAG y la tarea que va ajecutar.

```py
def execute_tasks():
    print("Hala Madrid")
```

Definimos el objeto DAG:
```py
dag = DAG(
    DAG_ID,
    default_args=default_args,
    description=DAG_DESCRIPTION,
    catchup=False,# Esto hace que el dag se ponga al día con todas las ejecuciones pendientes
    schedule_interval=DAG_SCHEDULE,
    max_active_runs=1,# Máxima número de ejecuciones que puede tener el dag
    dagrun_timeout=timedelta(minutes=60),
    tags=TAGS,
    retries=retries,
    retry_delay=retry_delay,
)
```

Donde cabe añadir a la descripción los parámetros:
- **catchup**: En el que se especifica si queremos que el dag se ponga al día con todas aquellas ejecuciones pendientes.

- **max_active_runs**: Máximo número de ejeciciones que puede tener el dag.


Una vez configurado el DAG, vamos a definir las tareas que se van a ejecutar en el DAG.

``` py
with dag as dag:
    start_task = EmptyOperator(task_id="inicia_proceso")
    
    end_task = EmptyOperator(task_id="finaliza_proceso")

    first_task = PythonOperator(task_id="primer_proceso", 
                                python_callable=execute_tasks,
                                retries=retries,
                                retry_delay=retry_delay)
```

Finalmente, se establece la dependencia entre cada una de las tareas:

```py

start_task >> first_task >> end_task

```

Siendo el flujo:
1. start_task.
2. first_task.
3. end_task.

Para poder visualizar este flujo lo podemos observar o bien esperando 5 minutos para que aparezca este nuevo flujo o bien ejecutar `docker compose restart`.
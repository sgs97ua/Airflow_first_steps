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


### Configuración de dependencias entre tareas

A la hora de establecer las dependencias existentes entre tareas, se puede especificar de dos maneras diferentes.

- Especificando dos ramas en el que intervengan dos tareas totalmente diferentes. En el código inferiro la *end_task* depende de que haya finalizado la tarea *first_task* y *second_task* en paralelo.
```py
start_task >> first_task >> end_task
start_task >> second_task >> end_task
```

![Ejemplo de flow](./images/example(1).png)

- Especificando mediante una lista aquellas tareas que se tienen que ejecutar en paralelo
```py
start_task >> [first_task,second_task] >> end_task
```


Ejemplo de definición de un flujo en el que tenga diferentes actividades en paralelos.
``` python
    start_task >> [first_task,second_task] >> third_task
    third_task >> [fourth_task,fifth_task] >> end_task
```

![Ejemplo flujo multiparalelo](./images/example(2).png)

### Configuracion de variables de entorno

Para ello tenemos que clickar en el menú `Admin > Variables`. Podemos crear las variables siguiendo una estructura **Key-Value**.

Para acceder desde el DAG a las variables de entorno definidas, tenemos que importar la clase **Variables** del paquete **airflow.models**.
``` python
from airflow.models import Variables
```
Una vez importado el modulo necesario, para acceder a las variables de entorno definidas, se accede de la misma manera que se accede a un diccionario de Python.
``` python
ENV = Variables.get("env")
ID = Variables.get("id")
```


### Ejecucion de Dataflow con parámetros.

A la hora de especificar parámetros en el DataFlow, utilizamos el parámetro del constructor del objeto **DAG** denominado `params`.

```python
dag = DAG(
    DAG_ID,
    default_args=default_args,
    description=DAG_DESCRIPTION,
    catchup=False,
    schedule_interval=DAG_SCHEDULE,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=60),
    tags=TAGS,
    params={'Manual':True}
)
```

Establecer el parámetro `Manual:True` hace que al ejecutar de forma manual el DAG en la aplicación, se nos dirija a una página en la que podemos modificar los parámetros de ejecución, también se puede asignar un DAG_ID específico, pudiendo cambiar la fecha lógica de la ejecución.

![Página de configuración de parámetros](images/configuracion_parametros_dag.png)

Para añadir más parámetros, se añaden nuevos pares *clave-valor* en el constructor del DAG en el parámetro **params**. En el ejemplo, se ha añadido un parámetro fecha en el que se incluye la fecha de hoy.

``` python
dag = DAG(
    DAG_ID,
    default_args=default_args,
    description=DAG_DESCRIPTION,
    catchup=False,
    schedule_interval=DAG_SCHEDULE,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=60),
    tags=TAGS,
    params={'Manual':True,'Fecha':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
)

```

Al ejecutar el DAG con estos parámetros, observamos que nos devuleve los valores de los parámetros que hemos configurado en el apartado *Run Config*.

![Parámetros devuletos tras la ejecución](images/param_result_ejecucion.png)


> **BUENA PRÁCTICA**: No definir directamente los parámetros dentro del constructor del DAG, mejor definir un diccionario fuera y pasasrselo como parámetro.


### Usando Contexto de las Tareas en Airflow

El contexto es la información y variables que son pasadas a las tareas durante la ejecución de un DAG. Generalmente el contexto inlcuye información como fecha de ejecución, identificador de la tarea, estado de la tarea, etc.

El contexto es muy importante ya que permite acceder a la información de manera relevante y dinámica, lo que facilita la personalización y control de ejecución de cada tarea.


Para acceder al contexto en un **PythonOperator** se establece en primer lugar el parámetro `provide_context=True`.

```
first_task = PythonOperator(task_id="primer_proceso",               
                            python_callable=execute_tasks,
                            retries=retries,
                            retry_delay=retry_delay,
                            provide_context=True)
```

Posteriormente en el **python_callable** se agrega el parámetro `**kwargs`.
Este parámetro, es un diccionario con gran cantidad de información. Para ver el funcionamiento utilizamos el siguiente código.

```py
def execute_tasks(**kwargs):
    params = kwargs.get('params',{})
    manual = params.get('Manual',False)

    if manual:
        kwargs['ti'].xcom_push(key='Color', value='Amarillo')
    else:
        kwargs['ti'].xcom_push(key='Color', value='Azul')
```

1. Se obtienen los parámetros.
2. Se obtiene el parámetro `Manual`.
3. En función del valor `Manual` se añade a los parámetros de la instancia de la tarea que se esta ejecutando un valor diferente de *Color*. Esto se hace accediendo a `kwargs['ti']` y invocando el método `xcom_push`


En caso de que se quiera acceder al contexto en el siguiente operador, tendremos que acceder de nuevo a `kwargs['ti']` e invocar el método `xcom_pull(key='<KEY>', task_ids='<ID TAREA>')` para obtener el valor.

```

def context_task(**kwargs):
    ti = kwargs['ti']
    color = ti.xcom_pull(key='Color', task_ids='primer_proceso')
    print(f"El color es: {color}")

```


### Variables importantes del contexto.

* `ds`: Fecha de inicio de la ejecución de la tarea. Pero en formato con separación. Ejemplo: *2024-04-29*
* `ds_nodash`: Igual que `ds` pero sin separadores en la fecha. Ejemplo: *20240429*
* `next_execution_date`: Fecha de la próxima ejecución automática. En formato *DateTime*
* `prev_execution_date`: Fecha de la ejecución anterior. En formato *DateTime*.
* `prev_execution_date_success`: Fecha de la anterior ejecución automática exitosa.
* `tomorrow_ds`: Día después de la ejecución de la tarea.
* `yesterday_ds`: Un día antes de la ejecución de la tarea.


#### Operadores sin funcionalidad de provided context
Existen operadores que no reciben la funcionalidad de provided context, pero si reciben parámetros, podemos hacer uso de estos parámetros especificandolo de esta manera `op_kawrgs={'ds':'{{ds}}'}`, de esta manera se accede de forma más rápida a los valores del contexto.

Ejemplo:
``` python
    def execute_tasks(**kwargs):
    params = kwargs.get('params',{})
    manual = params.get('Manual',False)

    if manual:
        kwargs['ti'].xcom_push(key='Color', value='Amarillo')
    else:
        kwargs['ti'].xcom_push(key='Color', value='Azul')



    second_task = PythonOperator(task_id="segundo_proceso",
                                  python_callable=context_task,
                                  retries=retries,
                                  retry_delay=retry_delay,
                                  op_kwargs={'ds':'{{ds}}',
                                            'color':'{{ti.xcom_pull(task_ids="primer_proceso", key="Color")}}'}) 
    
```

Definimos en el parámetro `op_kwargs`, a que clave del diccionario de argumentos debe acceder. En este caso se accede a la variable de fecha de inicio de la tarea `ds` y a la variable de la tarea del primer proceso con clave Color mediante el método `xcom_pull`. 


### Control de excepciones

Algunas de las excepciones más utilizadas son:

- **AirFlowSkipException**: Utilizada para omitir tareas.
- **AirFlowException**: Excepción que permite controlar cuando una tarea falla.
- **AirFlowTaskTimeout**: Excepción que permite controlar cuando excede el tiempo de espera.


``` python
from airflow.eceptions import AirflowSkipException, AirflowException, AirflowTaskTimeout 
```

Ejemplo de lanzar una excepción de omisión de una parte del código.

```python
def execute_tasks(**kwargs):
    params = kwargs.get('params',{})
    manual = params.get('Manual',False)

    if manual:
        raise AirflowSkipException("Se supende la tarea porque quiero")

```

Al ejecutar la tarea observamos que la tarea ha sido omitida.

![Airflow Skip Exception](images/AirflowSkipException.png)


Ejemplo de lanzar una excepción error de una parte del código.

```python
def execute_tasks(**kwargs):
    params = kwargs.get('params',{})
    manual = params.get('Manual',False)

    if manual:
        raise AirflowException("Error al ejecutar la tarea")

```


Ejemplo de lanzar una TimeOutException.

```python
def execute_tasks(**kwargs):
    params = kwargs.get('params',{})
    manual = params.get('Manual',False)

    if manual:
        timeout = 10
        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                raise AirflowTaskTimeout("La tarea ha excedido el tiempo de espera especificado")
            time.sleep(1)

```

![Airflow TimeOut Exception](images/TimeOutException.png)


### Trigger Rules

Las trigger rules vienen a ser las condiciones necesarias para que una tarea pueda ejecutarse dentro de un flujo de trabajo. Estas condiciones estan basadas en el estado de las tareas anteriores (upstream) en el flujo.

En primer lugar, tenemos que importar el paquete TriggerRule.
``` python
from airflow.utils.trigger_rule import TriggerRule
```

Existen diferentes tipos de *TriggerRules*:
- `ALL_SUCCESS`: Todas las tareas previas tienen que haber sido ejecutadas con éxito para que se actualice la información.

- `ONE_SUCCESS`: La tarea se ejecuta si al menos una de las tareas anteriores ha tenido éxito.

- `ALL_FAILED`: La tarea se ejecuta si al menos una de las tareas anteriores ha fallado.

- `ONE_FAILED`: La tarea se ejecuta si al menos una de las tareas ha fallado.

- `ALL_DONE`: La tarea se ejecuta cuando todas las tareas anteriores han terminado, sin importar que hayan tenido éxito o hallan fallado.

- `NONE_FAILED`: La tarea se ejecuta si ninunga de las tareas anteriiores ha fallado.

- `ALWAYS`: La tarea se ejecuta sin importar el estado de las tareas anteriores.

En el caso de que configuremos un DAG de la siguiente manera.

``` python
    start_task = EmptyOperator(task_id="inicia_proceso")
    
    end_task = EmptyOperator(task_id="finaliza_proceso",
                             trigger_rule=TriggerRule.ALL_SUCCESS,)

    first_task = PythonOperator(task_id="primer_proceso", 
                                python_callable=execute_tasks,
                                retries=retries,
                                retry_delay=retry_delay,
                                provide_context=True)
    
    second_task = PythonOperator(task_id="segundo_proceso",
                                  python_callable=second_tasks,
                                  provide_context=True)

    
    
    start_task >> [first_task,second_task] >> end_task
```

Estamos estableciendo que la tarea `end_task`se ejecute únicamente si las tareas `first_task,second_task` que son las tareas anteriores han sido ejecutadas de forma exitosa.

Al ejecutar el DAG obtenedremos **upstream_failed**.


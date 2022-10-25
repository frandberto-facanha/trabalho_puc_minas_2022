"""
### Extracao metricas CPU - Prometheus Estaleiro
"""
# [START tutorial]
# [START import_module]
from datetime import datetime, timezone, timedelta
import requests
import pendulum
from airflow.operators.bash import BashOperator

# The DAG object; we'll need this to instantiate a DAG
from airflow.decorators import dag, task

# Operators; we need this to operate!
from airflow.operators.python import PythonOperator

# [END import_module]

# [START instantiate_dag]
@dag(
    # [START default_args]
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={'retries': 2},
    schedule_interval='*/15 * * * *',
    start_date=pendulum.datetime(2022, 5, 26, tz="America/Fortaleza"),
    catchup=False,
    tags=['cpu','memory', 'estaleiro'],
)
def prometheus_estaleiro_metrics_extraction():
    """
    ### Extraction of CPU and Memory Metrics from Estaleiro/Prometheus service
    This is a simple ETL data pipeline to extract Prometheus metrics from API-Rest at each 15 minutes  
    """
    def extract_system_name(namespace):
        environment = namespace.split('-')[-1]
        system = namespace.split(f'-{environment}')[0]
        return system

    def get_datetime_now():
        timezone_offset = -3.0  # Brasil/Fortaleza
        tzinfo = timezone(timedelta(hours=timezone_offset))
        return datetime.now(tzinfo)

    # [START check_healthy]
    @task()
    def check_healthy():
        url_healthy = 'http://localhost:9090/-/healthy'
        response = requests.get(url_healthy)
        if response.status_code == 200:
           print('Prometheus is healthy')
    # [END check_healthy]

    # [START check_ready]
    @task()
    def check_ready():
        url_ready = 'http://localhost:9090/-/ready'
        response = requests.get(url_ready)
        if response.status_code == 200:
           print('Prometheus is ready')
    # [END check_ready]

    # [START CPU Extraction]
    @task()
    def cpu_extraction():
        # ti = kwargs['ti'] # Sem parâmetros
        # extract_data_string = ti.xcom_pull(task_ids='extract', key='order_data')
        # order_data = json.loads(extract_data_string)

        #url_prometheus_cpu = 'http://localhost:9090/api/v1/query?query=pod_name:container_cpu_usage:sum{}[1m]'
        url_prometheus_cpu = 'http://localhost:9090/api/v1/query'
        # Remove containers: pushgateway, backbox, pgbouncer
        filter_sql = 'sum(rate(container_cpu_usage_seconds_total{container!~"POD|", container!= "blackbox", container!= "pgbouncer", container!= "pushgateway"}[5m])) by (namespace,pod,container)'        
        response = requests.get(url_prometheus_cpu, params={'query': filter_sql})

        if response.status_code == 200:
            json_response = response.json() # This method is convenient when the API returns JSON   
            x = get_datetime_now()
            timestamp = x.strftime("%H%M%S%d%m%Y")
            file = open(f"./dags/data/cpu_{timestamp}.csv", "a")
            print(f'Criado arquivo de resultado cpu_{timestamp}')
            for json in json_response['data']['result']:
                try:
                    container = json['metric']['container']
                    namespace = json['metric']['namespace']
                    system = extract_system_name(namespace)
                    pod_name = json['metric']['pod']
                    cpu = json['value'][1]
                    print(f'Escreveu resultado {pod_name} para saida')
                    file.write(f'{system};{namespace};{container};{pod_name};{cpu}\n')
                except:
                    print(f'Erro ao realizar o parser de {json}')
                    print(f'Lendo proximo registro')
            file.close()            
        else:
            print(f'Erro na obtenção da resposta do Prometheus')         
            file.close()
            exit(1)
        
        # ti.xcom_push('total_order_value', total_value_json_string)

    # [END CPU Extraction]

    # [START Memory Extraction]
    @task()
    def memory_extraction():
        # ti = kwargs['ti'] # Sem parâmetros
        # extract_data_string = ti.xcom_pull(task_ids='extract', key='order_data')
        # order_data = json.loads(extract_data_string)

        #url_prometheus_memory = 'http://localhost:9090/api/v1/query?query=pod_name:container_memory_working_set_bytes:sum'
        url_prometheus_memory = 'http://localhost:9090/api/v1/query'
        filter_sql = 'sum(container_memory_usage_bytes{container!~"POD|", container!="blackbox", container!="pushgateway", container!="pgbouncer"}) by (namespace,pod,container)'
        response2 = requests.get(url_prometheus_memory, params={'query': filter_sql})

        if response2.status_code == 200:
            json_response2 = response2.json() # This method is convenient when the API returns JSON   
            x = get_datetime_now()
            timestamp = x.strftime("%H%M%S%d%m%Y")
            file_mem = open(f"./dags/data/memory_{timestamp}.csv", "a")
            print(f'Criado arquivo de resultado memory_{timestamp}')
            for json2 in json_response2['data']['result']:
                try:
                    pod_name = json2['metric']['pod']
                    namespace = json2['metric']['namespace']
                    system = extract_system_name(namespace)
                    container = json2['metric']['container']
                    memory = json2['value'][1]
                    print(f'Coleta Memoria: pod {pod_name}')
                    file_mem.write(f'{system};{namespace};{container};{pod_name};{memory}\n')
                except:
                    print(f'Erro ao realizar o parser de {json2}')
                    print(f'Lendo proximo registro')
        else:
            print(f'Erro na obtenção da resposta do Prometheus')         
            file_mem.close()
            exit(1)
        file_mem.close()

        # ti.xcom_push('total_order_value', total_value_json_string)

    # [END CPU Extraction]

    # [START Error Extraction]
    @task()
    def error_extraction():
        # ti = kwargs['ti'] # Sem parâmetros
        # extract_data_string = ti.xcom_pull(task_ids='extract', key='order_data')
        # order_data = json.loads(extract_data_string)

        # url_prometheus_error = 'http://localhost:9090/api/v1/query?query=count_over_time(kube_pod_container_status_last_terminated_reason{reason="OOMKilled"}[5m])'
        url_prometheus_error = 'http://localhost:9090/api/v1/query'
        filter_sql = 'sum(kube_pod_container_status_last_terminated_reason{reason="OOMKilled"}) by (container, namespace)'
        response3 = requests.get(url_prometheus_error, params={'query': filter_sql})

        if response3.status_code == 200:
            json_response3 = response3.json() # This method is convenient when the API returns JSON   
            x = get_datetime_now()
            timestamp = x.strftime("%H%M%S%d%m%Y")
            file_error = open(f"./dags/data/error_{timestamp}.csv", "a")
            print(f'Criado arquivo de resultado error_{timestamp}')
            for json3 in json_response3['data']['result']:
                try:
                    container = json3['metric']['container']
                    namespace = json3['metric']['namespace']
                    system = extract_system_name(namespace)
                    qtd = json3['value'][1]
                    print(f'Coleta error {container}')
                    if qtd > 0:
                        file_error.write(f'{system};{namespace};{container};OOMKilled;{qtd}\n')
                except:
                    print(f'Erro ao realizar o parser de {json3}')
                    print(f'Lendo proximo registro')
        else:
            print(f'Erro na obtenção da resposta do Prometheus')         
            file_error.close()
            exit(1)
        file_error.close()

        # ti.xcom_push('total_order_value', total_value_json_string)

    # [END Error Extraction]

    @task()
    def cpu_throttled():
        # ti = kwargs['ti'] # Sem parâmetros
        # extract_data_string = ti.xcom_pull(task_ids='extract', key='order_data')
        # order_data = json.loads(extract_data_string)

        #url_prometheus_cpu = 'http://localhost:9090/api/v1/query?query=pod_name:container_cpu_usage:sum{}[1m]'
        url_prometheus_cpu = 'http://localhost:9090/api/v1/query'
        filter_sql = 'sum(rate(container_cpu_cfs_throttled_seconds_total{container!~"POD|", container!="blackbox", container!="pushgateway", container!="pgbouncer"}[5m])) by (namespace,pod,container)'        
        response = requests.get(url_prometheus_cpu, params={'query': filter_sql})

        if response.status_code == 200:
            json_response = response.json() # This method is convenient when the API returns JSON   
            x = get_datetime_now()
            timestamp = x.strftime("%H%M%S%d%m%Y")
            file = open(f"./dags/data/cpu_throttled_{timestamp}.csv", "a")
            print(f'Criado arquivo de resultado cpu_throttled_{timestamp}')
            for json in json_response['data']['result']:
                try:
                    container = json['metric']['container']
                    namespace = json['metric']['namespace']
                    system = extract_system_name(namespace)
                    pod_name = json['metric']['pod']
                    cpu_throttled = json['value'][1]
                    print(f'Escreveu resultado {pod_name} para saida')
                    if cpu_throttled > 0:
                        file.write(f'{system};{namespace};{container};{pod_name};{cpu_throttled}\n')
                except:
                    print(f'Erro ao realizar o parser de {json}')
                    print(f'Lendo proximo registro')
            file.close()            
        else:
            print(f'Erro na obtenção da resposta do Prometheus')         
            file.close()
            exit(1)
    # [END CPU Overprocessing]

    # Zip o arquivo
    zip_result = BashOperator(
        task_id='zip_result',
        bash_command='gzip /opt/airflow/dags/data/*.csv')

    # [START main_flow]
    check_healthy() >> check_ready() >> [cpu_extraction(), memory_extraction(), error_extraction(), cpu_throttled()] >> zip_result

# [END main_flow]

prometheus_estaleiro_metrics_extraction = prometheus_estaleiro_metrics_extraction()

# [END]
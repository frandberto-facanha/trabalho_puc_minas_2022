# Trabalho de Pós-Graduação para PUC Minas - 2022

## Objetivo
Esse projeto corresponde a predição de flavors configurados para a execução de aplicações que rodam em ambiente Kubernetes num sistema de nuvem privada, que disponibiliza uma infraestrutura de PaaS (Plataform as a Service) para execução das aplicações.

Cada flavor está associado à aplicação (módulo, job ou addon) e quando essa é iniciada tem os parâmetros de request(solicitação) e limite configurados conforme o flavor associado.

## Dataset

Os dados utilizados no projeto foram coletados a partir da api do Prometheus, por meio de uma DAG criado no Airflow especificamente para isso. 

O sistema de nuvem privada tem coletas realizadas a cada minuto pelo Prometheus via a api do Metric Server do Kubernetes. Os dados coletados são armezados na base temporal do Prometheus para posterior consulta ou montagem de dashboards via Grafana.

A DAG criada [extract_prometheus_metrics.py](/script-extracao-airflow/extract_prometheus_metrics.py) utiliza esse ambiente de monitoração existente para nuvem privada para realizar coleta de métricas específicas via Prometheus.

A DAG era executada a cada 15 minutos realizando coletas das métricas: 
- container_cpu_usage_seconds_total
- container_memory_usage_bytes
- kube_pod_container_status_last_terminated_reason
- container_cpu_cfs_throttled_seconds_total

Os dados brutos resultados das coletas resultantes da DAG estão disponíveis da pasta do projeto [dados/coletas](/dados/coletas).

Os dados das 4 métricas estão nas respectivas pastas, em formato CSV compactado:
- [cpu](/dados/coletas/cpu)
- [memoria](/dados/coletas/memoria)
- [error](/dados/coletas/error)
- [throttled](/dados/coletas/throttled)

Esses arquivos num total 384, são a base dos dados processados pelos notebooks do projeto.

Outro arquivo disponível, é o **arquivo consolidado de resultados** já com rótulos aplicados, localizado em [dados/coletas/cpu_memoria_rotulado.csv]{/dados/coletas/cpu_memoria_rotulado.csv}. Esse arquivo de dados é o que foi utilizado no Modelo de Árvore de Decisão para predições.

## Processamento do Dados

## Treinamento


- 


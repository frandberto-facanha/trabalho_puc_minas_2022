# Trabalho de Pós-Graduação para PUC Minas - 2022

## Objetivo
Esse projeto compreende ao trabalho de fim do Curso de Especialização em Inteligência Artificial e Aprendizado de Máquina, como requisito parcial à obtenção do título de Especialista pela Pontifícia Universidade Católica (PUC) de Minas Gerais. 

O projeto tem objetivo de aperfeiçoar a seleção de flavors no Sistema de Nuvem Privada de uma empresa, que fornece um serviço de Plataform as a Service (PaaS), utilizando aprendizado de máquina, mais especificamente, modelo de classificação, a fim de predizer qual a configuração de flavors mais adequada para a execução de uma aplicação.

 Os Flavors são configurações pré-definidas de recursos de CPU e memória associadas a aplicação antes de ser publicada no sistema de Nuvem Privada. Essas configurações são utilizadas pelo Kubernetes para alocar os recursos para execução do pod.


Cada flavor está associado à aplicação (módulo, job ou addon) e quando essa é iniciada pelo Kubernetes, tem os parâmetros de request(solicitação) e limite configurados conforme o flavor associado.

## Dataset

Os dados utilizados no projeto foram coletados a partir da api do Prometheus, por meio de um DAG (Directed Acyclic Graph) criado no Airflow especialmente para isso. 

O sistema de nuvem privada tem coletas realizadas a cada minuto pelo Prometheus, via a api do Metric Server do Kubernetes. Os dados coletados são armazenados na base temporal do Prometheus para posterior consulta ou montagem de dashboards via Grafana.

A DAG criada [extract_prometheus_metrics.py](/script-extracao-airflow/extract_prometheus_metrics.py) utiliza esse ambiente de monitoração existente para nuvem privada para realizar coleta de métricas específicas via Prometheus.

O DAG foi executado a cada 15 minutos realizando coletas das métricas: 
- container_cpu_usage_seconds_total
- container_memory_usage_bytes
- kube_pod_container_status_last_terminated_reason
- container_cpu_cfs_throttled_seconds_total

Os dados brutos resultados das coletas resultantes da DAG estão disponíveis da pasta do projeto [dados/coletas](/dados/coletas) e [dados/coletas_dia_2](/dados/coletas_dia_2). Cada pasta corresponde a uma coleta de 24 horas em dias diferentes.

Os dados das 4 métricas estão nas respectivas pastas, em formato CSV compactado:
- [cpu](/dados/coletas/cpu)
- [memoria](/dados/coletas/memoria)
- [error](/dados/coletas/error)
- [throttled](/dados/coletas/throttled)

De forma similar, as pastas também estão organizadas para as coletas_dia_2.

Cada coleta de 24 horas gera um total 384 arquivos, que compreendem a base dos dados que são processados pelos notebooks do projeto.

Outro arquivo disponível é o **arquivo consolidado de resultados**, já com rótulos aplicados e localizado em [dados/coletas/cpu_memoria_rotulado.csv](/dados/coletas/cpu_memoria_rotulado.csv). Esse arquivo de dados é o que foi utilizado no Modelo de Árvore de Decisão para predições.

## Preparação, Processamento dos Dados

Todas as tarefas de preparação processamentos dos dados foram implementadas por Jupyter notebooks publicados no projeto [notebooks](/notebooks).

São eles:
- [01-pre_processar_arquivos](/notebooks/01-pre_processar_arquivos.ipynb): implementa o pré-processamento inicial gerando arquivos temporários que adicionam novos campos de tempo (hora e minuto) e campo hash (campo de identicação da aplicação/contêiner. Os arquivos pré-processados são armazenados na pasta **processados** de cada métrica. Por exemplo, para CPU os arquivos gerados ficam em **/dados/coletas/cpu/processados**.
- [02-agregar_coletas_metrica](/notebooks/02-agregar_coletas_metrica.ipynb): implementa o processamento dos arquivos que agrega os arquivos pré-processados num único arquivo por métrica. Os arquivos resultantes desse processamento estão localizados também nas pasta **processados** em formato CSV. São eles:
  - [consolidado_cpu.csv](/dados/coletas/cpu/processados/consolidado_cpu.csv)
  - [consolidado_memoria.csv](/dados/coletas/memoria/processados/consolidado_memoria.csv)
  - [consolidado_error.csv](/dados/coletas/error/processados/consolidado_error.csv)
  - [consolidado_cpu_throttled.csv](/dados/coletas/throttled/processados/consolidado_cpu_throttled.csv)
- [03-exploracao_dos_dados](/notebooks/03-exploracao_dos_dados.ipynb): implementa a exploração e análise dos dados para melhor compreensão.
- [04-preparar_dados](/notebooks/04-preparar_dados.ipynb): implementa a preparação dos dados para rodar o modelo de classificação. Nessa etapa também é feita a rotulação dos contêineres com base nos flavors definidos.

## Treinamento

A separação do dataset em dados de treinamento e testes, bem como o treinamento e avaliação do treinamento está implementado no notebook
[05-treinamento_classificacao](/notebooks/05-treinamento_classificacao.ipynb).
O modelo de Árvore de Decisão treinado com critério **entropy**, está salvo no formato pickle em [decision_tree_classifier_entropy.pkl](/notebooks/decision_tree_classifier_entropy.pkl)

O notebook [06-teste-outro-dataset](/notebooks/06-teste-outro-dataset.ipynb) carrega o modelo treinado e realiza predições com dados de teste obtidos de uma coleta de 24 horas realizada em outro dia (**coleta_dia_2**). Depois são obtidas as métricas de avaliação (acurária, precisão, recall).
- 


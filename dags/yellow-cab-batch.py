from airflow import DAG
import os
import base64
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import timedelta
from airflow.utils.dates import days_ago

service_account_path = "/tmp/airflow-gcp-key.json"
service_account_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if service_account_key:
    with open(service_account_path, "wb") as key_file:
        print("Writing service account key to temporary file...")
        key_file.write(base64.b64decode(service_account_key))

PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = os.getenv("DATASET_ID")

default_args = {
    "owner": "hafidz",
    "retry_delay": timedelta(minutes=5),
}

spark_dag = DAG(
    dag_id="etl_yellow_cab",
    default_args=default_args,
    schedule_interval=None,
    dagrun_timeout=timedelta(minutes=60),
    description="",
    start_date=days_ago(1),
)

# SparkSubmitOperator to execute the PySpark script
ETL = SparkSubmitOperator(
    application='/spark-scripts/taxi_etl.py',
    conn_id="spark_main",
    task_id='etl_task',
    env_vars={
        "PROJECT_ID": PROJECT_ID,
        "DATASET_ID": DATASET_ID,
        "GOOGLE_APPLICATION_CREDENTIALS": service_account_path
    },
    conf={
        "spark.jars.packages": "org.apache.sedona:sedona-python-adapter-3.0_2.12:1.2.0-incubating,"
                               "org.datasyslab:geotools-wrapper:geotools-24.0",
        "spark.jars.repositories": "https://repo1.maven.org/maven2/"
    },
    dag=spark_dag
)

ETL
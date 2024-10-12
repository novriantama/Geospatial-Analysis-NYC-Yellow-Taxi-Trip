from airflow import DAG
import os
import base64
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago
from airflow.models import Variable

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
    # Run once a day at 11 PM Jakarta time
    schedule_interval="0 23 * * *", 
    dagrun_timeout=timedelta(minutes=60),
    description="",
    start_date=days_ago(1)
)

# Task to dynamically generate the filename
def generate_filename(**kwargs):
    execution_date = kwargs['execution_date']
    # Format the date into YYYY-MM-DD
    formatted_date = execution_date.strftime('%Y-%m-%d') 
    filename = f"yellow_tripdata_{formatted_date}.csv"
    Variable.set("filename", filename)  # Store in Airflow Variable
    return filename

# Generate filename task
generate_filename_task = PythonOperator(
    task_id="generate_filename",
    python_callable=generate_filename,
    provide_context=True,
    dag=spark_dag
)

# SparkSubmitOperator to execute the PySpark script
ETL = SparkSubmitOperator(
    application='/spark-scripts/taxi_etl.py',
    conn_id="spark_main",
    task_id='etl_task',
    env_vars={
        "PROJECT_ID": PROJECT_ID,
        "DATASET_ID": DATASET_ID,
        "GOOGLE_APPLICATION_CREDENTIALS": service_account_path,
        "FILENAME": "{{ var.value.filename }}"  # Access filename from Variable
    },
    conf={
        "spark.jars.packages": "org.apache.sedona:sedona-python-adapter-3.0_2.12:1.2.0-incubating,"
                               "org.datasyslab:geotools-wrapper:geotools-24.0",
        "spark.jars.repositories": "https://repo1.maven.org/maven2/",
        "spark.executor.memory": "8g", 
        "spark.driver.maxResultSize": "8g",
        "spark.driver.memory": "2g"
    },
    dag=spark_dag
)

generate_filename_task >> ETL  # Set task dependency
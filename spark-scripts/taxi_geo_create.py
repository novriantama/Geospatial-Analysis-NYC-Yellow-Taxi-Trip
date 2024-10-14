import os
from google.cloud import bigquery
from pyspark.sql import SparkSession

DATASET_ID = os.environ.get("DATASET_ID")
credentials_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

def main():
    spark = SparkSession.builder \
        .appName("BigQueryCreateGeo")
    spark.config("log4j.logger.org.apache.spark", "DEBUG")
    
    client = bigquery.Client.from_service_account_json(credentials_file)
    source_table_ref = client.dataset(DATASET_ID).table('fact_trip')

    query = f"""
    CREATE OR REPLACE TABLE `{DATASET_ID}.new_fact_trip` AS
        SELECT 
            *,
            ST_GEOGPOINT(pickup_longitude, pickup_latitude) AS pickup_location,
            ST_GEOGPOINT(dropoff_longitude, dropoff_latitude) AS dropoff_location
        FROM `{source_table_ref}`
    """

    job_config = bigquery.QueryJobConfig()

    query_job = client.query(query, job_config=job_config)
    query_job.result()

if __name__ == "__main__":
    main()


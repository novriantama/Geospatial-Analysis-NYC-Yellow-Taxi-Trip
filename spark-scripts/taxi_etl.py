import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from sedona.register import SedonaRegistrator
from pyspark.sql.functions import expr
from google.cloud import bigquery
from pyspark.sql.functions import to_timestamp

PROJECT_ID = os.environ.get("PROJECT_ID")
DATASET_ID = os.environ.get("DATASET_ID")
credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def main():
    spark = SparkSession.builder \
        .appName("BigQueryETL") \
        .config("spark.jars.packages", "org.apache.sedona:sedona-python-adapter-3.0_2.12:1.2.0-incubating,"
                                      "org.datasyslab:geotools-wrapper:geotools-24.0") \
        .config("spark.jars.repositories", "https://repo1.maven.org/maven2/") \
        .config("viewsEnabled", "true") \
        .config("materializationDataset", DATASET_ID) \
        .config("credentialsFile", credentials_file) \
        .config("parentProject", PROJECT_ID) \
        .config("spark.driver.extraJavaOptions", "-Dlog4j.debug") \
        .config("log4j.logger.org.apache.spark", "DEBUG") \
        .getOrCreate()

    SedonaRegistrator.registerAll(spark)

    client = bigquery.Client.from_service_account_json(credentials_file)

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",  
        create_disposition="CREATE_IF_NEEDED",
    )

    # Read the CSV data
    df = spark.read.csv(
        "/data/yellow_tripdata_2016-01.csv",
        header=True,
        inferSchema=True
    )

    # --- Data Cleaning ---
    # Remove rows with missing values in key columns
    df = df.dropna(subset=["tpep_pickup_datetime", "tpep_dropoff_datetime", "pickup_longitude", "pickup_latitude"])

    # --- Create Dimension Tables ---
    dim_vendor = df.select("VendorID").distinct().withColumnRenamed("VendorID", "Vendor_Name")

    # Create Dim_Datetime
    dim_datetime = df.select(
        "tpep_pickup_datetime"
    ).distinct().withColumn(
        "Datetime", to_timestamp("tpep_pickup_datetime")
    ).withColumn(
        "Year", year("Datetime")
    ).withColumn(
        "Month", month("Datetime")
    ).withColumn(
        "Day", dayofmonth("Datetime")
    ).withColumn(
        "Hour", hour("Datetime")
    ).withColumn(
        "Day_of_Week", dayofweek("Datetime")
    ).withColumn(
        "Weekend_Indicator", when(dayofweek("Datetime").isin(1, 7), True).otherwise(False).cast(BooleanType())
    )

    # --- Create Fact Table ---
    fact_trip = df.withColumn(
        "Trip_Duration",
        (unix_timestamp("tpep_dropoff_datetime") - unix_timestamp("tpep_pickup_datetime")) / 60
    ).withColumn(
        "Pickup_Point",
        expr(f"ST_Point(pickup_longitude, pickup_latitude)")
    ).withColumn(
        "Dropoff_Point",
        expr(f"ST_Point(dropoff_longitude, dropoff_latitude)")
    ).withColumn(
        "Trip_Distance_Calculated",
        expr(f"ST_Distance(Pickup_Point, Dropoff_Point)")
    ).withColumn(
        "Pickup_Point_WKB", 
        expr(f"ST_AsBinary(Pickup_Point)").cast(BinaryType())  
    ).withColumn(
        "Dropoff_Point_WKB", 
        expr(f"ST_AsBinary(Dropoff_Point)").cast(BinaryType())  
    ).select(
        "VendorID",
        "payment_type",
        "pickup_longitude",
        "pickup_latitude",
        "dropoff_longitude",
        "dropoff_latitude",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "fare_amount",
        "extra",
        "mta_tax",
        "tip_amount",
        "tolls_amount",
        "improvement_surcharge",
        "total_amount",
        "Trip_Duration",
        "store_and_fwd_flag",
        "Pickup_Point_WKB",
        "Dropoff_Point_WKB",
        "Trip_Distance_Calculated"
    )

    fact_trip.drop("Dropoff_Point", "Pickup_Point")

    fact_trip.show(10)

    # --- Save the data (example: to Parquet files) ---
    dim_vendor_write = client.load_table_from_dataframe(dim_vendor.toPandas(), f"{PROJECT_ID}.{DATASET_ID}.dim_vendor", job_config=job_config)
    dim_vendor_write.result()

    dim_datetime_write = client.load_table_from_dataframe(dim_datetime.toPandas(), f"{PROJECT_ID}.{DATASET_ID}.dim_datetime", job_config=job_config)
    dim_datetime_write.result()

    fact_trip_write = client.load_table_from_dataframe(fact_trip.toPandas(), f"{PROJECT_ID}.{DATASET_ID}.fact_trip", job_config=job_config)
    fact_trip_write.result()

    spark.stop()

if __name__ == "__main__":
    main()
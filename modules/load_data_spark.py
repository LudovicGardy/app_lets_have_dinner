from modules.cache_data_fun import create_cache_decorator
from logger.logger import loading_logger

from dotenv import dotenv_values

# Load environment variables
config = dotenv_values(".env")
from pyspark.sql import SparkSession

# Initialize cache decorator for caching data
cache_decorator = create_cache_decorator(force_lru_cache=True)


@cache_decorator
def load_restaurants_from_parquet_spark(parquet_file_path: str) -> object:
    """
    Load restaurant data from a Parquet file using Apache Spark.

    :param spark: Spark session object.
    :param parquet_file_path: Path to the Parquet file.
    :return: DataFrame containing restaurant data, or None in case of failure.
    """
    loading_logger.info("Loading data from Parquet using Spark.")

    try:
        spark_session = SparkSession.builder.appName("letsdine").getOrCreate()

        # Read data from Parquet file
        restaurants_df = spark_session.read.parquet(
            parquet_file_path, header=True, inferSchema=True
        )

        # Drop missing values
        restaurants_df = restaurants_df.na.drop()

        # Ensure correct data types for latitude and longitude
        restaurants_df = restaurants_df.withColumn(
            "latitude", restaurants_df["latitude"].cast("float")
        ).withColumn("longitude", restaurants_df["longitude"].cast("float"))

        return spark_session, restaurants_df
    except Exception as e:
        loading_logger.error(f"Error while loading the Parquet file: {e}")
        raise f"Error while loading the Parquet file: {e}"

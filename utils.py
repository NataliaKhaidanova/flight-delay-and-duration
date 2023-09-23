from pyspark.sql import SparkSession
from pyspark.sql.functions import round
from pyspark.sql.functions import when
from pyspark.ml.feature import StringIndexer 
from pyspark.ml.feature import VectorAssembler

# Create SparkSession object
spark = SparkSession.builder \
                    .master('local[*]') \
                    .appName('flight') \
                    .getOrCreate()
                    
# DATA PREPARATION
def train_test_split():
    """
    """
    flights = spark.read.csv('flights.csv', sep=',', header=True, inferSchema=True, nullValue='NA')

    print('The data contains %d records.' % flights.count())

    flights = flights.drop('flight') # Remove the "flight" column

    # All missing values come from the "delay" column (as stated from the data analysis) 
    print('The data contains %d missing values.' % flights.filter('delay IS NULL').count()) 
    # Remove records with missing "delay" values 
    flights = flights.filter('delay IS NOT NULL') 
    # Or remove records with missing values in any column and get the number of remaining rows
    flights = flights.dropna() 
    print('The data contains %d records after removing the missing values.' % flights.count())

    # Convert "mile" to "km" and drop "mile" column (1 mile is equivalent to 1.60934 km)
    flights = flights.withColumn('km', round(flights.mile * 1.60934, 0)) \
                     .drop('mile')

    # Create "label" column indicating whether flight was delayed (1) or not (0)
    flights = flights.withColumn('label', (when (flights.delay >= 15, 1)
    .otherwise (0)).cast('integer'))

    # Create an indexer, create a new column with numeric index values for string data
    flights_indexed = StringIndexer(inputCol='carrier', outputCol='carrier_idx').fit(flights).transform(flights)
    flights_indexed = StringIndexer(inputCol='org', outputCol='org_idx').fit(flights_indexed).transform(flights_indexed)
    flights_indexed.show(5)

    # Create an assembler object
    assembler = VectorAssembler(inputCols=['mon','dom','dow','carrier_idx','org_idx','km','depart','duration'], outputCol='features')
    # Consolidate predictor columns
    flights_assembled = assembler.transform(flights_indexed)
    # Check the resulting column
    flights_assembled.select('features', 'delay').show(5, truncate=False)
    
    # Split into training and testing sets in a 80:20 ratio
    flights_train, flights_test = flights_assembled.randomSplit([0.8, 0.2], seed=43)

    # Check that training set has around 80% of records
    training_ratio = flights_train.count() / flights_assembled.count()
    print('Training ratio to the whole data: {}.' .format(training_ratio))
    
    return flights_train, flights_test
# TPC-H Divergent Design Index Tuning Benchmarker

The [TPC-H benchmark](https://www.tpc.org/tpch/) is an industry standard decision support benchmark for a single database. To compare the performance of divergent design index tuning algorithms, such as [qDINA](https://github.com/const-sambird/dina), it is necessary to run the benchmarks in such a manner that each query template can be routed to a different replica based on the index recommendation.

> [!IMPORTANT]
> This implementation is based on [tpch-pgsql](https://github.com/Data-Science-Platform/tpch-pgsql), a Python implementation of the TPC-H benchmark for PostgreSQL. The installation instructions are based on that, but the usage is slightly different.

### Requirements
* The benchmark requires TPC-H dbgen:
```
wget -q https://github.com/electrum/tpch-dbgen/archive/32f1c1b92d1664dba542e927d23d86ffa57aa253.zip -O tpch-dbgen.zip
unzip -q tpch-dbgen.zip && mv tpch-dbgen-32f1c1b92d1664dba542e927d23d86ffa57aa253 tpch-dbgen && rm tpch-dbgen.zip
```
* gcc

```
gcc --version
```

* python3

```
python3 --version
```

* python requirements

```
pip3 install -r requirements.txt
```

* some running instances of Postgres

Also make sure that you have full rights on the target databases (GRANT ALL PRIVILEGES)

### Usage

```
usage: bench.py [-h] [-r REPLICA_PATH] [-i INDEX_CONFIG_PATH] [-t ROUTE_TABLE_PATH] [-s SCALE_FACTOR] [-v] {prepare,run}

positional arguments:
  {prepare,run}         prepare the data or load the benchmark?

options:
  -h, --help            show this help message and exit
  -r REPLICA_PATH, --replica-path REPLICA_PATH
                        the path to the replica configuration
  -i INDEX_CONFIG_PATH, --index-config-path INDEX_CONFIG_PATH
                        the path to the index configuration file
  -t ROUTE_TABLE_PATH, --route-table-path ROUTE_TABLE_PATH
                        the path to the routeing table file
  -s SCALE_FACTOR, --scale-factor SCALE_FACTOR
                        TPC-H scale factor
  -v, --verbose         more verbose output is required
```

The script expects three inputs:

* The *index configuration*, which describes the indexes to be constructed on the replicas
* The *routeing table*, which describes which query templates should be routed to which replicas
* The *replica file*, which gives the configuration parameters for each replica

Additional flags can be used to set the TPC-H scale factor and to enable more verbose logging.

#### 1. Create the query data

```
python bench.py -s [SCALE_FACTOR] prepare
```

#### 2. Create configuration files

**Index configuration**

Each row of the index configuration file should specify a single index to create on a given replica, in the format `replica_id,column_1,column_2,...,column_n`. For example, if our desired index configuration looks something like this:

Replica|Indexes
-------|-------
0      |('p_name',), ('l_commitdate', 'l_orderkey', 'l_receiptdate', 'l_suppkey')
1      |('ps_suppkey',), ('p_container', 'p_size'), ('l_partkey', 'l_shipmode')

Then the index configuration file should have the following format:

```
0,p_name
0,l_commitdate,l_orderkey,l_receiptdate,l_suppkey
1,ps_suppkey
1,p_container,p_size
1,l_partkey,l_shipmode
```

**Routeing table**

The TPC-H benchmark has 22 query templates. The routeing table should be a one-line file that specifies the ID of each replica that the template at the relevant position. An example is given below (note the 22 entries):

```
1,0,1,0,0,0,0,0,1,0,1,1,1,1,1,1,1,0,0,0,1,0
```

**Replica file**

The replica file should contain one line for every database replica we should benchmark on, in the format:

```
ID (integer),hostname,port,dbname,username,password
```

#### 3. Run benchmarks

```
python bench.py -r [REPLICA_PATH] -i [INDEX_CONFIG_PATH] -t [ROUTE_TABLE_PATH] -s [SCALE_FACTOR] run
```

import argparse
import os
from replica import Replica
from tpcbench import query

PREFIXES = {
    'l': 'LINEITEM',
    'p': 'PART',
    'ps': 'PARTSUPP',
    'o': 'ORDERS',
    'c': 'CUSTOMER',
    'n': 'NATION',
    'r': 'REGION',
    's': 'SUPPLIER'
}

def get_index_config(path: str, replicas: list[Replica]) -> list[tuple[str]]:
    indexes = []
    for replica in replicas:
        indexes.append([])
    
    with open(path, 'r') as infile:
        lines = infile.readlines()
        for index in lines:
            fields = index.split(',')
            to_replica = int(fields[0])
            table = table_from_column_prefix(fields[1])
            indexes[to_replica].append([table, fields[1:]])
    
    return indexes

def get_routeing_table(path: str) -> list[int]:
    routes = None

    with open(path, 'r') as infile:
        table = infile.readline()
        routes = table.split(',')
        routes = [int(r) for r in routes]
    
    return routes

def get_replicas(path: str) -> list[Replica]:
    replicas = []
    with open(path, 'r') as infile:
        lines = infile.readlines()
        for config in lines:
            fields = config.split(',')
            replicas.append(
                Replica(
                    id=int(fields[0]),
                    hostname=fields[1],
                    port=fields[2],
                    dbname=fields[3],
                    user=fields[4],
                    password=fields[5]
                )
            )
    return replicas

def table_from_column_prefix(column: str) -> str:
    '''
    Given the name of a column in the TPC-H benchmark,
    returns the name of the table it is on based on the
    prefix attached to the column name.

    :param column: the column name (eg ps_suppkey)
    :returns: the table name (eg PARTSUPP)
    '''
    prefix = column.split('_')[0]

    return PREFIXES[prefix]

def create_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--replica-path', type=str, default='replicas.csv', help='the path to the replica configuration')
    parser.add_argument('-i', '--index-config-path', type=str, default='index_config.csv', help='the path to the index configuration file')
    parser.add_argument('-t', '--route-table-path', type=str, default='routes.csv', help='the path to the routeing table file')
    parser.add_argument('-s', '--scale-factor', type=int, default=1, help='TPC-H scale factor')
    parser.add_argument('-v', '--verbose', action='store_true', help='more verbose output is required')

    parser.add_argument('phase', choices=['prepare', 'run'], help='prepare the data or load the benchmark?')

    return parser.parse_args()

if __name__ == '__main__':
    args = create_arguments()

    REPLICA_PATH = os.path.join('.', args.replica_path)
    INDEX_CONFIG_PATH = os.path.join('.', args.index_config_path)
    ROUTE_TABLE_PATH = os.path.join('.', args.route_table_path)
    SCALE_FACTOR = args.scale_factor
    IS_VERBOSE = args.verbose
    PHASE = args.phase

    if PHASE == 'run':
        replicas = get_replicas(REPLICA_PATH)
        indexes = get_index_config(INDEX_CONFIG_PATH, replicas)
        routes = get_routeing_table(ROUTE_TABLE_PATH)
    else:
        replicas = []
        indexes = []
        routes = []

    query.main(
        phase=PHASE,
        replicas=replicas,
        routes=routes,
        index_config=indexes,
        scale=SCALE_FACTOR,
        verbose=IS_VERBOSE
    )

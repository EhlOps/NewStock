from google.cloud import bigquery
from query import create_query

bq = bigquery.Client()
project = bq.project

def sim_query():
    query = create_query(
        f'SELECT * FROM `{project}.newstock.gdelt` '
        'WHERE source = \'nytimes.com\' '
        'LIMIT 50'
    )
    print(query)
    query_job = bq.query(query)
    rows = query_job.result()
    for row in rows:
        print(row)
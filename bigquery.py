from google.cloud import bigquery

bq = bigquery.Client()
project = bq.project

def sim_query():
    query = (
        f'SELECT * FROM `{project}.newstock.gdelt`'
        'WHERE publish_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)'
        'AND source = \'nytimes.com\''
        'LIMIT 10'
    )
    query_job = bq.query(query)
    rows = query_job.result()
    for row in rows:
        print(row)
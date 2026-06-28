import os
import re

DATE_FILTER = "publish_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)"


def create_query(query_str: str) -> str:
    if os.environ.get("DEV"):
        # demote any existing WHERE to AND so our WHERE can lead the clause
        query_str = re.sub(r"(?i)\bWHERE\b", "AND", query_str, count=1)
        # insert our WHERE on the line after the FROM statement
        query_str = re.sub(
            r"(?i)(\bFROM\b\s+\S+)",
            rf"\1\nWHERE {DATE_FILTER}",
            query_str,
            count=1,
        )
    return query_str

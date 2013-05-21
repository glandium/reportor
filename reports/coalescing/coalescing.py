#!/usr/bin/env python
import os
import requests
import datetime
import json
import time
import logging
import sqlalchemy as sa
from reportor.utils import td2s, dt2ts

def get_jobs(db, branch, start, end):
    q = sa.text("""
    SELECT buildrequests.complete_at, count(*) as c FROM
        buildsets, buildrequests WHERE
        buildrequests.buildsetid = buildsets.id AND
        buildrequests.buildername like :branch AND
        buildsets.complete_at >= :start AND
        buildsets.complete_at < :end AND
        buildrequests.complete_at IS NOT NULL AND
        buildrequests.complete = 1

        GROUP BY buildrequests.buildername, buildrequests.claimed_at, buildrequests.claimed_by_name, buildrequests.claimed_by_incarnation
        ORDER BY complete_at ASC
        """)
    builds = db.execute(q, start=start, end=end, branch='%{0}%'.format(branch))
    return list(builds)

if __name__ == '__main__':
    import reportor.db
    db = reportor.db.db_from_config('scheduler_db')

    now = time.time()
    start = now - 45*86400

    s = time.time()

    jobs = get_jobs(db, 'mozilla-inbound', start, now)
    results = []
    for j in jobs:
        results.append((j.complete_at, j.c))

    e = time.time()
    report = {
            "data": results,
            "report_start": s,
            "report_elapsed": e-s,
            "data_start": start,
            "data_end": now,
            }
    print json.dumps(report)

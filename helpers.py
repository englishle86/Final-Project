from functools import wraps
from flask import g, request, redirect, url_for
from datetime import datetime, timedelta
import csv

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def week_of():
    now = datetime.now()
    day = now.weekday()
    if day == 4:
        dt = datetime.today()
        date_time = dt.split(" ")
        week_starting = date_time[0]
        print(date_time, week_starting)
    
    elif day > 4:
        days_to_subtract = day - 4
        return(datetime.today() - timedelta(days=days_to_subtract))

    elif day < 4:
        days_to_subtract = (day - 4) + 7
        return(datetime.today() - timedelta(days=days_to_subtract))

def get_jobs():    
    with open('jobs.csv', mode='r') as infile:
        reader = csv.reader(infile)
        with open('jobs_new.csv', mode='w') as outfile:
            writer = csv.writer(outfile)
            jobs = {rows[0]:rows[1] for rows in reader}
            return jobs

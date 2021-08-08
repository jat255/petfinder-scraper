from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import sqlite3
from dateutil.parser import parse

app = Flask(__name__)
Bootstrap(app)

@app.route("/")
def list():
   con = sqlite3.connect("dogs.db")
   con.row_factory = sqlite3.Row
   
   cur = con.cursor()
   cur.execute("SELECT d.name, d.link, d.photoLink, d.breed, d.firstSeen, d.sex, "
               "       o.name AS org_name, o.url AS org_link FROM dogs d "
               "INNER JOIN orgs o ON d.org = o.id")
   
   rows = cur.fetchall(); 

   return render_template("doglist.html", rows = rows)

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = parse(date)
    native = date.replace(tzinfo=None)
    format='%b %e\n%l:%M %p'
    return native.strftime(format).strip()
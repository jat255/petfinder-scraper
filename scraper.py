import sqlite3
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

from requests.api import request

load_dotenv()

placeholder_im = 'https://graphicriver.img.customer.envatousercontent.com/files/270440720/CartoonDogPointer%20p.jpg?auto=compress%2Cformat&q=80&fit=crop&crop=top&max-h=8000&max-w=590&s=d7ccf47eef9f9a8f679c134cc70bffa5'

def dict_factory(cursor, row):
    """
    Helper to get sqlite response as dict instead of tuple
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_dogs(token):
    url = 'https://api.petfinder.com/v2/animals/' + \
          '?type=Dog&location=80305&age=baby&size=medium&sort=recent'

    r = requests.get(url, headers={"Authorization": token})
    if r.status_code != 200:
        raise requests.exceptions.RequestException(f"Getting dogs returned invalid status code: {r.status_code}")

    return r.json()['animals']


def make_html(dogs_list):
    def _make_header():
        return """
                <!doctype html>

                <html lang="en">
                <head>
                  <meta charset="utf-8">
                  <title>$NUMDOGS new dogs on Petfinder as of {0}</title>
                  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.3/css/bootstrap.min.css" integrity="sha384-Zug+QiDoJOrZ5t4lssLdxGhVrurbmBWopoEl+M6BdEfwnCJZtKxi1KgxUyJq13dy" crossorigin="anonymous">
                </head>

                <body>
                <div class="row align-items-center justify-content-center">
                    $NUMDOGS new dogs on Petfinder as of {0} <br />
                    View complete database of dogs <a href="http://192.168.1.17/" 
                    target="_blank">here</a> (must be at home or connected to VPN).
                </div>
                <br />
                <div class="row align-items-center justify-content-center">
                <table style="width:70%" class="table table-hover">
                    <thead class="thead-light">
                    <tr>
                        <th>Name</th>
                        <th>Picture</th>
                        <th>Breed</th>
                        <th>Sex</th>
                        <th>Organization</th>
                    </tr>
                    </thead>
                    <tbody>
                """.format(now.strftime('%A, %b %-d - %-I:%M %P'))

    def _make_row(dog_dict):
        row = f"""
               <tr>
                <td><a href="{dog_dict['link']}">{dog_dict['name']}</a></td>
               """
        if dog_dict['photoLink']:
            row += f"""<td><img src={dog_dict['photoLink']} class="img-fluid img-thumbnail" 
                      style="max-height:300px;"></td>
                    """
        else:
            row += f"""<td><img src={placeholder_im} class="img-fluid img-thumbnail" 
                      style="max-height:300px;"></td>
                    """
        row +=  f"""
                    <td>{dog_dict['breed']}</td>
                    <td>{dog_dict['sex']}</td>
                    <td>
                        <a href={dog_dict['org_link']} target='_blank'>
                            {dog_dict['org_name']}
                        </a>
                    </td>
                    </tr>
                """

        return row

    def _make_footer():
        return """</div></tbody></table>"""

    html = ''
    html += _make_header()
    i = 0
    for d in dogs_list:
        html += _make_row(d)
    html += _make_footer()

    html = html.replace('$NUMDOGS', '{}'.format(len(dogs_list)))

    return html


def send_email(html, num_dogs):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    me = os.environ['GMAIL_EMAIL']
    you1 = os.environ['SEND_TO_1']
    you2 = os.environ['SEND_TO_2']
    
    for you in [you1, you2]:
        # skip sending if the "to" email isn't defined 
        if you == "":
            continue

        # Create message container - the
        # correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"{num_dogs} new dogs on " \
                         f"Petfinder - {now.strftime('%A, %b %-d - %-I:%M %P')}"
        msg['From'] = me
        msg['To'] = you

        # Record the MIME types of both parts - text/plain and text/html.
        part2 = MIMEText(html, 'html')
        msg.attach(part2)
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(me, os.environ['GMAIL_PASS'])
        server.sendmail(me, you,
                        msg.as_string())
        print(f"Sending email notification to {you} from {me}")
        server.quit()

def get_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": os.environ['API_KEY'],
        "client_secret": os.environ['API_SECRET']
    }
    url = f"https://api.petfinder.com/v2/oauth2/token" 
    r = requests.post(url, json=data)

    if r.status_code == 200:
        return f"{r.json()['token_type']} {r.json()['access_token']}"
    else:
        raise requests.exceptions.RequestException(
            f"Unexpected status_code: {r.status_code}")


def add_org(org_id, con, token):
    """
    Add an organization to the DB, fetching info from the API
    """
    url = f'https://api.petfinder.com/v2/organizations/{org_id}'

    r = requests.get(url, headers={"Authorization": token})
    if r.status_code != 200:
        raise requests.exceptions.RequestException(f"Getting org details returned invalid status code: {r.status_code}")

    org_data = r.json()['organization']

    insert_q = f"INSERT INTO orgs (id, name, email, url, phone) VALUES" + \
               f"(?, ?, ?, ?, ?)"
    
    with con:
        con.execute(insert_q, 
            (org_data['id'], org_data['name'], 
             org_data['email'], org_data['url'], 
             org_data['phone']))



def process_results(data, con, token):
    """
    Process a list of results and insert dogs/orgs as needed into DB

    data : list
        The list of animals returned by the API
    con : sqlite3.connection
        The connection object to the DB
    """
    now = datetime.now()
    for d in data:
        dog_id = d['id']
        org_id = d['organization_id']
        link = d['url']
        if d['primary_photo_cropped'] is not None:
            photoLink = d['primary_photo_cropped']['full']
        else:
            photoLink = placeholder_im
        breed = d['breeds']['primary']
        if d['breeds']['secondary'] is not None:
            breed = breed + ' / ' + d['breeds']['secondary']
        name = d['name'].strip().capitalize()
        age = d['age']
        sex = d['gender']

        insert_q = f"INSERT INTO dogs (id, firstSeen, name, age, breed, sex, link, photoLink, org) VALUES" + \
	               "(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        insert_vals = (dog_id, now, name, age, breed, sex, link, photoLink, org_id)

        get_dog_q = f"SELECT * FROM dogs WHERE id = ?"
        get_org_q = f"SELECT * FROM orgs WHERE id = ?"
        
        with con:
            if len(con.execute(get_dog_q, (dog_id, )).fetchall()) > 0:
                print(f"Dog {dog_id} named {name} already in DB, skipping")
                continue
        
        with con:
            if len(con.execute(get_org_q, (org_id, )).fetchall()) == 0:
                # org was not found in DB, so we need to add it
                print(f'Adding org_id: {org_id}')
                add_org(org_id, con, token)
                    
        with con:
            print(f"Adding dog with name {name} and id {dog_id}")
            con.execute(insert_q, insert_vals)

    con.row_factory = dict_factory
    with con:
        # get all dogs added in last 10 minutes
        new_dogs = con.execute(
            "SELECT d.name, d.link, d.photoLink, d.breed, d.firstSeen, "
                   "d.sex, o.name AS org_name, o.url AS org_link "
            "FROM dogs d INNER JOIN orgs o ON d.org = o.id "
            "WHERE d.firstSeen > ? "
            "ORDER BY firstSeen DESC", 
            (now - timedelta(minutes=10), )).fetchall()

    return new_dogs


if __name__ == "__main__":

    now = datetime.now()

    print("Getting API token...")
    token = get_token()

    db_name = 'dogs.db'
    con = sqlite3.connect(db_name)

    print("Fetching results from Petfinder...")
    data = get_dogs(token)

    print("Processing results...")
    new_dogs = process_results(data, con, token)

    if len(new_dogs) > 0:
        print(f"{len(new_dogs)} new dogs, so sending email")
        send_email(make_html(new_dogs), len(new_dogs))
    else:
        print("No new dogs at this time!")
    print("")

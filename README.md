# PetFinder Scraper

*Note, this is totally for personal use, and hasn't been made particularly generic at all*

This app will do three things:

- Probe the PetFinder API for dogs nearby matching a certain criteria, and load them into a local SQLite database
- Send emails to the specified addresses in `.env` when new dogs are found
- Display the database in a simple Flask app 

## Requirements

- Clone this repo somewhere
- API access from PetFinder: https://www.petfinder.com/developers/v2/docs/
- Install `requests`, `python-dotenv`, `sqlite3`, `flask`, `flask-bootstrap`, `dateutil`, and `uwsgi` (with Python plugin)
- Put something like the following into a crontab:
  - `0 06,09,12,15,18,21 * * * cd /path/to/petfinder-scraper && python scraper.py &> /path/to/petfinder-scraper/scraper.log`
  - (Note, the log file must be named `scraper.log` and placed in the same folder as the app code for it to display in the web page
- Create a `uwsgi` service file to run the web app (`/etc/uwsgi/doggos.ini `) and enable it:

```ini
[uwsgi]
chdir = /path/to/petfinder-scraper
module = webapp:app
plugins = python
http = 0.0.0.0:80
```

- Create an SQLite database with a structure like the following:

```sql
-- orgs definition

CREATE TABLE orgs (
	id TEXT NOT NULL,
	name TEXT,
	email TEXT,
	url TEXT,
	phone TEXT
);

-- dogs definition

CREATE TABLE dogs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
firstSeen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
name TEXT,
age TEXT,
breed TEXT,
sex TEXT,
link TEXT,
photoLink TEXT,
org TEXT,
FOREIGN KEY (org) REFERENCES orgs(id)
);
```

- Edit `.env.example` as necessary and save as `.env` with your PetFinder API key, an SMTP email to send from and two emails to send to (this could be configured better, but I'm lazy and this was the way I first wrote it).

## Web app display

Using the Uwsgi app definition above, you'll get a web page that simply presents both the log file and the contents of the database, which looks something like this:

![image](https://user-images.githubusercontent.com/1278301/129056593-6c38b33b-1716-48c1-bb58-651be9ed9528.png)

## Database display

```
sqlite> select * from orgs;
id     name        email                            url                                             phone
-----  ---------   -----------------------------    ----------------------------------------------  --------------
COxxx  Rescue 1    xxxxxxxxxxxxxxxxxxx@gmail.com    https://www.petfinder.com/member/us/co/xxx/xxx  (888) 888-8888
COxxx  Rescue 2    xxxxxxxxxxxxxxxxxxx@gmail.com    https://www.petfinder.com/member/us/co/xxx/xxx  (888) 888-8888
COxxx  Rescue 3    xxxxxxxxxxxxxxxxxxx@gmail.com    https://www.petfinder.com/member/us/co/xxx/xxx
COxxx  Rescue 4    xxxxxxxxxxxxxxxxxxx@gmail.com    https://www.petfinder.com/member/us/co/xxx/xxx
COxxx  Rescue 5    xxxxxxxxxxxxxxxxxxx@gmail.com    https://www.petfinder.com/member/us/co/xxx/xxx  (888) 888-8888
COxxx  Rescue 6    xxxxxxxxxxxxxxxxxxx@gmail.com    https://www.petfinder.com/member/us/co/xxx/xxx  (888) 888-8888
COxxx  Rescue 7    xxxxxxxxxxxxxxxxxxx@gmail.com    https://www.petfinder.com/member/us/co/xxx/xxx  (888) 888-8888
COxxx  Rescue 8    xxxxxxxxxxxxxxxxxxx@gmail.com    https://www.petfinder.com/member/us/co/xxx/xxx  (888) 888-8888

sqlite> select * from dogs;
id        firstSeen                   name         age   breed                                 sex     link                                             photoLink                                                                       org
--------  --------------------------  -----------  ----  ------------------------------------  ------  -----------------------------------------------  ------------------------------------------------------------------------------  ----- 
525xxxxx  2021-08-08 01:58:21.388559  Dog name 1   Baby  Labrador Retriever                    Male    https://www.petfinder.com/dog/link-to-dogs-page  https://dl5zpyw5k3jeb.cloudfront.net/photos/pets/xxxxxxxxxx/1/?bust=xxxxxxxxxx  COXX3
525xxxxx  2021-08-08 01:58:21.388559  Dog name 2   Baby  Labrador Retriever                    Male    https://www.petfinder.com/dog/link-to-dogs-page  https://dl5zpyw5k3jeb.cloudfront.net/photos/pets/xxxxxxxxxx/1/?bust=xxxxxxxxxx  COXX1
525xxxxx  2021-08-08 01:58:21.388559  Dog name 3   Baby  Shih Tzu                              Male    https://www.petfinder.com/dog/link-to-dogs-page  https://dl5zpyw5k3jeb.cloudfront.net/photos/pets/xxxxxxxxxx/1/?bust=xxxxxxxxxx  COXX7
525xxxxx  2021-08-08 01:58:21.388559  Dog name 4   Baby  Shih Tzu                              Male    https://www.petfinder.com/dog/link-to-dogs-page  https://dl5zpyw5k3jeb.cloudfront.net/photos/pets/xxxxxxxxxx/1/?bust=xxxxxxxxxx  COXX7
525xxxxx  2021-08-08 01:58:21.388559  Dog name 5   Baby  Whippet / Tennessee Treeing Brindle   Female  https://www.petfinder.com/dog/link-to-dogs-page  https://dl5zpyw5k3jeb.cloudfront.net/photos/pets/xxxxxxxxxx/1/?bust=xxxxxxxxxx  COXX8
525xxxxx  2021-08-08 01:58:21.388559  Dog name 6   Baby  Australian Shepherd / Border Collie   Male    https://www.petfinder.com/dog/link-to-dogs-page  https://dl5zpyw5k3jeb.cloudfront.net/photos/pets/xxxxxxxxxx/1/?bust=xxxxxxxxxx  COXX9
525xxxxx  2021-08-08 01:58:21.388559  Dog name 7   Baby  Shepherd                              Female  https://www.petfinder.com/dog/link-to-dogs-page  https://dl5zpyw5k3jeb.cloudfront.net/photos/pets/xxxxxxxxxx/1/?bust=xxxxxxxxxx  COXX7
525xxxxx  2021-08-08 01:58:21.388559  Dog name 8   Baby  Labrador Retriever                    Female  https://www.petfinder.com/dog/link-to-dogs-page  https://dl5zpyw5k3jeb.cloudfront.net/photos/pets/xxxxxxxxxx/1/?bust=xxxxxxxxxx  COXX2
525xxxxx  2021-08-08 01:58:21.388559  Dog name 9   Baby  Labrador Retriever                    Female  https://www.petfinder.com/dog/link-to-dogs-page  https://dl5zpyw5k3jeb.cloudfront.net/photos/pets/xxxxxxxxxx/1/?bust=xxxxxxxxxx  COXX2
```

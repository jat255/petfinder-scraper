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
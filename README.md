# CITS5505 Group Project

## Application Description

PerthPins is a Flask web application for discovering, 
sharing, and saving local places around Perth.

---

## Team Members

| UWA ID   | Name.                 | GitHub Username  |
|----------|-----------------------|------------------|
| 24133154 | Zhiqiang Meng         | Michael-24133154 |
| 25086027 | Prathish Vijaya Kumar | prat4677         |
| 24665878 | Zhichao Liu           | Ironman1231      |
|          |                       |                  |


## How to Run the Application

Run all commands from the project root directory.

### Option 1: Run the Application with existing Database

```bash
source .venv/bin/activate
flask --app backend.app run --debug
```

Then open:

```text
http://127.0.0.1:5000
```

### Option 2: Prepare the Database, Then Run the Application

```bash
source .venv/bin/activate
rm backend/migrations/.gitkeep
flask --app backend.app db init
flask --app backend.app db migrate -m "initial schema"
flask --app backend.app db upgrade
flask --app backend.app run --debug
```

The default local SQLite database file is generated at:

```text
backend/instance/perth_explorer.db
```

After the database and migrations have already been created, run the application with:

```bash
source .venv/bin/activate
flask --app backend.app run --debug
```


---

## How to Run the Tests

> TODO
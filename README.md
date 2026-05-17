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

### Install the Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

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

To inspect or roll back the latest database migration:

```bash
flask --app backend.app db history
flask --app backend.app db downgrade 48aac9de597d
flask --app backend.app db upgrade
```


---

## How to Run the Tests

Run all test commands from the project root after installing the dependencies.

```bash
source .venv/bin/activate
```

### Default Test Suite

The default test command runs the Flask test-client tests and skips Selenium
browser tests. These tests use a pytest-only SQLite database under `/private/tmp`
and do not touch the development database.

```bash
python -m pytest
```

To run the same non-browser tests explicitly:

```bash
python -m pytest -m "not selenium"
```

### Selenium Browser Tests

Selenium tests are marked with `selenium` and are not part of the default test
run because they require a local WebDriver-compatible browser. The tests start a
temporary Flask server automatically, seed their own test users, and mock image
upload/delete calls so Cloudflare R2 credentials are not required.

Run Selenium tests with:

```bash
python -m pytest -m selenium
```

By default the Selenium fixture uses Microsoft Edge. To use Chrome instead:

```bash
SELENIUM_BROWSER=chrome python -m pytest -m selenium
```

If no supported browser or matching driver is available, the Selenium tests are
skipped with an explanatory message instead of failing the whole test run.

### Useful Test Commands

Collect tests without running them:

```bash
python -m pytest --collect-only -q
```

Run one test file:

```bash
python -m pytest tests/test_auth.py
```

Run one specific test:

```bash
python -m pytest tests/test_auth.py::test_register_new_user_successfully

The following code will be decided on whether it should be kept after running the test.
> TODO

For test_checkin_selenium.py file, run following code

```bash
pytest tests/test_checkin_selenium.py
```
For test_checkin.py file, run following code
```bash
DATABASE_URL="sqlite:///:memory:" pytest tests/test_checkin.py
```

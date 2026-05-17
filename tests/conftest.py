import sys
import os

# add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Keep pytest away from the development SQLite database. The application reads
# DATABASE_URL while backend.app is imported, so this must run in conftest before
# any test module imports the app object.
os.environ.setdefault(
    "DATABASE_URL",
    f"sqlite:///{os.path.join('/private/tmp', f'perthpins_pytest_{os.getpid()}.db')}",
)

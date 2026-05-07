import sys
import os

# Ensure the project root is on sys.path so both `app.*` and top-level
# packages (routers, schemas, services, utils) resolve correctly.
sys.path.insert(0, os.path.dirname(__file__))

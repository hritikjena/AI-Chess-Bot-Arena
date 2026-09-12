import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Engine.MatchManager import run_match_generator

# Assuming we seeded bots, get the first two from db
from Server.database import SessionLocal
from Server import models

db = SessionLocal()
b1 = db.query(models.Bot).first()
b2 = db.query(models.Bot).offset(1).first()

print(f"Testing match between {b1.filename} and {b2.filename}")
try:
    gen = run_match_generator(b1.filename, b2.filename)
    for i, state in enumerate(gen):
        print(state)
        if i > 2:
            break
except Exception as e:
    import traceback
    traceback.print_exc()

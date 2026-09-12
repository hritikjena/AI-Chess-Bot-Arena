import os
from sqlalchemy.orm import Session
from Server.database import SessionLocal, engine
from Server import models

# Ensure tables are created
models.Base.metadata.create_all(bind=engine)

def seed_bots():
    db = SessionLocal()
    bots_dir = os.path.join(os.path.dirname(__file__), 'bots')
    
    # Get all existing bots to avoid duplicates
    existing_filenames = {bot.filename for bot in db.query(models.Bot).all()}
    
    count = 0
    if os.path.exists(bots_dir):
        for filename in os.listdir(bots_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                if filename not in existing_filenames:
                    # Generate a nice name from filename
                    name = filename.replace('.py', '').replace('_', ' ').title()
                    bot = models.Bot(
                        name=name,
                        filename=filename,
                        description=f"Automated bot entry for {filename}"
                    )
                    db.add(bot)
                    count += 1
        
        db.commit()
    print(f"Successfully seeded {count} new bots into the database.")
    db.close()

if __name__ == "__main__":
    seed_bots()

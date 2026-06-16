import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.database import engine
from backend.models import Base

print("Dropping all existing database tables...")
Base.metadata.drop_all(bind=engine)
print("Recreating database tables with correct schema...")
Base.metadata.create_all(bind=engine)
print("Database tables recreated successfully!")

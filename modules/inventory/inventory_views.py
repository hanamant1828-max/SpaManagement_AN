# Import required models
from models import User
from modules.hanamantinventory.models import HanamanStockMovement

# Get recent transactions - placeholder for now
try:
    transactions = HanamanStockMovement.query.order_by(HanamanStockMovement.created_at.desc()).limit(100).all()
except:
    transactions = []
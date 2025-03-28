import re
from models import Commodity, db
from models import Commodity, UserRation, db  # ✅ Add UserRation here


# NLP Parser to handle multiple items in speech input
def parse_ration_request(user_input):
    pattern = r'(\d+)\s*(kg|liters)?\s*(\w+)'  # Match "5kg rice" or "2 sugar"
    matches = re.findall(pattern, user_input.lower())

    orders = []
    for match in matches:
        quantity, _, item = match
        quantity = int(quantity)
        item = item.strip()

        commodity = Commodity.query.filter_by(name=item).first()
        if commodity:
            orders.append((item, quantity))
    
    return orders

# Update stock function
# Update stock function with confirmation message
def update_stock(user_id, orders):
    response = []
    
    for item, quantity in orders:
        commodity = Commodity.query.filter_by(name=item).first()

        if not commodity or commodity.stock < quantity:
            response.append(f"❌ Not enough {item}. Available: {commodity.stock if commodity else 0}kg.")
            continue
        
        # Fetch user ration quota details
        user_ration = UserRation.query.filter_by(user_id=user_id, commodity=item).first()
        
        if user_ration:
            if user_ration.consumed + quantity > user_ration.quota_limit:
                response.append(f"⚠️ You exceeded your {item} quota! Limit: {user_ration.quota_limit}kg.")
                continue
            user_ration.consumed += quantity
        else:
            response.append(f"⚠️ No ration quota found for {item}")
            continue

        # Deduct stock after confirming user quota
        commodity.stock -= quantity

        # Save changes
        db.session.commit()
        response.append(f"✅ {quantity}kg {item} will be dispensed. Remaining: {commodity.stock}kg.")

    return " | ".join(response)  # Return a user-friendly message

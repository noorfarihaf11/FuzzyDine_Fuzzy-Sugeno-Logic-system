from flask import Flask, render_template, request
import numpy as np
import skfuzzy as fuzz

app = Flask(__name__)


# Membership function definitions
def price_cheap(x):
    if x <= 50000:
        return 1
    elif 50000 < x <= 100000:
        return (100000 - x) / 50000
    else:
        return 0

def price_medium(x):
    if x <= 75000 or x >= 150000:
        return 0
    elif 75000 < x < 112500:
        return (x - 75000) / 37500
    elif 112500 <= x < 150000:
        return (150000 - x) / 37500
    else:
        return 0

def price_expensive(x):
    if x <= 125000:
        return 0
    elif 125000 < x < 200000:
        return (x - 125000) / 75000
    else:
        return 1


def rating_low(x):
    if x <= 2:
        return 1
    if x > 2 and x < 3:
        return (3 - x) / 1
    return 0

def rating_medium(x):
    if x <= 2 or x >= 4:
        return 0
    if x > 2 and x < 3:
        return (x - 2) / 1
    if x >= 3 and x < 4:
        return (4 - x) / 1
    return 0

def rating_high(x):
    if x <= 3:
        return 0
    if 3 < x < 4:
        return (x - 3) / 1
    if 4 <= x <= 5:
        return 1
    return 0


def distance_near(x):
    if x <= 2:
        return 1
    if x > 2 and x < 5:
        return (5 - x) / 3
    return 0

def distance_medium(x):
    if x <= 2 or x >= 8:
        return 0
    if x > 2 and x < 5:
        return (x - 2) / 3
    if x >= 5 and x < 8:
        return (8 - x) / 3
    return 0

def distance_far(x):
    if x <= 5:
        return 0
    if 5 < x < 8:
        return (x - 5) / 3
    if x >= 8:
        return 1
    return 0


# Get membership values for a specific input
def get_membership_values(type_name, value):
    if type_name == "price":
        return {
            "cheap": price_cheap(value),
            "medium": price_medium(value),
            "expensive": price_expensive(value)
        }
    elif type_name == "rating":
        return {
            "low": rating_low(value),
            "medium": rating_medium(value),
            "high": rating_high(value)
        }
    elif type_name == "distance":
        return {
            "near": distance_near(value),
            "medium": distance_medium(value),
            "far": distance_far(value)
        }
    return {}

# Define fuzzy rules
def apply_rules(price, rating, distance):
    rules = [
        # Cheap price
        {"condition": min(price_cheap(price), rating_low(rating), distance_near(distance)), "output": 60, "description": "IF price=cheap AND rating=low AND distance=near"},
        {"condition": min(price_cheap(price), rating_low(rating), distance_medium(distance)), "output": 50, "description": "IF price=cheap AND rating=low AND distance=medium"},
        {"condition": min(price_cheap(price), rating_low(rating), distance_far(distance)), "output": 40, "description": "IF price=cheap AND rating=low AND distance=far"},
        
        {"condition": min(price_cheap(price), rating_medium(rating), distance_near(distance)), "output": 70, "description": "IF price=cheap AND rating=medium AND distance=near"},
        {"condition": min(price_cheap(price), rating_medium(rating), distance_medium(distance)), "output": 60, "description": "IF price=cheap AND rating=medium AND distance=medium"},
        {"condition": min(price_cheap(price), rating_medium(rating), distance_far(distance)), "output": 50, "description": "IF price=cheap AND rating=medium AND distance=far"},
        
        {"condition": min(price_cheap(price), rating_high(rating), distance_near(distance)), "output": 90, "description": "IF price=cheap AND rating=high AND distance=near"},
        {"condition": min(price_cheap(price), rating_high(rating), distance_medium(distance)), "output": 80, "description": "IF price=cheap AND rating=high AND distance=medium"},
        {"condition": min(price_cheap(price), rating_high(rating), distance_far(distance)), "output": 70, "description": "IF price=cheap AND rating=high AND distance=far"},
        
        # Medium price
        {"condition": min(price_medium(price), rating_low(rating), distance_near(distance)), "output": 50, "description": "IF price=medium AND rating=low AND distance=near"},
        {"condition": min(price_medium(price), rating_low(rating), distance_medium(distance)), "output": 40, "description": "IF price=medium AND rating=low AND distance=medium"},
        {"condition": min(price_medium(price), rating_low(rating), distance_far(distance)), "output": 30, "description": "IF price=medium AND rating=low AND distance=far"},
        
        {"condition": min(price_medium(price), rating_medium(rating), distance_near(distance)), "output": 65, "description": "IF price=medium AND rating=medium AND distance=near"},
        {"condition": min(price_medium(price), rating_medium(rating), distance_medium(distance)), "output": 55, "description": "IF price=medium AND rating=medium AND distance=medium"},
        {"condition": min(price_medium(price), rating_medium(rating), distance_far(distance)), "output": 45, "description": "IF price=medium AND rating=medium AND distance=far"},
        
        {"condition": min(price_medium(price), rating_high(rating), distance_near(distance)), "output": 75, "description": "IF price=medium AND rating=high AND distance=near"},
        {"condition": min(price_medium(price), rating_high(rating), distance_medium(distance)), "output": 65, "description": "IF price=medium AND rating=high AND distance=medium"},
        {"condition": min(price_medium(price), rating_high(rating), distance_far(distance)), "output": 55, "description": "IF price=medium AND rating=high AND distance=far"},
        
        # Expensive price
        {"condition": min(price_expensive(price), rating_low(rating), distance_near(distance)), "output": 40, "description": "IF price=expensive AND rating=low AND distance=near"},
        {"condition": min(price_expensive(price), rating_low(rating), distance_medium(distance)), "output": 30, "description": "IF price=expensive AND rating=low AND distance=medium"},
        {"condition": min(price_expensive(price), rating_low(rating), distance_far(distance)), "output": 20, "description": "IF price=expensive AND rating=low AND distance=far"},
        
        {"condition": min(price_expensive(price), rating_medium(rating), distance_near(distance)), "output": 55, "description": "IF price=expensive AND rating=medium AND distance=near"},
        {"condition": min(price_expensive(price), rating_medium(rating), distance_medium(distance)), "output": 45, "description": "IF price=expensive AND rating=medium AND distance=medium"},
        {"condition": min(price_expensive(price), rating_medium(rating), distance_far(distance)), "output": 35, "description": "IF price=expensive AND rating=medium AND distance=far"},
        
        {"condition": min(price_expensive(price), rating_high(rating), distance_near(distance)), "output": 70, "description": "IF price=expensive AND rating=high AND distance=near"},
        {"condition": min(price_expensive(price), rating_high(rating), distance_medium(distance)), "output": 60, "description": "IF price=expensive AND rating=high AND distance=medium"},
        {"condition": min(price_expensive(price), rating_high(rating), distance_far(distance)), "output": 50, "description": "IF price=expensive AND rating=high AND distance=far"},
    ]
    
    # Filter rules with non-zero weights
    active_rules = [rule for rule in rules if rule["condition"] > 0]
    
    return active_rules

# Calculate recommendation using Sugeno method
def calculate_recommendation(price, rating, distance):
    # Apply rules
    rule_results = apply_rules(price, rating, distance)
    
    # Calculate weighted average (Sugeno defuzzification)
    weight_sum = sum(rule["condition"] for rule in rule_results)
    weighted_output_sum = sum(rule["condition"] * rule["output"] for rule in rule_results)
    
    # Calculate final score
    score = weighted_output_sum / weight_sum if weight_sum > 0 else 0
    
    # Determine recommendation category
    category = "Not Recommended"
    if score > 80:
        category = "Highly Recommended"
    elif score > 60:
        category = "Recommended"
    elif score > 40:
        category = "Moderately Recommended"
    elif score > 20:
        category = "Less Recommended"
    
    # Format rule results for display
    rules = [
        {
            "rule": rule["description"],
            "weight": rule["condition"],
            "output": rule["output"]
        } for rule in rule_results
    ]
    
    return {
        "score": score,
        "category": category,
        "rules": rules
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/recommendation', methods=['GET', 'POST'])
def recommendation():
    if request.method == 'POST':
        # Get form data
        price = float(request.form.get('price', 100000))
        rating = float(request.form.get('rating', 3))
        distance = float(request.form.get('distance', 5))
        
        # Calculate membership values
        price_memberships = get_membership_values("price", price)
        rating_memberships = get_membership_values("rating", rating)
        distance_memberships = get_membership_values("distance", distance)
        
        # Calculate recommendation
        result = calculate_recommendation(price, rating, distance)
        
        return render_template(
            'recommendation.html',
            price=price,
            rating=rating,
            distance=distance,
            price_memberships=price_memberships,
            rating_memberships=rating_memberships,
            distance_memberships=distance_memberships,
            result=result
        )
    
    return render_template('recommendation.html')

if __name__ == '__main__':
    app.run(debug=True)

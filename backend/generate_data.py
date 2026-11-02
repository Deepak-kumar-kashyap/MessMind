import pandas as pd
import random
import numpy as np

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
meals = ['Breakfast', 'Lunch', 'Snacks', 'Dinner']
items = ['Rice', 'Biryani', 'Dosa', 'Chapati', 'Samosa', 'Puff', 'Sandwich', 'Noodles', 'Idli']
weathers = ['Sunny', 'Rainy', 'Cloudy', 'Cold']
events = ['No', 'Festival', 'Holiday', 'Exam', 'Sports Meet']

random.seed(42)
np.random.seed(42)

data = []

# Generate 3000 realistic records
for _ in range(3000):
    day = random.choice(days)
    meal = random.choice(meals)
    
    # Restrict items logically based on meal type for realism
    if meal == 'Breakfast':
        item = random.choice(['Dosa', 'Idli', 'Sandwich'])
    elif meal == 'Snacks':
        item = random.choice(['Samosa', 'Puff', 'Noodles', 'Sandwich'])
    else:
        item = random.choice(['Rice', 'Biryani', 'Chapati', 'Noodles'])
        
    weather = random.choice(weathers)
    event = random.choice(events)
    
    # Base demand
    demand = random.randint(100, 150)
    
    # Inject some correlations so the model can learn patterns
    if item == 'Biryani' or item == 'Samosa':
        demand += random.randint(30, 80)
    elif item == 'Chapati' or item == 'Puff':
        demand -= random.randint(10, 30)
        
    if event == 'Festival' or event == 'Sports Meet':
        demand += random.randint(50, 100)
    elif event == 'Holiday':
        if meal in ['Lunch', 'Breakfast']:
           demand += random.randint(20, 60)
        else:
           demand -= random.randint(20, 40)
    elif event == 'Exam':
        demand -= random.randint(10, 50)
        
    if weather in ['Rainy', 'Cold']:
        if meal == 'Snacks':
            demand += random.randint(20, 50) # more snacks on rainy days
        else:
            demand -= random.randint(10, 30)
    elif weather == 'Sunny':
        if meal != 'Snacks':
            demand += random.randint(10, 20)
        
    if day in ['Saturday', 'Sunday']:
        if meal == 'Dinner':
            demand += random.randint(20, 50)
        elif meal == 'Lunch':
            demand += random.randint(10, 30)
            
    # Ensure no negative demand
    demand = max(10, demand)
            
    data.append([day, meal, item, weather, event, demand])

df = pd.DataFrame(data, columns=['day', 'meal', 'item', 'weather', 'event', 'demand'])
df.to_csv('dataset.csv', index=False)
print(f"Successfully generated a dataset with {len(data)} records.")

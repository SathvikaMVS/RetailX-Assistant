#!/usr/bin/env python
# coding: utf-8

# In[1]:




# In[2]:


import pandas as pd
import json
import os

def read_file(file_name):
    _, extension = os.path.splitext(file_name)
    try:
        if extension.lower() == '.csv':
            df = pd.read_csv(file_name)
        elif extension.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_name)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
        df['column_name'] = df['column_name'].astype(str)
        print(f"Successfully read {file_name}. Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"First row: {df.iloc[0].to_dict()}")
        return df
    except Exception as e:
        print(f"Error reading {file_name}: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame if file can't be read

# Convert Timestamps to strings
def convert_timestamps(record):
    return {k: (v.isoformat() if isinstance(v, pd.Timestamp) else v) for k, v in record.items()}

# Read files
files = ['products_indian', 'stores_indian', 'customers_indian', 'orders_indian']
data = {}

for file in files:
    for ext in ['.xlsx', '.xls', '.csv']:
        file_name = f"{file}{ext}"
        if os.path.exists(file_name):
            df = read_file(file_name)
            if not df.empty:
                # Convert Timestamps before storing in data
                data[file] = [convert_timestamps(record) for record in df.to_dict('records')]
                break
    if file not in data:
        print(f"Couldn't read data for {file}")

# Create the main data structure
retailx_data = {
    "products": data.get('products_indian', []),
    "stores": data.get('stores_indian', []),
    "customers": data.get('customers_indian', []),
    "orders": data.get('orders_indian', [])
}

# Print the number of items in each category
for category, items in retailx_data.items():
    print(f"Number of {category}: {len(items)}")

# Convert the data to a JSON string with proper formatting
json_string = json.dumps(retailx_data, indent=2)

# Save the JSON data to a file
with open('retailx_data.json', 'w') as f:
    json.dump(retailx_data, f, indent=2)

print("JSON file 'retailx_data.json' has been created successfully.")

# To verify, let's read the file back and print the first product
with open('retailx_data.json', 'r') as f:
    loaded_data = json.load(f)

print("\nVerification - First products in the loaded data:")
print(json.dumps(loaded_data['products'][1], indent=2) if loaded_data['products'] else "No products found")


# In[3]:


import pandas as pd

# Function to read data from Excel files
def read_data(file_name):
    try:
        df = pd.read_excel(file_name)
        print(f"Successfully read {file_name}. Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Error reading {file_name}: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame if file can't be read

# Load data from Excel files
products_data = read_data('products_indian.xlsx')  # Replace with your actual file path
customers_data = read_data('customers_indian.xlsx')  # Replace with your actual file path
orders_data = read_data('orders_indian.xlsx')  # Replace with your actual file path
stores_data = read_data('stores_indian.xlsx')  # Replace with your actual file path

# Clean up column names
products_data.columns = products_data.columns.str.strip()  # Remove whitespace
customers_data.columns = customers_data.columns.str.strip()  # Remove whitespace
orders_data.columns = orders_data.columns.str.strip()  # Remove whitespace
stores_data.columns = stores_data.columns.str.strip()  # Remove whitespace

# Check and print column names for debugging
print("Columns in products_data:", products_data.columns.tolist())
print("Columns in customers_data:", customers_data.columns.tolist())
print("Columns in orders_data:", orders_data.columns.tolist())
print("Columns in stores_data:", stores_data.columns.tolist())

# Virtual Shopping Assistant Functionality
def find_product(preference):
    """Find products based on customer preference."""
    try:
        recommended = products_data[products_data['ProductName'].str.contains(preference, case=False)]
        return recommended.to_dict(orient='records') if not recommended.empty else "No products found."
    except KeyError:
        return "Column 'ProductName' not found in products data."

def check_product_availability(product_name):
    """Check if a product is available in stock."""
    try:
        product = products_data[products_data['ProductName'].str.contains(product_name, case=False)]
        if not product.empty:
            availability = product[['ProductName', 'Stock']].to_dict(orient='records')
            return availability
        return "Product not found."
    except KeyError:
        return "Column 'ProductName' not found in products data."

def track_order(order_id):
    """Simulate tracking an order."""
    order = orders_data[orders_data['OrderID'] == order_id]
    if not order.empty:
        return f"Tracking details for order ID {order_id}: {order.to_dict(orient='records')}"
    return "Order not found."

def personalized_promotions(customer_id):
    """Provide personalized promotions based on loyalty points."""
    customer = customers_data[customers_data['CustomerID'] == customer_id]
    if not customer.empty:
        # Assuming you have a 'Loyalty Points' column, replace with actual column if it exists
        points = customer.get('Loyalty Points', 0)  # Adjust if this column doesn't exist
        if points > 100:
            return "You have a 10% discount on your next purchase!"
    return "No promotions available."

def monitor_inventory():
    """Monitor inventory and check for low stock items."""
    low_stock = products_data[products_data['Stock'] < 5]
    return low_stock.to_dict(orient='records') if not low_stock.empty else "All products are sufficiently stocked."

# Main interaction loop
if __name__ == "__main__":
    while True:
        print("\nWelcome to RetailX Assistant!")
        print("1. Find a Product")
        print("2. Check Product Availability")
        print("3. Track an Order")
        print("4. Get Personalized Promotions")
        print("5. Monitor Inventory")
        print("6. Exit")
        
        choice = input("Please choose an option (1-6): ")
        
        if choice == '1':
            preference = input("Enter the product name or keyword: ")
            result = find_product(preference)
            print("Product Search Result:", result)
        
        elif choice == '2':
            product_name = input("Enter the product name: ")
            result = check_product_availability(product_name)
            print("Product Availability:", result)
        
        elif choice == '3':
            order_id = int(input("Enter the order ID: "))
            result = track_order(order_id)
            print(result)
        
        elif choice == '4':
            customer_id = int(input("Enter the customer ID: "))
            result = personalized_promotions(customer_id)
            print(result)
        
        elif choice == '5':
            result = monitor_inventory()
            print("Low Stock Items:", result)
        
        elif choice == '6':
            print("Exiting the RetailX Assistant. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please select a number between 1 and 6.")



# In[ ]:





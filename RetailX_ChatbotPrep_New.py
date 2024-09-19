import pandas as pd
import os
import streamlit as st

# Function to read files
def read_file(file_name):
    _, extension = os.path.splitext(file_name)
    try:
        if extension.lower() == '.csv':
            df = pd.read_csv(file_name)
        elif extension.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_name)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
        
        return df
    except Exception as e:
        st.error(f"Error reading {file_name}: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame if file can't be read

# Convert Timestamps to strings
def convert_timestamps(record):
    return {k: (v.isoformat() if isinstance(v, pd.Timestamp) else v) for k, v in record.items()}

# Load data from Excel files
def load_data():
    files = ['products_indian', 'stores_indian', 'customers_indian', 'orders_indian']
    data = {}

    for file in files:
        for ext in ['.xlsx', '.xls', '.csv']:
            file_name = f"{file}{ext}"
            if os.path.exists(file_name):
                df = read_file(file_name)
                if not df.empty:
                    data[file] = [convert_timestamps(record) for record in df.to_dict('records')]
                    break
    return {
        "products": data.get('products_indian', []),
        "stores": data.get('stores_indian', []),
        "customers": data.get('customers_indian', []),
        "orders": data.get('orders_indian', [])
    }

# Load the retail data
retailx_data = load_data()

# Function to search for products
def find_product(preference):
    products_data = pd.DataFrame(retailx_data['products'])
    # Display the actual column names for debugging
    st.write("Product Data Columns:", products_data.columns)
    filtered_products = products_data[products_data['ProductName'].str.contains(preference, case=False, na=False)]
    return filtered_products.to_dict(orient='records') if not filtered_products.empty else "No products found."

# Function to check product availability
def check_product_availability(product_name):
    products_data = pd.DataFrame(retailx_data['products'])
    available_products = products_data[products_data['ProductName'].str.contains(product_name, case=False, na=False)]
    return available_products[['ProductName', 'Stock']].to_dict(orient='records') if not available_products.empty else "Product not available."

# Function to track an order by its ID
def track_order(order_id):
    orders_data = pd.DataFrame(retailx_data['orders'])
    order = orders_data[orders_data['Order ID'] == order_id]
    return order.to_dict(orient='records') if not order.empty else "Order not found."

# Function to generate personalized promotions
def personalized_promotions(customer_id):
    customers_data = pd.DataFrame(retailx_data['customers'])
    customer = customers_data[customers_data['Customer ID'] == customer_id]
    if not customer.empty:
        return f"Special promotions for customer {customer_id}: 10% off on your next purchase!"
    return "Customer not found."

# Function to monitor inventory and detect low stock
def monitor_inventory():
    products_data = pd.DataFrame(retailx_data['products'])
    low_stock = products_data[products_data['Stock'] < 5]
    return low_stock.to_dict(orient='records') if not low_stock.empty else "All products are sufficiently stocked."

# Streamlit app layout
st.title("RetailX Assistant")

# User selection
option = st.selectbox("Select an option:", 
                       ["Find a Product", 
                        "Check Product Availability", 
                        "Track an Order", 
                        "Get Personalized Promotions", 
                        "Monitor Inventory", 
                        "Exit"])

# Find a Product
if option == "Find a Product":
    preference = st.text_input("Enter the product name or keyword:")
    if st.button("Search"):
        result = find_product(preference)
        st.write("Product Search Result:", result)

# Check Product Availability
elif option == "Check Product Availability":
    product_name = st.text_input("Enter the product name:")
    if st.button("Check"):
        result = check_product_availability(product_name)
        st.write("Product Availability:", result)

# Track an Order
elif option == "Track an Order":
    order_id = st.number_input("Enter the order ID:", min_value=1)
    if st.button("Track"):
        result = track_order(order_id)
        st.write(result)

# Get Personalized Promotions
elif option == "Get Personalized Promotions":
    customer_id = st.number_input("Enter the customer ID:", min_value=1)
    if st.button("Get Promotions"):
        result = personalized_promotions(customer_id)
        st.write(result)

# Monitor Inventory
elif option == "Monitor Inventory":
    if st.button("Check Inventory"):
        result = monitor_inventory()
        st.write("Low Stock Items:", result)

# Exit option
elif option == "Exit":
    st.write("Thank you for using RetailX Assistant!")

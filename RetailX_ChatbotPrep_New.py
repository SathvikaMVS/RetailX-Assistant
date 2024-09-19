import pandas as pd
import os
import re
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
        
        st.write(f"Successfully read {file_name}. Shape: {df.shape}")
        return df
    except Exception as e:
        st.write(f"Error reading {file_name}: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame if file can't be read

# Read files and load data
def load_data():
    files = ['products_indian', 'stores_indian', 'customers_indian', 'orders_indian']
    data = {}

    for file in files:
        for ext in ['.xlsx', '.xls', '.csv']:
            file_name = f"{file}{ext}"
            if os.path.exists(file_name):
                df = read_file(file_name)
                if not df.empty:
                    data[file] = df
                    break
        if file not in data:
            st.write(f"Couldn't read data for {file}")

    # Create the main data structure
    retailx_data = {
        "products": data.get('products_indian', pd.DataFrame()),
        "stores": data.get('stores_indian', pd.DataFrame()),
        "customers": data.get('customers_indian', pd.DataFrame()),
        "orders": data.get('orders_indian', pd.DataFrame())
    }

    # Ensure Price and Stock are treated as numeric
    if not retailx_data['products'].empty:
        retailx_data['products']['Price'] = pd.to_numeric(retailx_data['products']['Price'], errors='coerce')
        retailx_data['products']['Stock'] = pd.to_numeric(retailx_data['products']['Stock'], errors='coerce')

    return retailx_data

# Helper function for natural language processing
def clean_input(user_input):
    return re.sub(r'\s+', ' ', user_input.strip().lower())

# Function to process user queries
def process_query(query, retailx_data):
    query = clean_input(query)

    if "how many stores are there in" in query:
        state = re.search(r"how many stores are there in (.*)", query)
        if state:
            return count_stores_in_state(state.group(1), retailx_data)

    elif "looking for" in query:
        return handle_product_search(query, retailx_data)

    elif "stock is left for" in query:
        product_name = re.search(r"stock is left for (.*)", query)
        if product_name:
            return check_product_availability(product_name.group(1), retailx_data)

    elif "branch in" in query:
        location = re.search(r"branch in (.*)", query)
        if location:
            return check_branch_availability(location.group(1), retailx_data)

    elif "didn't receive my order" in query:
        return ask_for_order_details(retailx_data)

    elif "last order date" in query:
        name = re.search(r"my name is (.*)", query)
        if name:
            return get_last_order_date(name.group(1), retailx_data)

    return "I'm sorry, I didn't understand that. Could you please rephrase?"

# Count the number of stores in a state
def count_stores_in_state(state, retailx_data):
    stores_data = retailx_data['stores']
    if 'State' in stores_data.columns:
        store_count = stores_data[stores_data['State'].str.contains(state, case=False, na=False)]
        return f"We have {len(store_count)} stores in total in {state}."
    return "State information is not available in store data."

# Handle product search queries
def handle_product_search(query, retailx_data):
    preference = re.search(r"looking for (.*)", query)
    if preference:
        budget = st.text_input("Can you please specify your budget? (e.g., 20000 to 50000)")
        if budget:
            return filter_products_by_budget(preference.group(1), budget, retailx_data)

def filter_products_by_budget(product, budget, retailx_data):
    try:
        low, high = map(int, budget.split('to'))
        filtered_products = retailx_data['products']
        available_products = filtered_products[
            (filtered_products['ProductName'].str.contains(product, case=False, na=False)) &
            (filtered_products['Price'] >= low) &
            (filtered_products['Price'] <= high)
        ]
        if not available_products.empty:
            return "\n".join([f"Product: {row['ProductName']}, Price: {row['Price']}" for index, row in available_products.iterrows()])
        return "No products found within that budget."
    except ValueError:
        return "Invalid budget format. Please use 'low to high'."

# Check stock availability for a product
def check_product_availability(product_name, retailx_data):
    products_data = retailx_data['products']
    if 'ProductName' in products_data.columns and 'Stock' in products_data.columns:
        available_products = products_data[products_data['ProductName'].str.contains(product_name, case=False, na=False)]
        if not available_products.empty:
            stock_info = "\n".join([f"Product: {row['ProductName']}, Stock: {row['Stock']}" for index, row in available_products.iterrows()])
            return f"Current stock:\n{stock_info}"
        return "Product not available."
    return "Stock information is not available for products."

# Check branch availability in a location
def check_branch_availability(location, retailx_data):
    stores_data = retailx_data['stores']
    if 'City' in stores_data.columns:
        branches = stores_data[stores_data['City'].str.contains(location, case=False, na=False)]
        if not branches.empty:
            branch_info = "\n".join([f"Branch: {row.get('BranchName', 'Unknown')}, Address: {row.get('Address', 'Unknown')}" for index, row in branches.iterrows()])
            return f"Branches in {location}:\n{branch_info}"
        return f"No branches found in {location}."
    return "Branch information is not available in store data."

# Ask for order details
def ask_for_order_details(retailx_data):
    customer_id = st.text_input("Please tell me your customer ID.")
    product_name = st.text_input("Please tell me the product name (or a part of it) you ordered.")
    if customer_id and product_name:
        return track_order(customer_id, product_name, retailx_data)

# Track an order based on customer ID and product name
def track_order(customer_id, product_name, retailx_data):
    orders_data = retailx_data['orders']
    if 'CustomerID' in orders_data.columns and 'ProductID' in orders_data.columns:
        order_info = orders_data[orders_data['CustomerID'] == int(customer_id)]
        if not order_info.empty:
            products_data = retailx_data['products']
            if 'ProductID' in products_data.columns and 'Status' in orders_data.columns:
                matching_products = order_info[order_info['ProductID'].isin(products_data['ProductID'])]
                if not matching_products.empty:
                    status = matching_products.iloc[0]['Status']  # Get the status of the first matching product
                    return f"Status: {status}. Please wait for its delivery."
    return "Order details not found."

# Get last order date for a customer
def get_last_order_date(customer_name, retailx_data):
    customers_data = retailx_data['customers']
    if 'Name' in customers_data.columns and 'LastOrderDate' in customers_data.columns:
        customer_info = customers_data[customers_data['Name'].str.contains(customer_name, case=False, na=False)]
        
        if not customer_info.empty:
            last_order_date = customer_info['LastOrderDate'].values[0]
            return f"{customer_name}, your last order date is {last_order_date}."
        
    return "Customer not found."

# Main Streamlit App
def main():
    st.title("RetailX Assistant")
    st.write("Ask me anything about your retail needs.")
    
    # Load the data
    retailx_data = load_data()

    # User input query
    query = st.text_input("You: ")

    if query:
        response = process_query(query, retailx_data)
        st.write

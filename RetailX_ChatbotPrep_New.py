import streamlit as st

st.title("RetailX Assistant")

# Load the data at the start
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

retailx_data = {
    "products": data.get('products_indian', []),
    "stores": data.get('stores_indian', []),
    "customers": data.get('customers_indian', []),
    "orders": data.get('orders_indian', [])
}

# Streamlit app functionality
option = st.selectbox("Select an option:", 
                       ["Find a Product", 
                        "Check Product Availability", 
                        "Track an Order", 
                        "Get Personalized Promotions", 
                        "Monitor Inventory", 
                        "Exit"])

if option == "Find a Product":
    preference = st.text_input("Enter the product name or keyword:")
    if st.button("Search"):
        result = find_product(preference)
        st.write("Product Search Result:", result)

elif option == "Check Product Availability":
    product_name = st.text_input("Enter the product name:")
    if st.button("Check"):
        result = check_product_availability(product_name)
        st.write("Product Availability:", result)

elif option == "Track an Order":
    order_id = st.number_input("Enter the order ID:", min_value=1)
    if st.button("Track"):
        result = track_order(order_id)
        st.write(result)

elif option == "Get Personalized Promotions":
    customer_id = st.number_input("Enter the customer ID:", min_value=1)
    if st.button("Get Promotions"):
        result = personalized_promotions(customer_id)
        st.write(result)

elif option == "Monitor Inventory":
    if st.button("Check Inventory"):
        result = monitor_inventory()
        st.write("Low Stock Items:", result)

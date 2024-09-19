import streamlit as st
import pandas as pd
import json
import os
import subprocess
import sys

# Check if nltk is installed, and if not, install it.
try:
    import nltk
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
    import nltk

# Proceed with the rest of the code.
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

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
        
        print(f"Successfully read {file_name}. Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Error reading {file_name}: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame if file can't be read

# Convert Timestamps to strings
def convert_timestamps(record):
    return {k: (v.isoformat() if isinstance(v, pd.Timestamp) else v) for k, v in record.items()}

# Read files and load data (no 'data/' folder, files expected at root level)
@st.cache_data
def load_data():
    files = ['products_indian', 'stores_indian', 'customers_indian', 'orders_indian']
    data = {}

    for file in files:
        for ext in ['.xlsx', '.xls', '.csv']:
            file_name = f"{file}{ext}"  # No 'data/' prefix, expect files in root
            if os.path.exists(file_name):
                df = read_file(file_name)
                if not df.empty:
                    data[file] = [convert_timestamps(record) for record in df.to_dict('records')]
                    break
        if file not in data:
            print(f"Couldn't read data for {file}")

    # Create the main data structure
    return {
        "products": data.get('products_indian', []),
        "stores": data.get('stores_indian', []),
        "customers": data.get('customers_indian', []),
        "orders": data.get('orders_indian', [])
    }

retailx_data = load_data()

# Function to search for products
def find_product(preference):
    products_data = pd.DataFrame(retailx_data['products'])
    filtered_products = products_data[products_data['Product Name'].str.contains(preference, case=False, na=False)]
    return filtered_products.to_dict(orient='records') if not filtered_products.empty else "No products found."

# Function to check product availability
def check_product_availability(product_name):
    products_data = pd.DataFrame(retailx_data['products'])
    available_products = products_data[products_data['Product Name'].str.contains(product_name, case=False, na=False)]
    return available_products[['Product Name', 'Stock']].to_dict(orient='records') if not available_products.empty else "Product not available."

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

class RetailXChatbot:
    def __init__(self):
        self.data = retailx_data
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def preprocess(self, text):
        tokens = word_tokenize(text.lower())
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        return tokens

    def get_intent(self, tokens):
        intents = {
            'product_search': ['find', 'search', 'looking', 'product'],
            'check_availability': ['available', 'stock', 'inventory'],
            'order_status': ['track', 'order', 'status'],
            'promotions': ['promotion', 'discount', 'offer'],
            'inventory': ['monitor', 'low', 'stock']
        }
        
        for intent, keywords in intents.items():
            if any(keyword in tokens for keyword in keywords):
                return intent
        return 'general_inquiry'

    def respond(self, user_input):
        tokens = self.preprocess(user_input)
        intent = self.get_intent(tokens)
        
        if intent == 'product_search':
            product = ' '.join(tokens)
            return f"Here are the products matching '{product}':\n{find_product(product)}"
        elif intent == 'check_availability':
            product = ' '.join(tokens)
            return f"Availability for '{product}':\n{check_product_availability(product)}"
        elif intent == 'order_status':
            order_id = next((token for token in tokens if token.isdigit()), None)
            if order_id:
                return f"Order status:\n{track_order(int(order_id))}"
            else:
                return "Please provide an order ID to track."
        elif intent == 'promotions':
            customer_id = next((token for token in tokens if token.isdigit()), None)
            if customer_id:
                return personalized_promotions(int(customer_id))
            else:
                return "Please provide a customer ID for personalized promotions."
        elif intent == 'inventory':
            return f"Current inventory status:\n{monitor_inventory()}"
        else:
            return "I'm sorry, I didn't understand that. Can you please rephrase your question?"

# Streamlit app
st.title("RetailX Assistant")

chatbot = RetailXChatbot()

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What can I help you with?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = chatbot.respond(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# Instructions for the user
st.sidebar.title("How to use RetailX Assistant")
st.sidebar.markdown("""
1. Search for products: "Find me smartphones"
2. Check availability: "Is iPhone 12 available?"
3. Track order: "Track my order 12345"
4. Get promotions: "Any promotions for customer 1001?"
5. Check inventory: "Show low stock items"
""")

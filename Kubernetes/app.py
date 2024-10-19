# -*- coding: utf-8 -*-

import streamlit as st
import requests
import json
import base64
from kubernetes import client, config

# Charger la configuration Kubernetes (par exemple, fichier kubeconfig)
config.load_kube_config()

# Créer une instance de l'API Kubernetes
v1 = client.CoreV1Api()

# Nom de votre Secret Kubernetes
secret_name = 'api-secret'
# Namespace de votre Secret Kubernetes
namespace = 'customer'

# Récupérer le Secret depuis Kubernetes
secret = v1.read_namespaced_secret(name=secret_name, namespace=namespace)

# Décoder et récupérer la clé API
api_key_encoded = secret.data['api-key']
api_key = base64.b64decode(api_key_encoded).decode('utf-8')
api_key = base64.b64decode(api_key).decode('utf-8')

# Streamlit app title
st.title("Customer Prediction App")

# Sidebar for manual input
st.sidebar.header("Manual Input Section")

# Input fields for the payload data
server_ts = st.sidebar.text_input("Server Timestamp (e.g., 2014-03-01T03:39:23.099Z)")
client_addr = st.sidebar.text_input("Client Address (e.g., 50.204.38.160)")
visitor_id = st.sidebar.text_input("Visitor ID (e.g., 45467421ac4f218)")
session_id = st.sidebar.text_input("Session ID (e.g., 463fe4c146ea482)")
location = st.sidebar.text_input("Location (e.g., http://dataiku.com/blog/2014/01/14/winning-kaggle.html)")
user_agent = st.sidebar.text_input("User Agent (e.g., Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36)")
br_width = st.sidebar.number_input("Browser Width", min_value=0)
br_height = st.sidebar.number_input("Browser Height", min_value=0)
sc_width = st.sidebar.number_input("Screen Width", min_value=0)
sc_height = st.sidebar.number_input("Screen Height", min_value=0)
br_lang = st.sidebar.text_input("Browser Language (e.g., en-US)")
tz_off = st.sidebar.number_input("Timezone Offset", value=0)
customer = st.sidebar.number_input("Customer", min_value=0)

# Button to trigger the API call
if st.sidebar.button("Run Prediction"):
    # Construct payload data
    payload_data = {
        "features": {
            "server_ts": server_ts,
            "client_addr": client_addr,
            "visitor_id": visitor_id,
            "session_id": session_id,
            "location": location,
            "user_agent": user_agent,
            "type": "page",
            "br_width": br_width,
            "br_height": br_height,
            "sc_width": sc_width,
            "sc_height": sc_height,
            "br_lang": br_lang,
            "tz_off": tz_off,
            "customer": customer
        }
    }

    # API endpoint
    api_url = "https://api-eaa79d81-1696b071-dku.eu-west-3.app.dataiku.io/public/api/v1/website/predict_customer/predict"


    # Make API call
    response = requests.post(api_url, json=payload_data, auth=(api_key, ''))

    # Display API response
    st.subheader("API Response:")
    st.json(response.json())

else:
    api_url = "https://api-eaa79d81-1696b071-dku.eu-west-3.app.dataiku.io/public/api/v1/website/predict_customer/predict"

    payload_data = {
        "features": {
            "server_ts": "2014-03-01T11:11:47.029Z",
            "client_addr": "109.25.210.20",
            "visitor_id": "22eb1631f385f1e",
            "session_id": "1947c3f17a3087b",
            "location": "http://www.dataiku.com/products/",
            "referer": "dataiku",
            "user_agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36",
            "type": "page",
            "br_width": 798,
            "br_height": 558,
            "sc_width": 1366,
            "sc_height": 768,
            "br_lang": "fr",
            "tz_off": -60,
            "customer": 0
        }
    }

    # Convert payload data to JSON format
    try:
        payload_json = json.dumps(payload_data)
    except Exception as e:
        st.write(f"Error converting payload to JSON: {str(e)}")
        payload_json = "{}"  # Provide a default empty JSON object

    # Make the API call
    try:
        response = requests.post(api_url, json=payload_data, auth=(api_key, ''))
        if response.status_code == 200:
            prediction = response.json()
            st.write("Prediction:", prediction)
        else:
            st.write(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.write(f"An error occurred: {str(e)}")


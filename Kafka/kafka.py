# -*- coding: utf-8 -*-

import streamlit as st
import requests
import json
import base64
from kubernetes import client, config
from confluent_kafka import Producer
import requests
import json

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

# Kafka cluster configuration
bootstrap_servers = 'pkc-60py3.europe-west9.gcp.confluent.cloud:9092'
group_id = 'lkc-v6w6jp'

# Producer configuration
producer_conf = {
    'bootstrap.servers': bootstrap_servers,
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': 'FYYTFPBYZSMWGGHD',
    'sasl.password': 'pNJ4Ug7Zv/uy0hwRWiLDov3VGdHNElAJBcdAe4sisd8sA5y8XAO/SGpooO36/fmj'
}

# Kafka topic
output_topic = 'customer'

# Create Kafka Producer
producer = Producer(producer_conf)

# API URL for fetching data
data_api_url = 'https://api-56ce4d5f-779f448b-dku.eu-west-3.app.dataiku.io/public/api/v1/generate_rows/generate-rows/run'

# Make HTTP request to fetch data
response_data = requests.get(data_api_url)
if response_data.status_code == 200:
    # Convert the JSON response to a Python dictionary
    data = response_data.json()

    # Extract relevant fields from the data
    features_data = {
        "server_ts": data['response']['server_ts'],
        "client_addr": data['response']['client_addr'],
        "visitor_id": data['response']['visitor_id'],
        "session_id": data['response']['session_id'],
        "location": data['response']['location'],
        "user_agent": data['response']['user_agent'],
        "type": data['response']['type'],
        "br_width": int(data['response']['br_width']),
        "br_height": int(data['response']['br_height']),
        "sc_width": int(data['response']['sc_width']),
        "sc_height": int(data['response']['sc_height']),
        "br_lang": data['response']['br_lang'],
        "tz_off": int(data['response']['tz_off']),
        "customer": ''
    }

    # Create payload data for scoring API
    payload_data = {"features": features_data}

    # Convert the payload data to a JSON string
    payload_json = json.dumps(payload_data)

    # API URL for scoring
    scoring_api_url = 'https://api-eaa79d81-1696b071-dku.eu-west-3.app.dataiku.io/public/api/v1/website/predict_customer/predict'

    response_scoring = requests.post(scoring_api_url, json=payload_data, auth=(api_key, ''))

    if response_scoring.status_code == 200:
        # Extract the prediction value from the scoring API response
        prediction_value = response_scoring.json()['result']['prediction']

        # Create a message with both features and prediction
        combined_message = {
            "features": features_data,
            "prediction": prediction_value
        }

        # Convert the combined message to a JSON string
        combined_message_json = json.dumps(combined_message)

        # Produce the combined message to the Kafka topic
        producer.produce(output_topic, value=combined_message_json)

        # Flush the producer to ensure the message is sent
        producer.flush()

        print("Prediction successful. Combined message:", combined_message)
    else:
        print(f"Failed to score data. Status code: {response_scoring.status_code}")
        print("Response content:", response_scoring.text)
else:
    print(f"Failed to fetch data from the API. Status code: {response_data.status_code}")

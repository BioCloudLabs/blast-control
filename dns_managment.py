import requests

def create_record(api_token, record_name, record_content, record_type='A', ttl=1):
    url = "https://api.cloudflare.com/client/v4/zones/de4b843d0fb20d24d1203b01df3237f1/dns_records"
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'type': record_type,
        'name': record_name,
        'content': record_content,
        'ttl': ttl,
        'proxied': False  # Adjust as needed
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("DNS record created successfully.")
    else:
        print(f"Failed to create DNS record. Status code: {response.status_code}")
        print(response.text)


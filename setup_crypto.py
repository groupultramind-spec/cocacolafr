from cryptography.fernet import Fernet
import json

# Generate key
key = Fernet.generate_key()
with open('secret.key', 'wb') as key_file:
    key_file.write(key)

f = Fernet(key)

# The sensitive data
data = {
    "token": "8822322073:AAGFjh2SjGNis8ipyzXCS2BhrCB0gKU0IXQ",
    "channel_id": "-1004403791517"
}

# Encrypt data
encrypted_data = f.encrypt(json.dumps(data).encode('utf-8'))

# Save to file
with open('secrets.enc', 'wb') as enc_file:
    enc_file.write(encrypted_data)

print("Data encrypted and saved to secrets.enc")

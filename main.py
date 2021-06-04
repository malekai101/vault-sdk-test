import hvac
import sys
import os
import base64
import json


def get_secret(client):
    try:
        # use the token to get the secret
        mount_point = 'secret'
        secret_path = 'data/testdata/universe'

        read_secret_result = client.secrets.kv.v1.read_secret(
            path=secret_path,
            mount_point=mount_point,
        )
        print(f"The answer is {read_secret_result['data']['data']['theanswer']}")
        return read_secret_result['data']['data']['theanswer']
    except:
        print("Failed pulling secret")
        raise


def encrypt_data(client, cleartext):
    # encode the clear text
    encoded_cleartext = base64.b64encode(cleartext.encode('utf-8')).decode('utf-8')
    encrypt_data_response = client.secrets.transit.encrypt_data(
        name='orders',
        plaintext=encoded_cleartext
    )
    return encrypt_data_response['data']['ciphertext']


def decrypt_data(client, ciphertext):
    decrypt_data_response = client.secrets.transit.decrypt_data(
        name='orders',
        ciphertext=ciphertext,
    )
    encoded_cleartext = decrypt_data_response['data']['plaintext']
    return base64.b64decode(encoded_cleartext.encode('utf-8')).decode('utf-8')


# limited permissions.  hidden in env variables, typically injected 
role_id = os.environ.get("PYROLEID")
secret_id = os.environ.get("PYVAULTSECRET")

client = hvac.Client(url="http://localhost:8200")
try:
    # get the token for authentication
    client.auth_approle(role_id, secret_id)
except:
    # failed to get a token
    print("Error on token auth")
    sys.exit(1)

if sys.argv[1].upper() == "DECRYPT":
    doc = json.loads(sys.argv[2])
    decrypted = decrypt_data(client, doc["SSN"])
    print(decrypted)
elif sys.argv[1].upper() == "ENCRYPT":
    record = {"Name": sys.argv[2], "Job": sys.argv[3], "SSN": encrypt_data(client, sys.argv[4])}
    print(json.dumps(record))
else:
    print(f"Unknown argument {sys.argv[1]}")


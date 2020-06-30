import hvac
import sys
import os

# limited permissions.  hidden in env variables, typically injected 
role_id = os.environ.get("ROLEID")
secret_id = os.environ.get("VAULTSECRET")

client = hvac.Client(url="http://localhost:8200")
try:
    # get the token for authentication
    client.auth_approle(role_id, secret_id)
except:
    # failed to get a token
    print("Error on token auth")
    sys.exit(1)

try:
    # use the token to get the secret
    mount_point = 'secret'
    secret_path = 'data/testdata/universe'

    read_secret_result = client.secrets.kv.v1.read_secret(
        path=secret_path,
        mount_point=mount_point,
    )
    print(f"The answer is {read_secret_result['data']['data']['theanswer']}")
except:
    print("Failed pulling secret")
    sys.exit(2)
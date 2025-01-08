import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

keyVaultName = "cloud-learning-keys"
KVUri = f"https://{keyVaultName}.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

settings = {
    'host': client.get_secret("cosmos-endpoint"),
    'master_key': client.get_secret("cosmos-readwrite-key"),
    'database_id': os.environ.get('COSMOS_DATABASE', 'Movies'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'Movies'),
    'storage_account_url': os.environ.get('STORAGE_ACCOUNT_URL', 'https://simonl2cimages.blob.core.windows.net'),
}
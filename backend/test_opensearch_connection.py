from app.storage.opensearch_client import client

info = client.info()

print("=" * 80)
print("OPENSEARCH CONNECTION")
print("=" * 80)

print("Cluster :", info["cluster_name"])
print("Version :", info["version"]["number"])

print("\nConnection Successful!")

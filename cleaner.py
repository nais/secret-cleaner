from kubernetes import client, config
import pickle
import adal
import re
from collections import defaultdict

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
in_use_secrets = set()
secrets_to_delete = defaultdict(set)
namespaces_to_clean = ['default', 'u1', 'u2', 'u3', 'u7', 'u88', 'u89', 't0', 't1', 't10', 't13', 't2', 't3', 't4', 't5', 't6', 'q', 'q0', 'q1', 'q10', 'q11', 'q2', 'q4', 'q5', 'q6', 'qx']
token_pattern = re.compile('.*-token-[a-z0-9]{5}$')

print('listing secrets')
secrets = v1.list_secret_for_all_namespaces(watch=False, field_selector="type=kubernetes.io/service-account-token").items
print('fetched {} secrets'.format(len(secrets)))

print('listing pods')
pods = v1.list_pod_for_all_namespaces(watch=False).items
print('fetched {} pods'.format(len(pods)))

print('massaging pods')
for i in pods:
    for v in i.spec.volumes:
        if v.secret:
            in_use_secrets.add(v.secret.secret_name)

print('massaging secrets')
for secret in secrets:
    if secret.metadata.namespace in namespaces_to_clean and not secret.metadata.name in in_use_secrets:
        if token_pattern.match(secret.metadata.name):
            secrets_to_delete[secret.metadata.namespace].add(secret.metadata.name)

print('deleting secrets from {} namespaces'.format(len(secrets_to_delete)))
for namespace, secrets in secrets_to_delete.items():
    print('deleting {} secrets from namespace {}'.format(len(secrets), namespace))
    for name in secrets:
        print("deleting {} from {}".format(name, namespace))
        ret = v1.delete_namespaced_secret(name, namespace)
        print(ret)

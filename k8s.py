from pprint import pprint

from kubernetes import client, config

import json
from kubernetes import client, config, utils
from kubernetes.client import ApiException


class KubernetesInteraction:
    def __init__(self, token=None, host_url=None):
        _config = client.api_client.Configuration(
            host=host_url,
        )
        _config.verify_ssl = False
        _config.api_key = {"authorization": "Bearer " + token}
        self.api_client = client.ApiClient(_config)
        self.core_client = client.CoreV1Api(self.api_client)

    def list_pods(self):
        api_instance = client.CoreV1Api(self.api_client)
        pods = api_instance.list_pod_for_all_namespaces(watch=False)

        pods_list = []
        for item in pods.items:
            pods_list.append(item.metadata.name)

        return json.dumps(pods_list)

    def apply_resource(self, file):
        try:
            utils.create_from_yaml(self.api_client, file, verbose=True)
        except Exception as ex:
            print(ex)

    def start_nodejs_service(self):

        namespace = 'default'

        manifest = {
            "kind": "Pod",
            "apiVersion": "v1",
            "metadata": {
                "name": "vpn-proxy-service",
                "labels": {
                    "app": "proxy-service"
                }
            },
            "spec": {
                "containers": [
                    {
                        "name": "test-openvpn",
                        "image": "ilteoood/docker-surfshark",
                        "ports": [
                            {
                                "port": 3128,
                                "containerPort": 3128
                            }],
                        "dns": ['surfshark.com', '8.8.8.8'],
                        "cap_add": ['NET_ADMIN'],
                        "devices": ['/dev/net/tun'],
                        "environment": vpn_config
                    },
                    {
                        "name": "test-squid",
                        "image": "sameersbn/squid:3.5.27-2",
                        "network_mode": "container:test-openvpn",
                    }
                ],
                "ports": [{
                    "port": 3128,
                    "targetPort": 3128
                }]
            },
        }

        try:
            api_response = self.core_client.create_namespaced_service(namespace, manifest, pretty='true')
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_endpoints: %s\n" % e)


# Configs can be set in Configuration class directly or using helper utility
# config.load_kube_config("./kube/config")
# K8S_HOST = "https://172.18.20.60:16443"
# TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6Il85bjZzcFluV1ktVUlMeTNaSFF3WjBITXhNRGdQQnY4RVI3bzc4U0loYWMifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi10b2tlbi1oeDR6OCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJhZG1pbiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjdmYzZjNDAwLTljNTEtNGExNC1iNWRmLWVlNDdjNjAyMzM3MCIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlLXN5c3RlbTphZG1pbiJ9.ESgBSZ2PwQDPCRh6oJwILPAqBOC6h3MZ0bGoGQabaI60i_Rp07yagHGU8Szj1BaLsiObqaQe2XwsrfMiX0ew9y3EitJ0saUEyygdssYdineR5uzSCVUCOXsHRglcyczrxxqJxyYD3_g7FzxPzBxW_K7e4NicN5vZK3bU65EQIVLSuTJaC25vU33D7hLhi9huDO8F50xW9n4lmiHFPI6TkfNtb_6-w5-2AwyBWj9oaGW0EIjrI4Jn2vuzoJlUpfFtQlHgmWBb3c2yz1MtHN7pn7c-Ggp3FHHm3jd_s12Lkl_6A1Z3KrBFqSLGa3m3OPreDDP3KotgAJ54ERxXygq95w"
K8S_HOST = "https://10.10.10.158:8001"
TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6InJaVmNYZGlxQTM0ZVFReGN0NGo3NWtydFp6T09DdGdLWEVnSWRrZTgtRkEifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4iLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImIzYTcyNTQ5LTk5ZDEtNDI1OC1iYjQ1LTc3MjA5NDg1YmM2ZiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.prczYAG4PZip06h4AQuCoWRBs476KK6WUygwWzr_-Lc4dh1j0xU7J_mbC-7jtkP3crBs5Oy1mgOTSCrPT5_FfwMLh0hRkMMmvtlbBwkweuk0yn3iH2kO6ZT-4_mDojt6zsxYjpHjQUXCfhnBcTjZf9ZNOeDLRnC9_XCDh1oEmI_SgIh1EvXJP6nmt7vt5MyK07rfiDHXTZ4chcfiPjRt_ZwpXTJhncHofGZMuzH51pul_BWdj9gA-cVEfQeMloKTBkHtlIazBZ_DotQkJUjJ2dWyamMBbPzYmKwBnGOSP5dCLVO-D6gRsYEbLqL3twPhnmxWImY4cdJVwdpfWSpAIg"

vpn_config = {
    "SURFSHARK_USER": "BMHeBFJg2EgJg9ECpPrreLah",
    "SURFSHARK_PASSWORD": "7sM2GJTHqsVVTWFCxJUGGrRj",
    "SURFSHARK_COUNTRY": "us",
    "SURFSHARK_CITY": 'nyc',
    "CONNECTION_TYPE": 'tcp',
}

if __name__ == '__main__':
    interaction = KubernetesInteraction(TOKEN, K8S_HOST)
    interaction.start_nodejs_service()
    podsList = interaction.list_pods()
    print(podsList)

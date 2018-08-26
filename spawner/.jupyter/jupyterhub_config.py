import os

import json
import requests

# Override image details with that of the front end.

spawner_name = os.environ.get('SPAWNER_NAME')

service_account_name = '%s-hub' %  spawner_name
service_account_path = '/var/run/secrets/kubernetes.io/serviceaccount'

with open(os.path.join(service_account_path, 'namespace')) as fp:
    namespace = fp.read().strip()

c.KubeSpawner.hub_connect_ip = spawner_name

c.KubeSpawner.singleuser_image_spec = 'docker-registry.default.svc:5000/%s/%s-app-img' % (namespace, spawner_name)

c.KubeSpawner.cmd = ['/opt/butterfly/bin/start-butterfly.sh']

c.KubeSpawner.pod_name_template = '%s-user-{username}' % (
        c.KubeSpawner.hub_connect_ip)

c.KubeSpawner.common_labels = { 'app': spawner_name }

c.Spawner.mem_limit = convert_size_to_bytes('256Mi')

# Work out the public server address for the OpenShift REST API. Don't
# know how to get this via the REST API client so do a raw request to
# get it. Make sure request is done in a session so connection is closed
# and later calls against REST API don't attempt to reuse it. This is
# just to avoid potential for any problems with connection reuse.

server_url = 'https://openshift.default.svc.cluster.local'
api_url = '%s/oapi' % server_url

with requests.Session() as session:
    response = session.get(api_url, verify=False)
    data = json.loads(response.content.decode('UTF-8'))
    address = data['serverAddressByClientCIDRs'][0]['serverAddress']

# Enable the OpenShift authenticator. The OPENSHIFT_URL environment
# variable must be set before importing the authenticator as it only
# reads it when module is first imported.

os.environ['OPENSHIFT_URL'] = 'https://%s' % address

from oauthenticator.openshift import OpenShiftOAuthenticator
c.JupyterHub.authenticator_class = OpenShiftOAuthenticator

# Setup authenticator configuration using details from environment.

client_id = 'system:serviceaccount:%s:%s' % (namespace, service_account_name)

c.OpenShiftOAuthenticator.client_id = client_id

with open(os.path.join(service_account_path, 'token')) as fp:
    client_secret = fp.read().strip()

c.OpenShiftOAuthenticator.client_secret = client_secret

# Work out hostname for the exposed route of the JupyterHub server. This
# is tricky as we need to use the REST API to query it.

import openshift.client
import openshift.config

openshift.config.load_incluster_config()

api_client = openshift.client.ApiClient()
oapi_client = openshift.client.OapiApi(api_client)

route_list = oapi_client.list_namespaced_route(namespace)

host = None

for route in route_list.items:
    if route.metadata.name == spawner_name:
        host = route.spec.host

if not host:
    raise RuntimeError('Cannot calculate external host name for JupyterHub.')

c.OpenShiftOAuthenticator.oauth_callback_url = 'https://%s/hub/oauth_callback' % host

# Override URL prefix for application and copy files to volume.

c.KubeSpawner.user_storage_pvc_ensure = True

c.KubeSpawner.pvc_name_template = '%s-user-{username}' % spawner_name

c.KubeSpawner.user_storage_capacity = '%s' % os.environ['WORKSPACE_VOLUME_SIZE']

c.KubeSpawner.user_storage_access_modes = ['ReadWriteOnce']

c.KubeSpawner.volumes = [
    {
        'name': 'data',
        'persistentVolumeClaim': {
            'claimName': c.KubeSpawner.pvc_name_template
        }
    }
]

c.KubeSpawner.volume_mounts = [
    {
        'name': 'data',
        'mountPath': '/opt/app-root',
        'subPath': 'workspace'
    }
]

c.KubeSpawner.init_containers = [
    {
        'name': 'setup-volume',
        'image': 'docker-registry.default.svc:5000/%s/%s-app-img' % (namespace, spawner_name),
        'command': [
            'setup-volume.sh',
            '/opt/app-root',
            '/mnt/workspace'
        ],
        'resources': {
            'limits': {
                'memory': '256Mi'
            }
        },
        'volumeMounts': [
            {
                'name': 'data',
                'mountPath': '/mnt'
            }
        ]
    }
]

def modify_pod_hook(spawner, pod):
    pod.spec.containers[0].env.append(dict(name='URI_ROOT_PATH',
            value='/user/%s/' % spawner.user.name))

    #pod.spec.containers[0].volume_mounts.extend(volume_mounts)

    #pod.spec.init_containers.extend(init_containers)

    return pod

c.KubeSpawner.modify_pod_hook = modify_pod_hook

# Setup culling of front end instance if timeout parameter is supplied.

idle_timeout = os.environ.get('IDLE_TIMEOUT')

if idle_timeout and int(idle_timeout):
    c.JupyterHub.services = [
        {
            'name': 'cull-idle',
            'admin': True,
            'command': ['cull-idle-servers', '--timeout=%s' % idle_timeout],
        }
    ]

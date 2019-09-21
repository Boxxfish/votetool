#Tests ai integration with webapp
from oauth2client.client import GoogleCredentials
from googleapiclient import discovery
from googleapiclient import errors

ml = discovery.build("AITestService", "v1")
project_id = 'projects/{}'.format('testai-253617')
request = ml.projects().models().create()parent=project_id, body

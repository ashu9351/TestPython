from __future__ import print_function
import grpc
import requests
import threading
import io
import pubsub_api_pb2 as pb2
import pubsub_api_pb2_grpc as pb2_grpc
import avro.schema
import avro.io
import time
import certifi
import json
import os
import redis
from authwrapper import AuthWrapper

semaphore = threading.Semaphore(1)
latest_replay_id = None

#key 3MVG9ZL0ppGP5UrAP59A8.dNkSsWx54hRgtkftFHZh1bxEMSGF6kwnRNA8VheLBe2RHROd01KucH2QHHt5ggh
#sec 22883FEE07FDBA0FD71F317F8A4821155253D7853C280B4302EA229A30B1DDEF
pool = redis.ConnectionPool(host='red-cf00a2sgqg4cnpin55g0', port=6379, db=0)
redis = redis.Redis(connection_pool=pool)
global accesstoken 
accesstoken = redis.get('ACCESS_TOKEN')

def do_auth():
    username = os.getenv('API_USER')
    password = os.environ.get('API_PASSWORD')
    authUrl = os.environ.get('API_AUTH_URL')
    clientId = os.getenv('CONSUMER_KEY')
    clientSecret = os.getenv('CONSUMER_SECRET')
    authUrl = os.getenv('API_AUTH_URL')
    print('>>>>>>>AUTH Start>>>>>>>>');
    print(authUrl)
    print(username)
    print(password)
    print(clientId)
    print(clientSecret)
    print(authUrl)
    '''payload={
        'grant_type': 'password',
        'client_id': '3MVG9ZL0ppGP5UrAP59A8.dNkSsWx54hRgtkftFHZh1bxEMSGF6kwnRNA8VheLBe2RHROd01KucH2QHHt5ggh',
        'client_secret': '22883FEE07FDBA0FD71F317F8A4821155253D7853C280B4302EA229A30B1DDEF',
        'username': 'ashutoshexams@gmail.com',
        'password': 'ashutosh9351aozWQvXaav1CPDQaHHgtU7pQy',
        'organizationId': '00D28000000dVa8EAE'
    }'''
    payload = {
        'grant_type': 'password',
        'client_id': clientId,
        'client_secret': clientSecret,
        'username': username,
        'password': password,
    }
    res = requests.post(authUrl, 
        headers={"Content-Type":"application/x-www-form-urlencoded"},
        data=payload)
    
    if res.status_code == 200:
        response = AuthWrapper(res.json())
        print (response.access_token)
        print (response.instance_url)
       
        '''accesstoken = response.access_token;
        os.environ['ACCESS_TOKEN'] = response.access_token;
        os.environ['REQUEST_URL'] = response.instance_url;'''
        redis.set('ACCESS_TOKEN', response.access_token)
        redis.set('REQUEST_URL', response.instance_url)
        value = redis.get('mykey')
        print('>>>>>>>AUTHORIZED>>>>>>>>');
        global authmetadata
        authmetadata = (('accesstoken', redis.get('ACCESS_TOKEN')),
                        ('instanceurl', redis.get('REQUEST_URL')),
                            ('tenantid', os.getenv('API_ORG'))) 
        return True
    else:
        return False
    #do_auth ends here
def subscribe_to_channel():
    with open(certifi.where(), 'rb') as f:
        creds = grpc.ssl_channel_credentials(f.read())
    with grpc.secure_channel('api.pubsub.salesforce.com:7443', creds) as channel:
        # All of the code in the rest of the tutorial will go inside
        # this block
        print ('>>>>>In subscribe')
        print ('>>>>ACCESS TOKEN IN SUB>>>>>',accesstoken)
        if not accesstoken:
            print ('>>>>>NOT AUTHORIZED')
            isauthorized = do_auth();
            if isauthorized:
                print ('>>>>>SUBS')
                print (authmetadata)
                def fetchReqStream(topic):
                    while True:
                        semaphore.acquire()
                        yield pb2.FetchRequest(
                            topic_name = topic,
                            replay_preset = pb2.ReplayPreset.LATEST,
                            num_requested = 1)

                def decode(schema, payload):
                    schema = avro.schema.parse(schema)
                    buf = io.BytesIO(payload)
                    decoder = avro.io.BinaryDecoder(buf)
                    reader = avro.io.DatumReader(schema)
                    ret = reader.read(decoder)
                    return ret

                mysubtopic = "/data/AccountChangeEvent"
                print('Subscribing to ' + mysubtopic)
                substream = stub.Subscribe(fetchReqStream(mysubtopic),
                        metadata=authmetadata)
                for event in substream:
                    if event.events:
                        semaphore.release()
                        print("Number of events received: ", len(event.events))
                        payloadbytes = event.events[0].event.payload
                        schemaid = event.events[0].event.schema_id
                        schema = stub.GetSchema(
                                pb2.SchemaRequest(schema_id=schemaid),
                                metadata=authmetadata).schema_json
                        decoded = decode(schema, payloadbytes)
                        print("Got an event!", json.dumps(decoded))
                    else:
                        print("[", time.strftime('%b %d, %Y %l:%M%p %Z'),
                        "] The subscription is active.")
                        latest_replay_id = event.latest_replay_id

subscribe_to_channel(); 

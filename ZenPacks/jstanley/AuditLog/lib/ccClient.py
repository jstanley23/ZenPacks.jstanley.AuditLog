import json
import requests
import urllib3


class ccClient(object):
    def __init__(self, ccHost, ccPort, ccUser, ccPass):
        self.host = ccHost
        self.port = ccPort
        self.user = ccUser
        self.password = ccPass
        self.session = requests.Session()
        urllib3.disable_warnings()

    def login(self):
        """Login."""
        url = "https://{}:{}/login".format(self.host, self.port)
        data = json.dumps({'Username': self.user, 'Password': self.password})
        headers = { 'Content-Type': 'application/json' }
        self.session.post(url, data=data, headers=headers, verify=False)

    def getKibanaLogs(self, searchMessage):
        uri='/api/controlplane/kibana/elasticsearch/_msearch'
        headers = {
            "kbn-xsrf": "reporting",
            "Content-Type": "application/json",
        }
        url = "https://{}:{}/{}".format(self.host, self.port, uri)
        data = self.buildKibanaPayload(searchMessage)
        output = self.session.post(url, data=data, headers=headers, verify=False)
        return self.prettifyKibanaOutput(output.json())

    def buildKibanaPayload(self, searchMessage, fieldType='zenossaudit'):
        idx = '{"index":"*"}'
        queryString = "*{0}* AND *{1}*".format(fieldType, searchMessage)
        queryDict = {
            "query": {
                "filtered": {
                    "query": {
                        "query_string": {
                            "query": queryString,
                            "analyze_wildcard": True
                        }
                    }
                }
            },
            "size": 500,
            "sort":[
                {   
                    "@timestamp": {
                        "order": "desc",
                        "unmapped_type":"boolean"
                    }
                }
            ],
            "fields": ["message"],
            "script_fields": {},
            "fielddata_fields": ["@timestamp"]
        }
        queryJson = json.dumps(queryDict)
        return  "{0}\n{1}\n".format(idx, queryJson)

    def prettifyKibanaOutput(self, results):
        output = []
        if not isinstance(results, dict):
            return [results]
        responses = results.get('responses', [])
        for response in responses:
            firstHits = response.get('hits', {})
            hits = firstHits.get('hits', [])
            for hit in hits:
                fields = hit.get('fields', {})
                message = fields.get('message')
                if not message:
                    continue
                if isinstance(message, list):
                    output.append(str(message[0]))
                else:
                    output.append(message)
        return output


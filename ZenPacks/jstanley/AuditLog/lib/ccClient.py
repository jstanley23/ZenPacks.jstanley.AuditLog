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
        headers = {'Content-Type': 'application/json'}
        request = self.session.post(
            url,
            data=data,
            headers=headers,
            verify=False
        )
        return request.ok

    def getKibanaLogs(self, searchMessage):
        uri = 'api/controlplane/kibana/internal/bsearch'
        headers = {
            'authority': '%s:%s' % (self.host, self.port),
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0',
            'kbn-version': '7.12.0',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept': '*/*',
            'origin': 'https://%s:%s' % (self.host, self.port),
            'referer': 'https://%s:%s/api/controlplane/kibana/app/discover' % (self.host, self.port),
        }
        url = "https://{}:{}/{}".format(self.host, self.port, uri)
        query, data = self.buildKibanaPayload(searchMessage)
        try:
            request = self.session.post(
                url,
                data=data,
                headers=headers,
                verify=False
            )
            request.raise_for_status()
            output = self.prettifyKibanaOutput(request.json())
        except Exception as e:
            output = ["Request to %s failed: %s" % (url, e.message)]
        query = "Kibana query: {0}".format(query)
        output.insert(0, '\n')
        output.insert(0, "Response Status: %s" % request.status_code)
        output.insert(0, '\n')
        output.insert(0, query)
        return output

    def buildKibanaPayload(self, searchMessage, fieldType='zenossaudit'):
        searchMessage = searchMessage.replace('/zport/dmd', '')
        queryString = 'fields.type: *{0}* AND message: "{1}"'.format(
            fieldType,
            searchMessage
        )

        queryDict =  {
            u'batch': [
                {
                    u'request': {
                        u'params': {
                            u'body': {
                                u'_source': False,
                                u'fields': [
                                    {
                                        u'field': u'message',
                                    }
                                ],
                                u'query': {
                                    u'bool': {
                                        u'must': [
                                            {
                                                u'query_string': {
                                                    u'analyze_wildcard': True,
                                                    u'query': queryString,
                                                }
                                            }
                                        ]
                                    }
                                },
                                u'size': 500,
                                u'sort': [
                                    {
                                        u'@timestamp': {
                                            u'order': u'desc',
                                            u'unmapped_type': u'boolean'
                                        }
                                    }
                                ],
                            },
                            u'index': u'*',
                        }
                    }
                }
            ]
        }

        queryJson = json.dumps(queryDict)
        return (queryString, queryJson)

    def prettifyKibanaOutput(self, results):
        output = []
        if not isinstance(results, dict):
            return [results]

        result = results.get('result', {})
        response = result.get('rawResponse', {})
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
                output.append(str(message))

        if not output:
            return ['No results found.']

        return output

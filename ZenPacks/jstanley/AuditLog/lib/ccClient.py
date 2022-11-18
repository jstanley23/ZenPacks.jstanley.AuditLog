import json
import requests
import time
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
            'kbn-xsrf': 'true',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept': '*/*',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'origin': 'https://%s:%s' % (self.host, self.port),
            'referer': 'https://%s:%s/api/controlplane/kibana/app/discover' % (self.host, self.port),
        }
        url = "https://{}:{}/{}".format(self.host, self.port, uri)
        query, data = self.buildKibanaPayload(searchMessage)
        isRunning = True
        isPartial = True
        attempts = 10
        output = []

        # bsearch can return results while the query is still running
        # We loop through requests until the response say it is done
        try:
            while isPartial and isRunning and attempts != 0:
                request = self.session.post(
                    url,
                    data=data,
                    headers=headers,
                    verify=False
                )
                request.raise_for_status()
                content = request.json()
                result = content.get('result', False)
                if result:
                    isRunning = result.get('isRunning', False)
                    isPartial = result.get('isPartial', False)

                attempts -= 1
                if attempts <= 0:
                    raise Exception("Query results have not fully returned, wait a few minutes and try again.")

                if isRunning:
                    time.sleep(5)

            output.extend(self.prettifyKibanaOutput(content))
        except Exception as e:
            output = ["Request to %s failed: %s" % (url, e.message)]

        query = "Kibana query: {0}".format(query)
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
                            u'index': u'logstash-*',
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

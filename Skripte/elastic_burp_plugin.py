from burp import IBurpExtender, IHttpListener, IExtensionHelpers
from java.io import PrintWriter
from org.python.core.util import StringUtil
import json
import datetime
import requests

class BurpExtender(IBurpExtender, IHttpListener):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self._callbacks.setExtensionName("Elasticsearch Logger")
        self._stdout = PrintWriter(callbacks.getStdout(), True)
        self._stderr = PrintWriter(callbacks.getStderr(), True)

        # Register HTTP listener
        callbacks.registerHttpListener(self)

        # Elasticsearch setup
        self.es_url = 'http://10.8.0.2:6002/burp-traffic/_doc/'  
        self._stdout.println("Elasticsearch Logger extension loaded")

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        try:
            timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
            if messageIsRequest:
                # Process request
                self._stdout.println("Processing request")
                request = messageInfo.getRequest()
                request_info = self._helpers.analyzeRequest(request)
                headers = request_info.getHeaders()
                body = request[request_info.getBodyOffset():].tostring()

                request_line = headers[0]
                method, path, _ = request_line.split(' ', 2)

                # Construct the full URL
                http_service = messageInfo.getHttpService()
                scheme = 'https' if http_service.getPort() == 443 else 'http'
                url = "{}://{}:{}{}".format(scheme, http_service.getHost(), http_service.getPort(), path)

                data = {
                    'tool': self._callbacks.getToolName(toolFlag),
                    'type': 'request',
                    'timestamp': timestamp,
                    'url': url,
                    'headers': list(headers),
                    'body': body
                }
                self._stdout.println("Request data prepared: " + json.dumps(data))
            else:
                # Process response
                self._stdout.println("Processing response")
                response = messageInfo.getResponse()
                response_info = self._helpers.analyzeResponse(response)
                headers = response_info.getHeaders()
                body = response[response_info.getBodyOffset():].tostring()

                data = {
                    'tool': self._callbacks.getToolName(toolFlag),
                    'type': 'response',
                    'timestamp': timestamp,
                    'status_code': response_info.getStatusCode(),
                    'headers': list(headers),
                    'body': body
                }
                self._stdout.println("Response data prepared: " + json.dumps(data))

            # Send data to Elasticsearch
            self._stdout.println("Sending data to Elasticsearch")
            self.send_to_elasticsearch(data)

        except Exception as e:
            self._stderr.println("Error processing HTTP message: " + str(e))

    def send_to_elasticsearch(self, data):
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(self.es_url, data=json.dumps(data), headers=headers)
            self._stdout.println("Elasticsearch response status: {}".format(response.status_code))
            if response.status_code not in [200, 201]:
                self._stderr.println("Failed to send data to Elasticsearch: " + response.text)
        except Exception as e:
            self._stderr.println("Error sending data to Elasticsearch: " + str(e))


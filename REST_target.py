from burp import IBurpExtender, IBurpExtenderCallbacks, ISessionHandlingAction, IHttpRequestResponse, \
    ICookie, ITab, IProxyListener, IHttpListener, IInterceptedProxyMessage
from java.io import PrintWriter

class BurpExtender(IBurpExtender, IProxyListener, IHttpListener):
    PLUGIN_NAME = "REST API in Target blank"
    COMMENT = "Created by REST API Plugin"

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName(self.PLUGIN_NAME)
        self.stdout = PrintWriter(callbacks.getStdout(), True)

        self._callbacks.registerProxyListener(self)
        self._callbacks.registerHttpListener(self)
        self.container = dict()
        self.container_requests = dict()
        self.stdout.println("{}\n".format(self.PLUGIN_NAME))

    def processProxyMessage(self, message_is_request, message):
        if message_is_request:
            message_info = message.getMessageInfo()
            req_info = self._helpers.analyzeRequest(message_info)
            method = req_info.getMethod()
            url = req_info.getUrl()
            port = str(url.getPort())
            url = url.toString()
            url_without_port = url[:url.find(port) - 1] + url[url.find(port) + len(port):]
            site_map = self._callbacks.getSiteMap(url_without_port)
            # self.stdout.println("Site map len: {}".format(len(site_map)))
            if len(site_map) == 0:
                return
            # Find method of first request
            target_method = self._helpers.analyzeRequest(site_map[0]).getMethod()
            # self.stdout.println("Request {} -- Target {}".format(method, target_method))
            if target_method != method: # and method != "GET":
                self.stdout.println("Add new request {} {}".format(method, url_without_port))
                headers = req_info.getHeaders()
                req_body = message_info.getRequest()[req_info.getBodyOffset():]
                old_header = headers[0]
                headers[0] = headers[0][:headers[0].find(" ", len(method) + 1)] + "[{}]".format(method) + \
                             headers[0][headers[0].find(" ", len(method) + 1):]
                self.container_requests.update({headers[0]: old_header})
                request_bytes = self._helpers.buildHttpMessage(headers, req_body)
                message_info.setRequest(request_bytes)
                message_info.setComment(self.COMMENT)
                self.container.update({headers[0]: site_map[0]})
        else:
            message_info = message.getMessageInfo()
            # self.stdout.println(self._helpers.analyzeRequest(message_info).getHeaders()[0])
            if self.container.get(self._helpers.analyzeRequest(message_info).getHeaders()[0], None) is not None:
                self._callbacks.addToSiteMap(message_info)
                self._callbacks.addToSiteMap(self.container.get
                                             (self._helpers.analyzeRequest(message_info).getHeaders()[0]))

    def processHttpMessage(self, tool_flag, message_is_request, message_info):
        message_headers = self._helpers.analyzeRequest(message_info).getHeaders()
        if message_is_request:
            if self.container_requests.get(message_headers[0], None) is not None:
                # self.stdout.println("Find in stack")
                req_body = message_info.getRequest()[self._helpers.analyzeRequest(message_info).getBodyOffset():]
                message_headers[0] = self.container_requests[message_headers[0]]
                message_info.setRequest(self._helpers.buildHttpMessage(message_headers, req_body))
                # self.stdout.println("Update request")

            # else:
            #    self.stdout.println(self._helpers.analyzeRequest(message_info).getHeaders()[0])

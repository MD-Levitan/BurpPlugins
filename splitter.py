from burp import IBurpExtender, IBurpExtenderCallbacks, ISessionHandlingAction, IHttpRequestResponse, \
    ICookie, ITab, IProxyListener, IHttpListener, IInterceptedProxyMessage
from java.io import PrintWriter
from itertools import chain


class BurpExtender(IBurpExtender, IHttpListener):
    PLUGIN_NAME = "Cookie Splitter"

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName(self.PLUGIN_NAME)
        self.stdout = PrintWriter(callbacks.getStdout(), True)

        self._callbacks.registerHttpListener(self)

    def processHttpMessage(self, tool_flag, message_is_request, message_info):
        message_headers = self._helpers.analyzeRequest(message_info).getHeaders()
        ptr = "Cookie:"
        if message_is_request:
            def split(x):
                return list(map(lambda x: ptr + " " + x, x[len(ptr) + 1:].split(';')))
            new_headers = list(filter(lambda x: x.find(ptr, 0, len(ptr)) == -1, message_headers))
            new_headers += list(map(lambda x: split(x), list(filter(lambda x: x.find(ptr, 0, len(ptr)) != -1,
                                                                        message_headers))))[0]
            print(new_headers)
            req_body = message_info.getRequest()[self._helpers.analyzeRequest(message_info).getBodyOffset():]
            message_info.setRequest(self._helpers.buildHttpMessage(new_headers, req_body))

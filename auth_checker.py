from burp import IBurpExtender, IBurpExtenderCallbacks, IScannerCheck, IHttpRequestResponse, IScanIssue
from java.io import PrintWriter


class BurpExtender(IBurpExtender, IScannerCheck):
    PLUGIN_NAME = "Authentication checker"
    COMMENT = "Created by REST API Plugin"

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName(self.PLUGIN_NAME)
        self.stdout = PrintWriter(callbacks.getStdout(), True)

        self._callbacks.registerScannerCheck(self)
        self.stdout.println("{}\n".format(self.PLUGIN_NAME))


    ''' List<IScanIssue> doPassiveScan(IHttpRequestResponse baseRequestResponse); '''    
    def doPassiveScan(self, baseRequestResponse):
        req_info = self._helpers.analyzeRequest(baseRequestResponse)
        headers = req_info.getHeaders()
        headers_new = list(filter(lambda x: False if "Cookie" in x or "Authorization" in x else True, headers))
        
        req_body = baseRequestResponse.getRequest()[req_info.getBodyOffset():]  
        if len(headers) != len(headers_new):
            modifiedRequestResponse = self._callbacks.makeHttpRequest(baseRequestResponse.getHttpService(), self._helpers.buildHttpMessage(headers_new, req_body))
            modified_response_info = self._helpers.analyzeResponse(modifiedRequestResponse.getResponse())
            base_response_info = self._helpers.analyzeResponse(baseRequestResponse.getResponse())
            self.stdout.println("{} {} - {}".format(req_info.getUrl(), base_response_info.getStatusCode(), modified_response_info.getStatusCode()))
            if base_response_info.getStatusCode() == modified_response_info.getStatusCode():
                return [CustomScanIssue(
                        baseRequestResponse.getHttpService(),
                        self._helpers.analyzeRequest(baseRequestResponse).getUrl(),
                        [baseRequestResponse],
                        "Breaking Authorization", "The request can be executed without authorization",
                        "High")]


#
# class implementing IScanIssue to hold our custom scan issue details
#
class CustomScanIssue (IScanIssue):
    def __init__(self, httpService, url, httpMessages, name, detail, severity):
        self._httpService = httpService
        self._url = url
        self._httpMessages = httpMessages
        self._name = name
        self._detail = detail
        self._severity = severity

    def getUrl(self):
        return self._url

    def getIssueName(self):
        return self._name

    def getIssueType(self):
        return 0

    def getSeverity(self):
        return self._severity

    def getConfidence(self):
        return "Tentative"

    def getIssueBackground(self):
        pass

    def getRemediationBackground(self):
        pass

    def getIssueDetail(self):
        return self._detail

    def getRemediationDetail(self):
        pass

    def getHttpMessages(self):
        return self._httpMessages

    def getHttpService(self):
        return self._httpService
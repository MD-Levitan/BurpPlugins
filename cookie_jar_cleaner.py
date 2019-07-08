from burp import IBurpExtender, IBurpExtenderCallbacks, ISessionHandlingAction, IHttpRequestResponse, ICookie
from java.io import PrintWriter
from java.util import Date
import datetime


class BurpExtender(IBurpExtender, ISessionHandlingAction):
    ACTION_NAME = "Remove expired Cookies"
    PLUGIN_NAME = "Cookie JAR Cleaner"
    """
    Implements IBurpExtender for hook into burp and inherit base classes.
    Implement IMessageEditorTabFactory to access createNewInstance.
    """

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName(self.PLUGIN_NAME)
        self._callbacks.registerSessionHandlingAction(self)

        self.stdout = PrintWriter(callbacks.getStdout(), True)
        # self.stderr = PrintWriter(callbacks.getStdout(), True)
        self.stdout.println("{}\n".format(self.PLUGIN_NAME))
        self.stdout.println('starting at time : {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        self.stdout.println("-----------------------------------------------------------------\n\n")
        return

    def getActionName(self):
        return self.ACTION_NAME

    def performAction(self, current_request, macro_items):
        """

        :param IHttpRequestResponse current_request:
        :param list(IHttpRequestResponse) macro_items:
        :return:
        """
        def createCookie(cookie):
            class Cookie(ICookie):

                def getDomain(self):
                    return cookie.getDomain()

                def getPath(self):
                    return cookie.getPath()

                def getExpiration(self):
                    return cookie.getExpiration()

                def getName(self):
                    return cookie.getName()

                def getValue(self):
                    return null
            return Cookie()

        cookies = self._callbacks.getCookieJarContents()
        for cookie in cookies:
            date = cookie.getExpiration()
            if date != None and date != "null" and date < datetime.datetime.now():
                self.stdout.println("Remove expired cookie: {} with expiration {}\n".format(cookie.getName(), date))
                self._callbacks.updateCookieJar(createCookie(cookie))

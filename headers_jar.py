from burp import IBurpExtender, IBurpExtenderCallbacks, ISessionHandlingAction, IHttpRequestResponse, ICookie, ITab
from java.io import PrintWriter
from javax import swing
from java.awt import BorderLayout


class BurpExtender(IBurpExtender, ITab, ISessionHandlingAction):
    PLUGIN_NAME = "Headers JAR"

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName(self.PLUGIN_NAME)
        self.stdout = PrintWriter(callbacks.getStdout(), True)

        self.jar = dict()

        self.tab = swing.JPanel(BorderLayout())

        # Create the text area at the top of the tab
        text_panel = swing.JPanel()

        box_vertical = swing.Box.createVerticalBox()

        box_horizontal = swing.Box.createHorizontalBox()
        box_horizontal.add(swing.JLabel(self.PLUGIN_NAME))
        box_vertical.add(box_horizontal)

        box_horizontal = swing.Box.createHorizontalBox()
        self.headers_names = swing.JTextArea('', 4, 20)
        self.headers_names.setLineWrap(True)
        box_horizontal.add(swing.JLabel("Header Names"))
        box_horizontal.add(self.headers_names)
        box_vertical.add(box_horizontal)

        box_vertical.add(swing.JButton('Set settings', actionPerformed=self.set_settings))

        box_vertical.add(swing.JButton('Print jar', actionPerformed=self.print_jar))

        text_panel.add(box_vertical)
        self.tab.add(text_panel, "West")


        callbacks.addSuiteTab(self)

        self.update_action = UpdateHeaders(self.stdout, self._helpers, self.jar)
        self.add_action = AddHeaders(self.stdout, self._helpers, self.jar)

        self._callbacks.registerSessionHandlingAction(self.update_action)
        self._callbacks.registerSessionHandlingAction(self.add_action)

        self.stdout.println("{}\n".format(self.PLUGIN_NAME))
        return

    def set_settings(self, event):
        headers = map(lambda x: str(x.strip(" ")), self.headers_names.text.split(","))
        settings = {"headers": headers}
        self.update_action.set_settings(settings)
        self.add_action.set_settings(settings)

    def print_jar(self, event):
        for (x, y) in self.jar.items():
            self.stdout.println("{} -- {}".format(x, y))

    def getTabCaption(self):
        """Return the text to be displayed on the tab"""
        return self.PLUGIN_NAME

    def getUiComponent(self):
        """Passes the UI to burp"""
        return self.tab


class UpdateHeaders(ISessionHandlingAction):
    ACTION_NAME = "Update headers from jar"

    def __init__(self, stdout, helpers, jar):
        self.stdout = stdout
        self._helpers = helpers
        self.headers = []
        self.jar = jar

    def set_settings(self, settings):
        self.headers = settings["headers"]

    def getActionName(self):
        return self.ACTION_NAME

    def performAction(self, current_request, macro_items):
        request_info = self._helpers.analyzeRequest(current_request)
        headers = request_info.getHeaders()
        req_body = current_request.getRequest()[request_info.getBodyOffset():]
        for i in range(1, len(headers)):
            header = headers[i]
            head = header[:header.find(":")]
            if head in self.headers and self.jar.get(head, None) is not None:
                    headers[i] = "{}: {}".format(head, self.jar.get(head))

        message = self._helpers.buildHttpMessage(headers, req_body)
        current_request.setRequest(message)


class AddHeaders(ISessionHandlingAction):
    ACTION_NAME = "Add headers to jar"

    def __init__(self, stdout, helpers, jar):
        self.stdout = stdout
        self._helpers = helpers
        self.headers = []
        self.jar = jar

    def set_settings(self, settings):
        self.headers = settings["headers"]

    def getActionName(self):
        return self.ACTION_NAME

    def performAction(self, current_request, macro_items):
        request_info = self._helpers.analyzeRequest(current_request)
        headers = request_info.getHeaders()
        for header in headers[1:]:
            head = header[:header.find(":")]
            if head in self.headers:
                break_p = header.find(":")
                self.jar.update({header[:break_p]: header[break_p + 1:]})
                self.stdout.println("Add to jar header: {}".format(head))

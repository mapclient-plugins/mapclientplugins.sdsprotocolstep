

from PySide6 import QtWidgets
from mapclientplugins.sdsprotocolstep.ui_configuredialog import Ui_ConfigureDialog

from mapclientplugins.sdsprotocolstep.protocols import protocols, is_sds_protocol


INVALID_STYLE_SHEET = 'background-color: rgba(239, 0, 0, 50)'
DEFAULT_STYLE_SHEET = ''


def _display_parameter(display_name, parameter):
    display = ""
    names = []
    name = display_name.lower()
    if name in parameter and parameter[name]:
        names.append(parameter[name])
    elif name + "s" in parameter and parameter[name + "s"]:
        names.extend(parameter[name + "s"])

    if len(names):
        display += "\n"
        display += f"## {display_name}"
        display += "s" if len(names) > 1 else ""
        display += "\n"
        for index, n in enumerate(names):
            display += f"{index + 1}. "
            if "info" in n:
                display += f"{n['info']} "

            details = []
            if "mimetype" in n:
                details.append(f"type=**{n['mimetype']}**")
            if "destination" in n:
                details.append(f"destination=**{n['destination']}**")

            if details:
                display += f"[{', '.join(details)}]"

            display += "\n"

    return display


class ConfigureDialog(QtWidgets.QDialog):
    """
    Configure dialog to present the user with the options to configure this step.
    """

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        self._ui = Ui_ConfigureDialog()
        self._ui.setupUi(self)

        # Keep track of the previous identifier so that we can track changes
        # and know how many occurrences of the current identifier there should
        # be.
        self._previousIdentifier = ''
        # Set a place holder for a callable that will get set from the step.
        # We will use this method to decide whether the identifier is unique.
        self.identifierOccursCount = None
        self._protocols = [p for p in protocols if is_sds_protocol(p)]
        self._ui.comboBoxProtocols.insertItems(0, ["--"] + [p['name'] for p in self._protocols])

        self._make_connections()

    def _make_connections(self):
        self._ui.lineEditIdentifier.textChanged.connect(self.validate)
        self._ui.comboBoxProtocols.currentIndexChanged.connect(self._protocol_changed)

    def _protocol_changed(self, index):
        if index == 0:
            self._ui.textEditProtocolInfo.clear()
        else:
            current_protocol = self._protocols[index - 1]

            display_importer_parameters = f"# {current_protocol['name']}\n"
            display_importer_parameters += current_protocol['info']
            display_importer_parameters += _display_parameter("Input", current_protocol)

            self._ui.textEditProtocolInfo.setMarkdown(display_importer_parameters)

    def accept(self):
        """
        Override the accept method so that we can confirm saving an
        invalid configuration.
        """
        result = QtWidgets.QMessageBox.StandardButton.Yes
        if not self.validate():
            result = QtWidgets.QMessageBox.warning(
                self,
                'Invalid Configuration',
                'This configuration is invalid.  Unpredictable behaviour may result if you choose \'Yes\', are you sure you want to save this configuration?)',
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No, QtWidgets.QMessageBox.StandardButton.No)

        if result == QtWidgets.QMessageBox.StandardButton.Yes:
            QtWidgets.QDialog.accept(self)

    def validate(self):
        """
        Validate the configuration dialog fields.  For any field that is not valid
        set the style sheet to the INVALID_STYLE_SHEET.  Return the outcome of the
        overall validity of the configuration.
        """
        # Determine if the current identifier is unique throughout the workflow
        # The identifierOccursCount method is part of the interface to the workflow framework.
        value = self.identifierOccursCount(self._ui.lineEditIdentifier.text())
        valid = (value == 0) or (value == 1 and self._previousIdentifier == self._ui.lineEditIdentifier.text())
        if valid:
            self._ui.lineEditIdentifier.setStyleSheet(DEFAULT_STYLE_SHEET)
        else:
            self._ui.lineEditIdentifier.setStyleSheet(INVALID_STYLE_SHEET)

        protocol_valid = self._ui.comboBoxProtocols.currentText() != '--'
        return valid and protocol_valid

    def getConfig(self):
        """
        Get the current value of the configuration from the dialog.  Also
        set the _previousIdentifier value so that we can check uniqueness of the
        identifier over the whole of the workflow.
        """
        self._previousIdentifier = self._ui.lineEditIdentifier.text()
        config = {'identifier': self._ui.lineEditIdentifier.text(), 'protocol_name': self._ui.comboBoxProtocols.currentText()}
        return config

    def setConfig(self, config):
        """
        Set the current value of the configuration for the dialog.  Also
        set the _previousIdentifier value so that we can check uniqueness of the
        identifier over the whole of the workflow.
        """
        self._previousIdentifier = config['identifier']
        self._ui.lineEditIdentifier.setText(config['identifier'])
        self._ui.comboBoxProtocols.setCurrentText(config['protocol_name'])

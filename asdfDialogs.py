from PyQt4.QtCore import *
from PyQt4.QtGui import * 
from PyQt4.QtWebKit import QWebView
from PyQt4.QtNetwork import *

class AsdfHelpDialog(QDialog):

	html = """<html> <head> <style> body{ background-color: #fff; } td { width: 45%; } </style> </head> <body> <h1 style="text-align: center;"><span style="font-family: helvetica; color: #999999;">ASDF Help</span></h1> <hr /> 
	<table style="background-color: #e6e4e6; width: 90%; font-size: 14px;" border="0" cellspacing="5" cellpadding="5" align="center"><caption><strong>File</strong></caption> <tbody> <tr> <td style="background-color: #807f80;"><span style="font-size: small;"><strong><span style="color: #ffffff;">Action</span></strong></span></td> <td style="background-color: #807f80;"><span style="font-size: small;"><strong><span style="color: #ffffff;">Hotkey</span></strong></span></td> </tr> <tr> <td>New File</td> <td>Ctrl + N</td> </tr> <tr> <td>Save</td> <td>Ctrl + S</td> </tr> <tr> <td>Save as</td> <td>Ctrl + Shift + S</td> </tr> <tr> <td>Open</td> <td>Ctrl + O</td> </tr> <tr> <td>Export HTML</td> <td>Ctrl + H</td> </tr> <tr> <td>Export PDF</td> <td>Ctrl + P</td> </tr> </tbody> </table> <br> 
	<table style="background-color: #e6e4e6; width: 90%; font-size: 14px;" border="0" cellspacing="5" cellpadding="5" align="center"><caption><strong>Edit</strong></caption> <tbody> <tr> <td style="background-color: #807f80;"><span style="font-size: small;"><strong><span style="color: #ffffff;">Action</span></strong></span></td> <td style="background-color: #807f80;"><span style="font-size: small;"><strong><span style="color: #ffffff;">Hotkey</span></strong></span></td> </tr> <tr> <td>Cut</td> <td>Ctrl + X</td> </tr> <tr> <td>Copy</td> <td>Ctrl + C</td> </tr> <tr> <td>Paste</td> <td>Ctrl + V</td> </tr> <tr> <td>Undo</td> <td>Ctrl + Z</td> </tr> <tr> <td>Redo</td> <td>Ctrl + Y</td> </tr> <tr> <td>Find and replace</td> <td>Ctrl + F</td> </tr> </tbody> </table> <br> 
	<table style="background-color: #e6e4e6; width: 90%; font-size: 14px;" border="0" cellspacing="5" cellpadding="5" align="center"><caption><strong>Format</strong></caption> <tbody> <tr> <td style="background-color: #807f80;"><span style="font-size: small;"><strong><span style="color: #ffffff;">Action</span></strong></span></td> <td style="background-color: #807f80;"><span style="font-size: small;"><strong><span style="color: #ffffff;">Hotkey</span></strong></span></td> </tr> <tr> <td>Bold</td> <td>Ctrl + B</td> </tr> <tr> <td>Italic</td> <td>Ctrl + I</td> </tr> <tr> <td>Heading 1-6</td> <td>Ctrl + [1-6]</td> </tr> <tr> <td>Bulleted list</td> <td>Ctrl + .</td> </tr> <tr> <td>Numbered list</td> <td>Ctrl + ,</td> </tr> <tr> <td>Insert image</td> <td>Ctrl + M</td> </tr> <tr> <td>Insert hyperlink</td> <td>Ctrl + L</td> </tr> </tbody> </table> <br> 
	<table style="background-color: #e6e4e6; width: 90%; font-size: 14px;" border="0" cellspacing="5" cellpadding="5" align="center"><caption><strong>Settings</strong></caption> <tbody> <tr> <td style="background-color: #807f80;"><span style="font-size: small;"><strong><span style="color: #ffffff;">Action</span></strong></span></td> <td style="background-color: #807f80" ><span style="font-size: small;"><strong><span style="color: #ffffff;">Hotkey</span></strong></span></td> </tr> <tr> <td>Focus mode (hidden UI)</td> <td>ESC</td> </tr> <tr> <td>Help</td> <td>F1</td> </tr> <tr> <td>Font configurations</td> <td>F2</td> </tr> <tr> <td>Import CSS</td> <td>F3</td> </tr> <tr> <td>Syntax highlight</td> <td>F4</td> </tr> <tr> <td>Plain text mode</td> <td>F5</td> </tr> <tr> <td>Vertical view</td> <td>F6</td> </tr> <tr> <td>Horizontal view</td> <td>F7</td> </tr> <tr> <td>Fullscreen mode</td> <td>F11</td> </tr> </tbody> </table> </body> </html>
"""
	def __init__(self):
		QDialog.__init__(self)
		self.layout = QVBoxLayout()
		self.helpContent = QWebView()
		self.helpContent.setHtml(self.html)
		self.helpContent.setFixedSize(500,500)
		self.okButton = QPushButton("Close")
		self.layout.addWidget(self.helpContent,True)
		self.layout.addWidget(self.okButton, False)
		self.setWindowFlags(Qt.FramelessWindowHint|Qt.Popup)
		self.setStyleSheet("QDialog { background-color: #777;}")
		self.setLayout(self.layout)
		self.okButton.clicked.connect(self.close)

class AsdfAboutDialog(QDialog):
	def __init__(self):
		QDialog.__init__(self)

		self.setFixedSize(300,300)

		self.content = "Copyright © 2013 Tsz-Ho Yu. Released under the GPL 3 license."
		self.layout = QVBoxLayout()

		self.logoLabel = QLabel()
		self.logoLabel.setFixedSize(100,100)
		self.logo = QPixmap(":icons/logo.png")	
		self.logo = self.logo.scaled(self.logoLabel.size(), Qt.KeepAspectRatio)
		self.logoLabel.setPixmap(self.logo)
		self.logoLabel.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)

		self.titleLabel = QLabel("asdf markdown editor.")
		titleFont = QFont("Arial", 18, QFont.Bold)
		self.titleLabel.setFont(titleFont)
		self.titleLabel.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)

		self.contentLabel = QLabel(self.content)
		self.contentLabel.setWordWrap(True)
		contentFont = QFont("Arial", 12)
		self.contentLabel.setFont(contentFont)
		self.contentLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
		self.okButton = QPushButton("Close")

		self.layout.addWidget(self.titleLabel, False)
		self.layout.addWidget(self.logoLabel, False)
		self.layout.addWidget(self.contentLabel, True)
		self.layout.addWidget(self.okButton,  False)
		self.layout.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
		self.okButton.clicked.connect(self.close)

		self.setLayout(self.layout)


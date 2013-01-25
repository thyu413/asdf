import re
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class AsdfFindWidget(QFrame):
	def __init__(self, parent, editor):
		QDialog.__init__(self, parent, Qt.Dialog | Qt.WindowCloseButtonHint)
		self.tFind = QLineEdit()
		self.tReplace = QLineEdit()
		self.buttonFind = QPushButton("&Find")
		self.buttonReplace = QPushButton("&Replace")
		self.buttonReplaceAll = QPushButton("Replace &all")
		self.buttonCancel = QPushButton("&Cancel")
		self.editor = editor
		layout = QGridLayout()
		
		layout.addWidget(QLabel("Search for:"),0,0,1,1)
		layout.addWidget(QLabel("Replace with:"),1,0,1,1)
		layout.addWidget(self.tFind,0,1,1,3)
		layout.addWidget(self.tReplace,1,1,1,3)
		layout.addWidget(self.buttonFind,2,0,1,1)
		layout.addWidget(self.buttonReplace,2,1,1,1)
		layout.addWidget(self.buttonReplaceAll,2,2,1,1)
		layout.addWidget(self.buttonCancel,2,3,1,1)

		self.buttonCancel.clicked.connect(self.hide)
		self.buttonFind.clicked.connect(self.find)
		self.buttonReplace.clicked.connect(self.replace)
		self.buttonReplaceAll.clicked.connect(self.replaceAll)

		self.setLayout(layout)

	def find(self):
		# find current cursor's position
		c = self.editor.textCursor();
		cPos = c.position()
		# find the words using regex
		reg = re.compile(self.tFind.text())
		ret = reg.search(self.editor.toPlainText(), cPos)
		# if not found, rewind and search again
		if ret == None:
			ret = reg.search(self.editor.toPlainText(), 0)
			if ret == None:
				# can't find any!
				return
		# if found, update the cursor
		c.setPosition(ret.start())
		c.setPosition(ret.end(), QTextCursor.KeepAnchor)
		self.editor.setTextCursor(c)

	def replace(self):
		# find current cursor's position
		c = self.editor.textCursor();
		cPos = c.position()
		# find the words using regex
		reg = re.compile(self.tFind.text())
		ret = reg.search(self.editor.toPlainText(), cPos)
		# if not found, rewind and search again
		if ret == None:
			ret = reg.search(self.editor.toPlainText(), 0)
			if ret == None:
				# can't find any!
				return
		# if found, update the cursor
		c.setPosition(ret.start())
		c.setPosition(ret.end(), QTextCursor.KeepAnchor)
		self.editor.setTextCursor(c)
		# replace with new word
		self.editor.textCursor().insertText(self.tReplace.text())

	def replaceAll(self):
		# number of replaced words
		c = self.editor.textCursor();
		replaced = 0
		# make regular expression
		reg = re.compile(self.tFind.text())
		# search from the very beginning 
		cPos = 0
		while True:
			ret = reg.search(self.editor.toPlainText(), cPos)
			if ret == None:
				QMessageBox.information(self, "Replace all", "%d matches replaced." % replaced)
				return
			else:
				c.setPosition(ret.start())
				c.setPosition(ret.end(), QTextCursor.KeepAnchor)
				self.editor.setTextCursor(c)
				self.editor.textCursor().insertText(self.tReplace.text())
				replaced = replaced + 1
				cPos = ret.end()


class AsdfFileBrowser(QFrame):
	
	selected = pyqtSignal("QString")

	def __init__(self):
		self.currentpath = ""		
		super(AsdfFileBrowser, self).__init__()
	
		# Make file system model
		self.browserModel = QFileSystemModel()
		rootIndex = self.browserModel.setRootPath(QDir.currentPath())
		self.browserModel.setFilter(QDir.AllEntries | QDir.NoDot)

		# make list view 
		self.browser = QListView()
		self.browser.setModel(self.browserModel)
		self.browser.setRootIndex(rootIndex)
		
		# address bar 
		self.browserDir = QLineEdit()
		self.browserDir.setText(QDir.currentPath())

		# set layout
		self.browserBox = QVBoxLayout()
		self.browserBox.addWidget(self.browserDir, False)
		self.browserBox.addWidget(self.browser, True)
		self.setLayout(self.browserBox)
		
		# do something when browser is double clicked 
		self.browser.doubleClicked[QModelIndex].connect(self.asdfBrowserClicked)
		
		# do something when the dirctory bar is changed
		self.browserDir.returnPressed.connect(self.asdfBrowserDirChange)

		# set browser style
		pal = QPalette()
		self.browserBgColor = QColor(255,255,255)
		self.browserFgColor = QColor( 50, 50, 50)
		pal.setColor(QPalette.Base, self.browserBgColor)
		pal.setColor(QPalette.Text, self.browserFgColor)
		self.browser.setPalette(pal)
		self.browserDir.setPalette(pal)
		
		# set initial size
		self.resize(200, 500)
		self.setMaximumWidth(300)

	def asdfBrowserDirChange(self):
		path = self.browserDir.text()		
		index = self.browserModel.setRootPath(path)
		self.browser.setRootIndex(index)

	def asdfBrowserClicked(self):
		# Get index and path 
		index 	= self.browser.selectionModel().currentIndex()
		path 	= self.browserModel.filePath(index)
		# If directory is clicked, change directory
		if (self.browserModel.isDir(index)):
			index = self.browserModel.setRootPath(path)
			self.browser.setRootIndex(index)
			self.browserDir.setText(path)
		else:
			self.selected.emit(path)


class AsdfHighlighter(QSyntaxHighlighter):
	def __init__(self, document):
		QSyntaxHighlighter.__init__(self, document)
		self.enabled = True;
		self.highLightStyles = {
			"heading": 		self.format(QColor(0,0,255),["bold", "underline"]),
			"italic":	 	self.format(QColor(255,0,0), "italic"),
			"bold": 		self.format(QColor(0,255,0), "bold"), 
			"rbrackets": 	self.format(QColor(0,100,255), "bold"), 
			"cbrackets": 	self.format(QColor(0,255,255), "bold"), 
			"sbrackets": 	self.format(QColor(0,255,255), "bold"), 
			"list": 		self.format(QColor(255,255,0), "bold"), 
			"rule": 		self.format(QColor(128,128,128), "bold"), 
		}
		self.rules = [
			# headings 
			(QRegExp("^#[^\n]*"), 0, self.highLightStyles["heading"]),
			# italic 
			(QRegExp("(\*{1}[^\*]+\*{1}|\*{2}[^\*]+\*{2}|\*{3}[^\*]+\*{3})"), 0, self.highLightStyles["italic"]),
			(QRegExp("(_{1}[^_]+_{1}|_{2}[^_]+_{2}|_{3}[^_]+_{3})"), 0, self.highLightStyles["bold"]),
			# inside brackets
			(QRegExp("\([^\(\)]*\)"), 0, self.highLightStyles["rbrackets"]),
			(QRegExp("(\!)?\[[^\[\]]*\](\:)?"), 0, self.highLightStyles["cbrackets"]),
			(QRegExp("<[^<>]*>"), 0, self.highLightStyles["sbrackets"]),
			# lists  
			(QRegExp("^[\s]*(\*|\+|\-)[\s]+[^\n]*"), 0, self.highLightStyles["list"]),
			(QRegExp("^[\s]*(\d).[\s]+[^\n]*"), 0, self.highLightStyles["list"]), 
			# rules
			(QRegExp("^[\s\*\-]*(\*|\-)[\s\*\-]*(\*|\-)[\s\*\-]*(\*|\-)[\s\*\-]*"), 0, self.highLightStyles["rule"]), 
		]
		self.setCurrentBlockState(0)
	
	def format(self, color, style=''):
		# Return a QTextCharFormat with given attributes
		_format = QTextCharFormat()
		_format.setForeground(color)
		if "bold" in style:
			_format.setFontWeight(QFont.Bold)
		if "italic" in style:
			_format.setFontItalic(True)
		if "underline" in style:
			_format.setFontUnderline(True)
		return _format

	def highlightBlock(self, text):
		if not self.enabled:
			return
		for expression, nth, format in self.rules:
			index = expression.indexIn(text,0)
			while index >= 0:
				index = expression.pos(nth)
				length = len(expression.cap(nth))
				self.setFormat(index, length, format)
				index = expression.indexIn(text, index + length)
		self.setCurrentBlockState(0)	
		

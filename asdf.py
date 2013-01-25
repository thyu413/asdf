import sys
import re
import codecs
import markdown
import subprocess
import os
import asdfResource
from asdfWidgets import *
from asdfDialogs import *
from PyQt4.QtWebKit import QWebView
from PyQt4.QtNetwork import *
from PyQt4.QtCore import *
from PyQt4.QtGui import * 

class ASDF(QMainWindow):

	def __init__(self, argv):
		super(ASDF, self).__init__()
		self.setWindowTitle("asdf")
		self.setWindowIcon(QIcon(":icons/icon_asdf.png"))
		self.initSettings()
		self.initUI()
		self.setupUI()
		self.newFile()
		self.show()

		# restore state from previous session
		self.winState = QSettings()
		savedGeometry = self.winState.value("mainWindowGeometry")
		savedState = self.winState.value("mainWindowState")
		savedCSS = self.winState.value("cssState")
		if (savedGeometry != None):
			self.restoreGeometry(savedGeometry)
		if (savedState != None):
			self.restoreState(savedState);
		if (savedCSS != None):
			self.viewerStyle = savedCSS

	def closeEvent(self, event):		
		stateSettings = QSettings()
		stateSettings.setValue("mainWindowGeometry", self.saveGeometry())
		stateSettings.setValue("mainWindowState", self.saveState())
		QMainWindow.closeEvent(self, event)
	
	def modulePath(self):
		if hasattr(sys, "frozen"):
			return os.path.dirname(os.path.realpath(sys.executable))
		return os.path.dirname(os.path.realpath(__file__))

	def initSettings(self):

		# read settings 
		self.updateFreq = 1000
		self.markupEnabled = True
		self.editorBgColor = QColor( 50, 50, 50)
		self.editorFgColor = QColor(255,255,255)
		self.viewerBgColor = QColor(255,255,255)
		self.viewerFgColor = QColor( 50, 50, 50)
		self.hideMode = False
		self.viewerStyle = ""

		# init pdf printer
		self.pdfPrinter = QPrinter(QPrinterInfo.defaultPrinter(), QPrinter.HighResolution)
		self.pdfPrinter.setOutputFormat(QPrinter.PdfFormat)
		self.pdfPrinter.setOrientation(QPrinter.Portrait)
		self.pdfPrinter.setPageSize(QPrinter.A4)
		self.pdfPrinter.setFullPage(True)
		
		# numebred list count
		self.NlistCount = 1

		# exepath
		self.exePath = self.modulePath()

		# HTML templates
		self.strHtmlTemplate = "<!DOCTYPE HTML><html><head><style>{1}</style></head><title></title><body>{0}</body></html>"

	def setupUI(self):
		# setup timer 	
		self.refreshTimer = QTimer()
		self.refreshTimer.timeout.connect(self.refreshView)
		self.refreshTimer.start(self.updateFreq)

	def initUI(self):

		# editor 
		self.editor = QPlainTextEdit()
		self.editor.setFrameStyle(QFrame.WinPanel | QFrame.Sunken)
		self.editor.setContentsMargins(0,0,0,0)
		self.editor.setTabStopWidth(40)		

		#editor highlight
		self.highlight = AsdfHighlighter(self.editor.document())
		
		# viewer 
		self.viewer = QWebView()
		
		# file browser
		self.browser = AsdfFileBrowser()
		self.browser.selected.connect(self.browserSelected)
		
		# find dialog
		self.fWidget = AsdfFindWidget(self, self.editor)
		self.fWidget.hide()

		# help dialog
		self.helpDialog = AsdfHelpDialog()

		# about dialog
		self.aboutDialog = AsdfAboutDialog()

		# set editor style
		pal = QPalette()
		pal.setColor(QPalette.Base, self.editorBgColor)
		pal.setColor(QPalette.Text, self.editorFgColor)
		self.editor.setPalette(pal)

		# set viewer style 
		pal = QPalette()
		pal.setColor(QPalette.Base, self.viewerBgColor)
		pal.setColor(QPalette.Text, self.viewerFgColor)
		self.viewer.setPalette(pal)

		# set font for editor
		self.defaultFont = QFont()
		self.defaultFont.setStyleHint(QFont.TypeWriter, QFont.PreferDefault)
		self.defaultFont.setFamily(self.defaultFont.defaultFamily())
		self.defaultFont.setPointSize(12)
		self.editor.setFont(self.defaultFont)

		# set actions and shortcuts

		# Edit and format 

		actionCopy = QAction(QIcon(":icons/icon_copy.png"), "Copy", self)
		actionCopy.triggered.connect(self.editor.copy)
		QShortcut(QKeySequence("Ctrl+C", 0), self, self.editor.copy)
		
		actionCut = QAction(QIcon(":icons/icon_cut.png"), "Cut", self)
		actionCut.triggered.connect(self.editor.cut)
		QShortcut(QKeySequence("Ctrl+X", 0), self, self.editor.cut)
		
		actionPaste = QAction(QIcon(":icons/icon_paste.png"), "Paste", self)
		actionPaste.triggered.connect(self.editor.paste)
		QShortcut(QKeySequence("Ctrl+V", 0), self, self.editor.paste)
		
		actionUndo = QAction(QIcon(":icons/icon_undo.png"), "Undo", self)
		actionUndo.triggered.connect(self.editor.undo)
		QShortcut(QKeySequence("Ctrl+Z", 0), self, self.editor.undo)

		actionRedo = QAction(QIcon(":icons/icon_redo.png"), "Redo", self)
		actionRedo.triggered.connect(self.editor.redo)
		QShortcut(QKeySequence("Ctrl+Y", 0), self, self.editor.redo)
		
		actionBold = QAction(QIcon(":icons/icon_bold.png"), "Bold", self)
		actionBold.triggered.connect(self.editBold)
		QShortcut(QKeySequence("Ctrl+B", 0), self, self.editBold)
		
		actionItalic = QAction(QIcon(":icons/icon_italic.png"), "Italic", self)
		actionItalic.triggered.connect(self.editItalic)
		QShortcut(QKeySequence("Ctrl+I", 0), self, self.editItalic)
		
		actionBlist = QAction(QIcon(":icons/icon_blist.png"), "Bulleted list", self)
		actionBlist.triggered.connect(self.editBlist)
		QShortcut(QKeySequence("Ctrl+.", 0), self, self.editBlist)
		
		actionNlist = QAction(QIcon(":icons/icon_nlist.png"), "Numbered list", self)
		actionNlist.triggered.connect(self.editNlist)
		QShortcut(QKeySequence("Ctrl+,", 0), self, self.editNlist)

		actionImage = QAction(QIcon(":icons/icon_image.png"), "Insert image", self)
		actionImage.triggered.connect(self.insertImage)
		QShortcut(QKeySequence("Ctrl+M", 0), self, self.insertImage)
		
		actionLink = QAction(QIcon(":icons/icon_link.png"), "Insert hyperlink", self)
		actionLink.triggered.connect(self.insertLink)
		QShortcut(QKeySequence("Ctrl+L", 0), self, self.insertLink)
		

		actionFind = QAction(QIcon(":icons/icon_find.png"), "Find and Replace", self)
		actionFind.triggered.connect(self.findText)
		QShortcut(QKeySequence("Ctrl+F", 0), self, self.findText)

		actionH1 = QAction(QIcon(":icons/icon_fonth1.png"), "Heading 1", self)
		actionH2 = QAction(QIcon(":icons/icon_fonth1.png"), "Heading 2", self)
		actionH3 = QAction(QIcon(":icons/icon_fonth3.png"), "Heading 3", self)
		actionH4 = QAction(QIcon(":icons/icon_fonth4.png"), "Heading 4", self)
		actionH5 = QAction(QIcon(":icons/icon_fonth5.png"), "Heading 5", self)
		actionH6 = QAction(QIcon(":icons/icon_fonth6.png"), "Heading 6", self)
		QShortcut(QKeySequence("Ctrl+1", 0), self, self.editH1)
		QShortcut(QKeySequence("Ctrl+2", 0), self, self.editH2)
		QShortcut(QKeySequence("Ctrl+3", 0), self, self.editH3)
		QShortcut(QKeySequence("Ctrl+4", 0), self, self.editH4)
		QShortcut(QKeySequence("Ctrl+5", 0), self, self.editH5)
		QShortcut(QKeySequence("Ctrl+6", 0), self, self.editH6)
		actionH1.triggered.connect(self.editH1)
		actionH2.triggered.connect(self.editH2)
		actionH3.triggered.connect(self.editH3)
		actionH4.triggered.connect(self.editH4)
		actionH5.triggered.connect(self.editH5)
		actionH6.triggered.connect(self.editH6)

		# FILE 

		actionNew = QAction(QIcon(":icons/icon_new.png"), "New", self)
		actionNew.triggered.connect(self.newFile)
		QShortcut(QKeySequence("Ctrl+N", 0), self, self.newFile)
		
		actionSave = QAction(QIcon(":icons/icon_save.png"), "Save", self)
		actionSave.triggered.connect(self.saveFile)
		QShortcut(QKeySequence("Ctrl+S", 0), self, self.saveFile)

		actionSaveAs = QAction(QIcon(":icons/icon_saveas.png"), "Save as", self)
		actionSaveAs.triggered.connect(self.saveAsFile)
		QShortcut(QKeySequence("Ctrl+Shift+S", 0), self, self.saveAsFile)

		actionOpen = QAction(QIcon(":icons/icon_open.png"), "Open", self)
		actionOpen.triggered.connect(self.openFile)
		QShortcut(QKeySequence("Ctrl+O", 0), self, self.openFile)
		
		actionExportHtml = QAction(QIcon(":icons/icon_html.png"), "Export HTML", self)
		actionExportHtml.triggered.connect(self.exportHtml)
		QShortcut(QKeySequence("Ctrl+H", 0), self, self.exportHtml)
		
		actionExportPdf = QAction(QIcon(":icons/icon_pdf.png"), "Export PDF", self)
		actionExportPdf.triggered.connect(self.exportPdf)
		QShortcut(QKeySequence("Ctrl+P", 0), self, self.exportPdf)

		# SETTINGS 

		actionHideToolbar = QAction(QIcon(":icons/icon_showmenu.png"), "Hide menu", self)
		actionHideToolbar.triggered.connect(self.hideToolbar)
		QShortcut(QKeySequence("ESC", 0), self, self.hideToolbar)

		actionHelp = QAction(QIcon(":icons/icon_help.png"), "Help", self)
		actionHelp.triggered.connect(self.showHelp)
		QShortcut(QKeySequence("F1", 0), self, self.showHelp)

		actionFontConfig = QAction(QIcon(":icons/icon_font.png"), "Font", self)
		actionFontConfig.triggered.connect(self.changeFont)
		QShortcut(QKeySequence("F2", 0), self, self.changeFont)

		actionCSS = QAction(QIcon(":icons/icon_css.png"), "Set CSS", self)
		actionCSS.triggered.connect(self.importCSS)
		QShortcut(QKeySequence("F3", 0), self, self.importCSS)

		actionHighlight = QAction(QIcon(":icons/icon_highlight.png"), "Syntax highlight", self)
		actionHighlight.triggered.connect(self.toggleHighlight)
		QShortcut(QKeySequence("F4", 0), self, self.toggleHighlight)
			
		actionTogglePlainText = QAction(QIcon(":icons/icon_text.png"), "Plain text", self)
		actionTogglePlainText.triggered.connect(self.togglePlainText)
		QShortcut(QKeySequence("F5", 0), self, self.togglePlainText)
		
		actionViewVertical = QAction(QIcon(":icons/icon_vertical.png"), "Vertical split", self)
		actionViewVertical.triggered.connect(self.viewVertical)
		QShortcut(QKeySequence("F6", 0), self, self.viewVertical)
		
		actionViewHorizontal = QAction(QIcon(":icons/icon_horizontal.png"), "Horizontal split", self)
		actionViewHorizontal.triggered.connect(self.viewHorizontal)
		QShortcut(QKeySequence("F7", 0), self, self.viewHorizontal)

		actionAbout = QAction(QIcon(":icons/icon_asdf.png"), "About asdf...", self)
		actionAbout.triggered.connect(self.showAbout)
		QShortcut(QKeySequence("F8", 0), self, self.showAbout)

		actionToggleFullScreen = QAction(QIcon(":icons/icon_fullscreen.png"), "&FullScreen", self)
		actionToggleFullScreen.triggered.connect(self.toggleFullScreen)
		QShortcut(QKeySequence("F11", 0), self, self.toggleFullScreen)

		# File toolbar
		self.toolbarFile = QToolBar("toolbarFile")
		self.toolbarFile.setObjectName("toolbarFile")
		self.toolbarFile.setIconSize(QSize(36,36))
		self.toolbarFile.addAction(actionNew)
		self.toolbarFile.addAction(actionSave)
		self.toolbarFile.addAction(actionSaveAs)
		self.toolbarFile.addAction(actionOpen)
		self.toolbarFile.addSeparator()
		self.toolbarFile.addAction(actionExportHtml)		
		self.toolbarFile.addAction(actionExportPdf)		

		# Edit toolbr 
		self.toolbarEdit = QToolBar("toolbarEdit")
		self.toolbarEdit.setObjectName("toolbarEdit")
		self.toolbarEdit.setIconSize(QSize(36,36))
		self.toolbarEdit.addAction(actionCut)		
		self.toolbarEdit.addAction(actionCopy)		
		self.toolbarEdit.addAction(actionPaste)		
		self.toolbarEdit.addSeparator()
		self.toolbarEdit.addAction(actionUndo)
		self.toolbarEdit.addAction(actionRedo)
		self.toolbarEdit.addAction(actionFind)
		
		# Format toolbar 
		self.toolbarFormat = QToolBar("toolbarFormat")
		self.toolbarFormat.setObjectName("toolbarFormat")
		self.toolbarFormat.setIconSize(QSize(36,36))
		self.toolbarFormat.addAction(actionBold)
		self.toolbarFormat.addAction(actionItalic)
		self.toolbarFormat.addSeparator()
		self.toolbarFormat.addAction(actionH1)
		self.toolbarFormat.addAction(actionH2)
		self.toolbarFormat.addAction(actionH3)
		self.toolbarFormat.addAction(actionH4)
		self.toolbarFormat.addAction(actionH5)
		self.toolbarFormat.addAction(actionH6)
		self.toolbarFormat.addSeparator()
		self.toolbarFormat.addAction(actionBlist)
		self.toolbarFormat.addAction(actionNlist)
		self.toolbarFormat.addAction(actionImage)
		self.toolbarFormat.addAction(actionLink)

		# Setting toolbar 
		self.toolbarSettings = QToolBar("toolbarSettings")
		self.toolbarSettings.setObjectName("toolbarSettings")
		self.toolbarSettings.setIconSize(QSize(36,36))
		self.toolbarSettings.addAction(actionHideToolbar)
		self.toolbarSettings.addAction(actionFontConfig)
		self.toolbarSettings.addAction(actionCSS)
		self.toolbarSettings.addAction(actionHighlight)
		self.toolbarSettings.addAction(actionTogglePlainText)
		self.toolbarSettings.addAction(actionViewVertical)
		self.toolbarSettings.addAction(actionViewHorizontal)
		self.toolbarSettings.addAction(actionToggleFullScreen)

		# Help toolbar 
		self.toolbarAbout = QToolBar("toolbarAbout")
		self.toolbarAbout.setObjectName("toolbarAbout")
		self.toolbarAbout.setIconSize(QSize(36,36))
		self.toolbarAbout.addAction(actionAbout)
		self.toolbarAbout.addAction(actionHelp)

		# put find dialog above editor
		self.editorTop =  QWidget()
		self.editorTopL = QVBoxLayout()
		self.editorTopL.addWidget(self.fWidget, False)
		self.editorTopL.addWidget(self.editor, True)
		self.editorTop.setLayout(self.editorTopL)
		self.editorTopL.setMargin(0)
		
		# frame for viewer
		# editor (QWebView) is inside viewerBox 
		self.viewerFrame = QFrame()
		self.viewerFrame.setFrameStyle(QFrame.WinPanel | QFrame.Sunken)
		self.viewerBox = QHBoxLayout()
		self.viewerBox.setMargin(0)
		self.viewerBox.addWidget(self.viewer)
		self.viewerFrame.setLayout(self.viewerBox)
		
		# splitter 
		self.splitter1 = QSplitter(Qt.Horizontal)
		self.splitter1.setHandleWidth(1)
		self.splitter2 = QSplitter(Qt.Horizontal)
		self.splitter2.setHandleWidth(1)
		
		# add widgets 
		self.splitter1.addWidget(self.editorTop)
		self.splitter1.addWidget(self.viewerFrame)
		self.splitter2.addWidget(self.browser)
		self.splitter2.addWidget(self.splitter1)
		
		# pack toolbars 
		self.mainToolbar = QTabWidget()
		self.mainToolbar.addTab(self.toolbarFile, QIcon(":icons/icon_file.png"), "File")
		self.mainToolbar.addTab(self.toolbarEdit, QIcon(":icons/icon_edit.png"), "Edit")
		self.mainToolbar.addTab(self.toolbarFormat, QIcon(":icons/icon_format.png"), "Format")
		self.mainToolbar.addTab(self.toolbarSettings, QIcon(":icons/icon_settings.png"), "Settings")
		self.mainToolbar.addTab(self.toolbarAbout, QIcon(":icons/icon_help.png"), "About asdf...")
		self.mainToolbar.tabBar().setDrawBase(False)
		self.mainToolbar.setStyleSheet("QTabBar::tab{width: 100px;} QTabWidget::pane { border: 0px solid; border-top: 1px solid #aaaaaa;}")
		QShortcut(QKeySequence("Alt+1", 0), self, self.focusToolbarFile)
		QShortcut(QKeySequence("Alt+2", 0), self, self.focusToolbarEdit)
		QShortcut(QKeySequence("Alt+3", 0), self, self.focusToolbarFormat)
		QShortcut(QKeySequence("Alt+4", 0), self, self.focusToolbarSettings)
		QShortcut(QKeySequence("Alt+5", 0), self, self.focusToolbarAbout)

		# top widget 
		self.topLayout = QVBoxLayout()
		self.topLayout.addWidget(self.mainToolbar, False)
		self.topLayout.addWidget(self.splitter2, True)
		self.topLayout.setMargin(0)
		self.topLayout.setSpacing(0)
		self.topWidget = QWidget()
		self.topWidget.setLayout(self.topLayout)
		self.setCentralWidget(self.topWidget)

		# toolbar settings
		self.toolbarFormat.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)		
		self.toolbarSettings.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)		
		self.toolbarEdit.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)		
		self.toolbarFile.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
		self.toolbarAbout.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

		# adjust viewer and editor width
		self.splitter1.setSizes([250,250])
		
		# set focus
		self.editor.setFocus()

	def initShortcuts(self):
		pass  

	def refreshView(self):
		if (self.markupEnabled): # Markdown mode
			strMarkdown = markdown.markdown(self.editor.toPlainText())
			self.viewer.setHtml(self.strHtmlTemplate.format(strMarkdown, self.viewerStyle))
			# print(self.strHtmlTemplate.format(strMarkdown, self.viewerStyle))
		else: # Plaintext mode
			strMarkdown = markdown.markdown(self.editor.toPlainText())
			dic = [
				("&","&amp"), 
				("\"","&quot"),
				("\'","&#039"),
				("<","&lt;"),
				(">","&gt;"),
			]
			for i,j in dic:
				strMarkdown = strMarkdown.replace(i,j)
			self.viewer.setHtml(strMarkdown)

	def hideToolbar(self):
		if (self.hideMode):
			self.hideMode = False
			self.browser.show()
			self.mainToolbar.setMaximumSize(65535,65535)
			self.mainToolbar.setMaximumSize(65535,65535)
		else:
			self.hideMode = True
			self.browser.hide()
			self.mainToolbar.setMaximumSize(0,0)
			self.mainToolbar.setMaximumSize(0,0)

	# function for toggling full screen
	def toggleFullScreen(self):
		if self.isFullScreen():
			self.showNormal()
		else:
			self.showFullScreen()

	def confirmSave(self):
		if (self.editor.document().isModified()):
			returnVal = QMessageBox.question(self, 
					"Your document has been modified.", 
					"Do you want to save your changes?", 
					QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, 
					QMessageBox.Save)
			if returnVal == QMessageBox.Save:
				self.saveFile()
				return True
			elif returnVal == QMessageBox.Discard:
				return True
			elif returnVal == QMessageBox.Cancel:
				return False
		else:
			return True

	def importCSS(self):
		# open file 		
		filePath = QFileDialog.getOpenFileName(self, "Open", ".", "CSS file (*.css)");
		if (filePath == "" or filePath == None):
			return
		self.currentFilePath = filePath
		# read input file 		
		f = codecs.open(self.currentFilePath, encoding="utf-8", mode="r")
		strStyleInput = f.read()	
		f.close()
		# write it to style 
		cssSettings = QSettings();
		cssSettings.setValue("cssState", strStyleInput)
		self.viewerStyle = strStyleInput
		self.refreshView()

	def newFile(self):
		if (self.confirmSave()):
			self.currentFilePath = "Untitled.md"
			self.editor.setPlainText("")
			self.setWindowTitle(os.path.basename(self.currentFilePath) + " - asdf")
		else:
			return

	def saveFile(self):					
		if (self.currentFilePath == "Untitled.md" or self.currentFilePath == None):
			filePath = QFileDialog.getSaveFileName(self, "Save", ".", "Markdown file (*.md)")	
			if (filePath == "" or filePath == None):
				return
			self.currentFilePath = filePath
		data = self.editor.toPlainText()
		f = codecs.open(self.currentFilePath, encoding="utf-8", mode="w")
		f.write(data)
		f.close()
			

	def saveAsFile(self):
		filePath = QFileDialog.getSaveFileName(self, "Save", ".", "Markdown file (*.md)")	
		if (filePath == "" or filePath == None):
			return
		self.currentFilePath = filePath
		data = self.editor.toPlainText()
		f = codecs.open(self.currentFilePath, encoding="utf-8", mode="w")
		f.write(data)
		f.close()

	def openFile(self):
		if (self.confirmSave()):
			# self.curentFilePath = "Untitled.md"
			# self.editor.setPlainText("")
			filePath = QFileDialog.getOpenFileName(self, "Open", ".");
			if (filePath == "" or filePath == None):
				return
			self.currentFilePath = filePath
			f = codecs.open(self.currentFilePath, encoding="utf-8", mode="r")
			self.editor.setPlainText(f.read())	
			f.close()
			self.setWindowTitle(os.path.basename(self.currentFilePath) + " - asdf")
		else:
			return
	
	def changeFont(self):
		(f, ok) = QFontDialog.getFont(self.editor.currentCharFormat().font(), self, "Select Font")
		if (ok):
			cf = QTextCharFormat()
			cf.setFont(f)
			self.editor.setCurrentCharFormat(cf)

	def viewVertical(self):
		self.splitter1.setOrientation(Qt.Horizontal)

	def viewHorizontal(self):
		self.splitter1.setOrientation(Qt.Vertical)

	def editBold(self):
		c = self.editor.textCursor()
		if (c.hasSelection()):
			cPos = c.position()
			text = c.selectedText()	
			matchResult = re.match("\*\**\*\*", text)
			if (matchResult == None):
				c.insertText("**" + text + "**")
			else:
				c.removeSelectedText()
				c.insertText(text[2:-2])

	def editItalic(self):
		c = self.editor.textCursor()
		if (c.hasSelection()):
			cPos = c.position()
			text = c.selectedText()	
			matchResult = re.match("_[^_]*[^_]_", text)
			if (matchResult == None):
				c.insertText("_" + text + "_")
			else:
				c.removeSelectedText()
				c.insertText(text[1:-1])

	def editUnderline(self):
		self.editor.setFontUnderline(not self.editor.fontUnderline())
	
	# def editRemoveFormat(self):
	#	pass

	def editH1(self): self.editH_(1)
	def editH2(self): self.editH_(2)
	def editH3(self): self.editH_(3)
	def editH4(self): self.editH_(4)
	def editH5(self): self.editH_(5)
	def editH6(self): self.editH_(6)

	def editH_(self, sz):
		if (sz == 1 or sz == 2):
			# Get size of line
			cStart 	= QTextCursor(self.editor.textCursor())
			cEnd 	= QTextCursor(cStart)
			cStart.movePosition(QTextCursor.StartOfLine)
			cEnd.movePosition(QTextCursor.EndOfLine)
			lineWidth = cEnd.position() - cStart.position() 
			# Markdown symbol
			if (sz == 1):
				strMd = '\n' + '=' * lineWidth;
			if (sz == 2):
				strMd = '\n' + '-' * lineWidth;
			# insert text 
			cEnd.insertText(strMd)
		else:
			# get the start of line 
			cStart 	= QTextCursor(self.editor.textCursor())
			cStart.movePosition(QTextCursor.StartOfLine)
			# insert markdown
			cStart.insertText('#' * sz)

	def focusToolbarFile(self): 
		self.mainToolbar.setCurrentWidget(self.toolbarFile)
	def focusToolbarEdit(self): 
		self.mainToolbar.setCurrentWidget(self.toolbarEdit)
	def focusToolbarFormat(self): 
		self.mainToolbar.setCurrentWidget(self.toolbarFormat)
	def focusToolbarSettings(self): 
		self.mainToolbar.setCurrentWidget(self.toolbarSettings)
	def focusToolbarAbout(self): 
		self.mainToolbar.setCurrentWidget(self.toolbarAbout)


	def editBlist(self):
		# get the start of line 
		cStart 	= QTextCursor(self.editor.textCursor())
		cStart.movePosition(QTextCursor.StartOfLine)
		# insert markdown
		cStart.insertText('- ')
		pass
	
	def editNlist(self):
		# get the start of line 
		cStart 	= QTextCursor(self.editor.textCursor())
		cStart.movePosition(QTextCursor.StartOfLine)
		# insert markdown
		cStart.insertText('%d. ' % self.NlistCount)
		self.NlistCount = self.NlistCount + 1
		pass
	
	def insertImage(self):
		self.editor.textCursor().insertText("![ALT](PATH)")
		pass
	
	def insertLink(self):
		self.editor.textCursor().insertText("[TEXT](URL)")
		pass

	def exportHtml(self):
		filePath = QFileDialog.getSaveFileName(self, "Export as HTML", ".", "HTML file (*.html)")	
		if (filePath == "" or filePath == None):
			return
		self.refreshView() 			# refresh the final view
		data = self.toHtml()		# convert to Html
		f = codecs.open(filePath, encoding="utf-8", mode="w")
		f.write(data)
		f.close()

	def exportTex(self):
		# to be implemented 	
		pass

	def exportPdf(self):
		filePath = QFileDialog.getSaveFileName(self, "Export as PDF", ".", "PDF file (*.pdf)")	
		if (filePath == "" or filePath == None):
			return
		tempEdit = QTextEdit()
		tempEdit.zoomIn(5)
		self.refreshView()
		tempEdit.setHtml(self.viewer.page().currentFrame().toHtml())
		self.pdfPrinter.setOutputFileName(filePath)
		tempEdit.print_(self.pdfPrinter)

	def emailHtml(self):
		pass

	def browserSelected(self, path):
		fname, fext = os.path.splitext(path)
		openable =[".md", ".htm",".css",".txt",".html",".py"]
		openable = openable + [x.upper() for x in openable];
		if (fext in openable):
			if (self.confirmSave()):
				self.currentFilePath = path
				f = codecs.open(self.currentFilePath, encoding="utf-8", mode="r")
				self.editor.setPlainText(f.read())	
				f.close()
				self.setWindowTitle(os.path.basename(self.currentFilePath) + " - asdf")
		else:	
			# else use default app
			self.openFileDefaultApp(path)

	def openFileDefaultApp(self, filePath):
		if sys.platform.startswith('darwin'):
			subprocess.call(('open', filePath))
		elif os.name == 'nt':
			os.startfile(filePath)
		elif os.name == 'posix':
			subprocess.call(('xdg-open', filePath))

	def findText(self):
		if self.fWidget.isHidden():
			self.fWidget.show()
		else:
			self.fWidget.hide()

	def toggleHighlight(self):
		if self.highlight.enabled:
			self.highlight.enabled = False;
		else:
			self.highlight.enabled = True;
		self.highlight.rehighlight()

	def togglePlainText(self):
		self.markupEnabled = not self.markupEnabled
		self.refreshView()

	def showHelp(self):
		if (self.helpDialog.isHidden()):
			self.helpDialog.show()
		else:
			self.helpDialog.hide()

	def showAbout(self):
		if (self.aboutDialog.isHidden()):
			self.aboutDialog.show()
		else:
			self.aboutDialog.hide()

if __name__ == "__main__":

	asdfApp = QApplication(sys.argv)
	asdfApp.setWindowIcon(QIcon(":icons/icon_asdf.png"))
	asdfInstance = ASDF(sys.argv)
	sys.exit(asdfApp.exec_())

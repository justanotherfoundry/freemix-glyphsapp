# encoding: utf-8

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
import operator
from AppKit import NSPoint

MIN_NUMBER_OF_LINES = 4
MAX_NUMBER_OF_LINES = 10
VERTICAL_MARGIN = 6

class ComponentsPalette (PalettePlugin):
	
	dialog = objc.IBOutlet()
	label0 = objc.IBOutlet()
	label1 = objc.IBOutlet()
	label2 = objc.IBOutlet()
	label3 = objc.IBOutlet()
	label4 = objc.IBOutlet()
	label5 = objc.IBOutlet()
	label6 = objc.IBOutlet()
	label7 = objc.IBOutlet()
	label8 = objc.IBOutlet()
	label9 = objc.IBOutlet()
	posx0 = objc.IBOutlet()
	posx1 = objc.IBOutlet()
	posx2 = objc.IBOutlet()
	posx3 = objc.IBOutlet()
	posx4 = objc.IBOutlet()
	posx5 = objc.IBOutlet()
	posx6 = objc.IBOutlet()
	posx7 = objc.IBOutlet()
	posx8 = objc.IBOutlet()
	posx9 = objc.IBOutlet()
	posy0 = objc.IBOutlet()
	posy1 = objc.IBOutlet()
	posy2 = objc.IBOutlet()
	posy3 = objc.IBOutlet()
	posy4 = objc.IBOutlet()
	posy5 = objc.IBOutlet()
	posy6 = objc.IBOutlet()
	posy7 = objc.IBOutlet()
	posy8 = objc.IBOutlet()
	posy9 = objc.IBOutlet()
	heightConstrains = objc.IBOutlet()
	allFieldsHidden = False
	font = None
	
	# seems to be called whenever a new font is opened
	# careful! not called when the user switches to a different, already opened font
	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({'en': u'Components'})
		self.loadNib('ComponentsPaletteView', __file__)
		self.lineheight = self.posx0.frame().origin.y - self.posx1.frame().origin.y
		self.posxFieldsOriginX = self.posx0.frame().origin.x

	@objc.IBAction
	def editTextCallback_(self, textField):
		try:
			newValue = float(textField.stringValue())
		except ValueError:
			self.update()
			return
		for layer in self.font.selectedLayers:
			try:
				component = layer.components[textField.tag()]
			except IndexError:
				continue
			if textField.frame().origin.x == self.posxFieldsOriginX:
				component.position = NSPoint(newValue, component.position.y)
			else:
				component.position = NSPoint(component.position.x, newValue)

	@objc.python_method
	def update(self, sender=None):
		collapsed = (self.dialog.frame().origin.y != 0)
		if collapsed:
			# do not update in case the palette is collapsed:
			return
		if sender:
			self.font = sender.object()
		if not self.font:
			return
		self.allFieldsHidden = False
		visibleLinesCount = 0
		for i in range(MAX_NUMBER_OF_LINES):
			x = None
			y = None
			if not self.font.selectedLayers:
				# this also catches None, which Glyphs may return
				pass
			elif (len(self.font.selectedLayers)) == 1:
				layer = self.font.selectedLayers[0]
				try:
					component = layer.components[i]
					x = component.position.x
					y = component.position.y
					getattr(self, 'label' + str(i)).setStringValue_(component.name)
				except IndexError:
					pass
			else:
				getattr(self, 'label' + str(i)).setStringValue_(str(i + 1))
				for layer in self.font.selectedLayers:
					try:
						component = layer.components[i]
					except IndexError:
						continue
					if x == None:
						x = component.position.x
					elif x != round(component.position.x, 3):
						x = ''
					if y == None:
						y = component.position.y
					elif y != round(component.position.y, 3):
						y = ''
			assert((x is None) == (y is None))
			if x is None:
				getattr(self, 'label' + str(i)).setStringValue_('')
				getattr(self, 'posx' + str(i)).setHidden_(True)
				getattr(self, 'posy' + str(i)).setHidden_(True)
				continue
			getattr(self, 'posx' + str(i)).setHidden_(False)
			getattr(self, 'posy' + str(i)).setHidden_(False)
			if x == '':
				getattr(self, 'posx' + str(i)).setStringValue_('')
			else:
				getattr(self, 'posx' + str(i)).setIntValue_(int(x))
			if y == '':
				getattr(self, 'posy' + str(i)).setStringValue_('')
			else:
				getattr(self, 'posy' + str(i)).setIntValue_(int(y))
			visibleLinesCount = i + 1
		height = VERTICAL_MARGIN + visibleLinesCount * self.lineheight
		# we are never reducing the height of the palette
		# so as to minimize the changes (frequent height change
		# would be very distracting as we step through glyphs
		# in edit view)
		if height > self.heightConstrains.constant():
			self.heightConstrains.setConstant_(height)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# the following methods are adopted from the SDK without any changes

	@objc.python_method
	def start(self):
		# Adding a callback for the 'GSUpdateInterface' event
		Glyphs.addCallback(self.update, UPDATEINTERFACE)
	
	@objc.python_method
	def __del__(self):
		Glyphs.removeCallback(self.update)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
	
	# Temporary Fix
	# Sort ID for compatibility with v919:
	_sortID = 0
	@objc.python_method
	def setSortID_(self, id):
		try:
			self._sortID = id
		except Exception as e:
			self.logToConsole("setSortID_: %s" % str(e))
	
	@objc.python_method
	def sortID(self):
		return self._sortID
	
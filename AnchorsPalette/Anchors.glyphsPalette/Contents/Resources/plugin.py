# encoding: utf-8

import objc
from GlyphsApp import Glyphs, UPDATEINTERFACE
from GlyphsApp.plugins import PalettePlugin
from AppKit import (
	NSView, NSScrollView, NSTextField, NSFont, NSNumberFormatter, NSMakeRect,
	NSViewWidthSizable, NSViewHeightSizable, NSViewMinXMargin,
	NSNoBorder, NSTextAlignmentRight, NSLineBreakByTruncatingTail,
	NSControlSizeSmall, NSTextFieldSquareBezel,
)
import operator

# the palette height (in lines) can be changed by the user
# by dragging the bottom edge of the palette:
MIN_NUMBER_OF_LINES = 3
DEFAULT_NUMBER_OF_LINES = 6
MAX_NUMBER_OF_LINES = 40

LINE_HEIGHT = 21
VERTICAL_MARGIN = 6
DEFAULT_WIDTH = 165

LABEL_LEFT = 12
LABEL_HEIGHT = 14
LABEL_OFFSET_Y = 4
FIELD_WIDTH = 38
FIELD_HEIGHT = 19
FIELD_GAP = 2
FIELD_RIGHT_MARGIN = 20

HEIGHT_DEFAULTS_KEY = 'com.justanotherfoundry.AnchorsPalette.height'

try:
	GSSteppingTextField = objc.lookUpClass('GSSteppingTextField')
except objc.nosuchclass_error:
	GSSteppingTextField = NSTextField

# Glyphs asks the controller of a GSPaletteView whether the palette is resizable
# (minHeight/maxHeight) and calls setCurrentHeight: when the user drags it
try:
	GSPaletteView = objc.lookUpClass('GSPaletteView')
except objc.nosuchclass_error:
	GSPaletteView = NSView

# a flipped view so that the anchor list starts at the top
# (and short lists stick to the top of the scroll view)
try:
	AnchorsPaletteListView = objc.lookUpClass('AnchorsPaletteListView')
except objc.nosuchclass_error:
	class AnchorsPaletteListView (NSView):
		def isFlipped(self):
			return True

def heightForLines(lines):
	return VERTICAL_MARGIN + lines * LINE_HEIGHT

class AnchorsPalette (PalettePlugin):

	# note: self.dialog is created in code, so it must not be declared
	# as an objc.IBOutlet() (that would not retain the view)
	font = None

	# seems to be called whenever a new font is opened
	# careful! not called when the user switches to a different, already opened font
	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({
			'en': 'Anchors',
			'de': 'Anker',
		})
		self.anchorNames = []
		self.rows = []
		height = self.currentHeight()
		self.dialog = GSPaletteView.alloc().initWithFrame_(NSMakeRect(0, 0, DEFAULT_WIDTH, height))
		if self.dialog.respondsToSelector_('setController:'):
			self.dialog.setController_(self)
		# the palette sidebar uses auto layout; the height is driven by this constraint:
		self.dialog.setTranslatesAutoresizingMaskIntoConstraints_(False)
		self.heightConstraint = self.dialog.heightAnchor().constraintEqualToConstant_(height)
		self.heightConstraint.setActive_(True)
		self.scrollView = NSScrollView.alloc().initWithFrame_(self.dialog.bounds())
		self.scrollView.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
		self.scrollView.setHasVerticalScroller_(True)
		self.scrollView.setHasHorizontalScroller_(False)
		self.scrollView.setAutohidesScrollers_(True)
		self.scrollView.setBorderType_(NSNoBorder)
		self.scrollView.setDrawsBackground_(False)
		self.listView = AnchorsPaletteListView.alloc().initWithFrame_(NSMakeRect(0, 0, self.scrollView.contentSize().width, height))
		self.listView.setAutoresizingMask_(NSViewWidthSizable)
		self.scrollView.setDocumentView_(self.listView)
		self.dialog.addSubview_(self.scrollView)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# resizing (see PalettePlugin in the Glyphs SDK)

	def minHeight(self):
		return heightForLines(MIN_NUMBER_OF_LINES)

	def maxHeight(self):
		return heightForLines(MAX_NUMBER_OF_LINES)

	def currentHeight(self):
		height = Glyphs.defaults[HEIGHT_DEFAULTS_KEY]
		if height is None:
			return heightForLines(DEFAULT_NUMBER_OF_LINES)
		return max(self.minHeight(), min(self.maxHeight(), int(height)))

	def setCurrentHeight_(self, newHeight):
		newHeight = max(self.minHeight(), min(self.maxHeight(), int(newHeight)))
		Glyphs.defaults[HEIGHT_DEFAULTS_KEY] = newHeight
		self.heightConstraint.setConstant_(newHeight)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# the anchor rows (created on demand, so there is no limit to the number of anchors)

	@objc.python_method
	def makeTextField(self, frame, placeholder, action, tag):
		field = GSSteppingTextField.alloc().initWithFrame_(frame)
		field.setAutoresizingMask_(NSViewMinXMargin)
		field.cell().setControlSize_(NSControlSizeSmall)
		field.setFont_(NSFont.systemFontOfSize_(NSFont.smallSystemFontSize()))
		field.setBezeled_(True)
		field.setBezelStyle_(NSTextFieldSquareBezel)
		field.setEditable_(True)
		field.setSelectable_(True)
		field.setAlignment_(NSTextAlignmentRight)
		field.setPlaceholderString_(placeholder)
		field.cell().setScrollable_(True)
		field.cell().setSendsActionOnEndEditing_(True)
		formatter = NSNumberFormatter.alloc().init()
		formatter.setUsesGroupingSeparator_(False)
		formatter.setLenient_(True)
		formatter.setMinimumIntegerDigits_(1)
		formatter.setMaximumFractionDigits_(1)
		field.setFormatter_(formatter)
		field.setTag_(tag)
		field.setTarget_(self)
		field.setAction_(action)
		return field

	@objc.python_method
	def addRow(self):
		i = len(self.rows)
		top = i * LINE_HEIGHT
		width = self.listView.frame().size.width
		posyLeft = width - FIELD_RIGHT_MARGIN - FIELD_WIDTH
		posxLeft = posyLeft - FIELD_GAP - FIELD_WIDTH
		label = NSTextField.labelWithString_('')
		label.setFrame_(NSMakeRect(LABEL_LEFT, top + LABEL_OFFSET_Y, posxLeft - 6 - LABEL_LEFT, LABEL_HEIGHT))
		label.setAutoresizingMask_(NSViewWidthSizable)
		label.setFont_(NSFont.systemFontOfSize_(NSFont.smallSystemFontSize()))
		label.setLineBreakMode_(NSLineBreakByTruncatingTail)
		posx = self.makeTextField(NSMakeRect(posxLeft, top, FIELD_WIDTH, FIELD_HEIGHT), 'x', 'editTextCallbackX:', i)
		posy = self.makeTextField(NSMakeRect(posyLeft, top, FIELD_WIDTH, FIELD_HEIGHT), 'y', 'editTextCallbackY:', i)
		for view in (label, posx, posy):
			self.listView.addSubview_(view)
		self.rows.append((label, posx, posy))

	@objc.python_method
	def setNumberOfRows(self, count):
		while len(self.rows) < count:
			self.addRow()
		for i, row in enumerate(self.rows):
			for view in row:
				view.setHidden_(i >= count)
		frame = self.listView.frame()
		frame.size.height = heightForLines(count)
		self.listView.setFrame_(frame)

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	@objc.IBAction
	def editTextCallbackX_(self, textField):
		self.editTextCallback(textField, "X")
	@objc.IBAction
	def editTextCallbackY_(self, textField):
		self.editTextCallback(textField, "Y")

	@objc.python_method
	def editTextCallback(self, textField, key):
		try:
			newValue = float( textField.stringValue() )
		except ValueError:
			self.update()
			return
		if self.font is None:
			return
		anchorName = self.anchorNames[textField.tag()]
		for layer in self.font.selectedLayers:
			anchor = layer.anchors[anchorName]
			if anchor is None:
				continue
			if key == "X":
				anchor.x = newValue
			else:
				anchor.y = newValue

	@objc.python_method
	def update( self, sender=None ):
		collapsed = ( self.dialog.frame().origin.y < 0 )
		if collapsed:
			# do not update in case the palette is collapsed:
			return
		if sender:
			self.font = sender.object()
		if not self.font:
			return
		anchorStats = {}
		if self.font.selectedLayers:
			for layer in self.font.selectedLayers:
				for anchor in layer.anchors:
					if anchor.name not in anchorStats:
						anchorStats[anchor.name] = [0, 0]
					anchorStats[anchor.name][0] += 1
					anchorStats[anchor.name][1] += anchor.position.y
		# sort by average y position:
		anchorStats = sorted( [(name, stat[1]/stat[0]) for name, stat in anchorStats.items()], key=operator.itemgetter(1), reverse=True )
		self.anchorNames = [name for name, _ in anchorStats]
		self.setNumberOfRows( len( self.anchorNames ) )
		for anchorName, (label, posx, posy) in zip( self.anchorNames, self.rows ):
			label.setStringValue_( anchorName )
			x = None
			y = None
			for layer in self.font.selectedLayers:
				anchor = layer.anchors[anchorName]
				if anchor is None:
					continue
				if x is None:
					x = anchor.position.x
					if x == round( x, 3 ):
						x = int( x )
				elif x != round( anchor.position.x, 3 ):
					x = ''
				if y is None:
					y = anchor.position.y
					if y == round( y, 3 ):
						y = int( y )
				elif y != round( anchor.position.y, 3 ):
					y = ''
			if x == '':
				posx.setStringValue_( '' )
			else:
				posx.setIntValue_( x )
			if y == '':
				posy.setStringValue_( '' )
			else:
				posy.setIntValue_( y )

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
			self.logToConsole( "setSortID_: %s" % str(e) )

	@objc.python_method
	def sortID(self):
		return self._sortID

# encoding: utf-8

import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
import operator
from AppKit import NSPoint

MIN_NUMBER_OF_LINES = 4
MAX_NUMBER_OF_LINES = 10
VERTICAL_MARGIN = 6

class AnchorsPalette (PalettePlugin):
	
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
	
	# seems to be called whenever a new font is opened
	# careful! not called when the user switches to a different, already opened font
	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({'en': u'Anchors'})
		self.loadNib( 'AnchorsPaletteView', __file__ )
		self.lineheight = self.posx0.frame().origin.y - self.posx1.frame().origin.y
		self.posxFieldsOriginX = self.posx0.frame().origin.x

	@objc.IBAction
	def editTextCallback_(self, textField):
		try:
			newValue = float( textField.stringValue() )
		except ValueError:
			self.update()
			return
		anchorName = self.anchorNames[textField.tag()]
		for layer in self.font.selectedLayers:
			for anchor in layer.anchors:
				if anchor.name == anchorName:
					if textField.frame().origin.x == self.posxFieldsOriginX:
						layer.anchors[anchorName].position = NSPoint( newValue, layer.anchors[anchorName].position.y )
					else:
						layer.anchors[anchorName].position = NSPoint( layer.anchors[anchorName].position.x, newValue )
					break

	@objc.python_method
	def update( self, sender=None ):
		collapsed = ( self.dialog.frame().origin.y != 0 )
		if collapsed and self.allFieldsHidden:
			# do not update in case the palette is collapsed:
			return
		if sender:
			self.font = sender.object()
		if not self.font:
			return
		if not collapsed:
			anchorStats = {}
			if self.font.selectedLayers:
				for layer in self.font.selectedLayers:
					for anchor in layer.anchors:
						if anchor.name not in anchorStats:
							anchorStats[anchor.name] = [0, 0]
						anchorStats[anchor.name][0] += 1
						anchorStats[anchor.name][1] += anchor.position.y
			# convert to a list, sorted by number of anchors:
			anchorStats = sorted( anchorStats.items(), key=operator.itemgetter(1), reverse=True )
			# trim to max MAX_NUMBER_OF_LINES elements:
			del anchorStats[MAX_NUMBER_OF_LINES:]
			# sort by average y position:
			anchorStats = sorted( [(name, stat[1]/stat[0]) for name, stat in anchorStats], key=operator.itemgetter(1), reverse=True )
			self.anchorNames = []
			self.allFieldsHidden = False
		else:
			anchorStats = []
		for i in range( MAX_NUMBER_OF_LINES ):
			try:
				anchorName = anchorStats[i][0]
			except IndexError:
				getattr( self, 'label' + str( i ) ).setStringValue_( '' )
				getattr( self, 'posx' + str( i ) ).setHidden_( True )
				getattr( self, 'posy' + str( i ) ).setHidden_( True )
				continue
			getattr( self, 'posx' + str( i ) ).setHidden_( False )
			getattr( self, 'posy' + str( i ) ).setHidden_( False )
			getattr( self, 'label' + str( i ) ).setStringValue_( anchorName )
			x = None
			y = None
			for layer in self.font.selectedLayers:
				for anchor in layer.anchors:
					if anchor.name == anchorName:
						if x == None:
							x = anchor.position.x
							if x == round( x, 3 ):
								x = int( x )
						elif x != round( anchor.position.x, 3 ):
							x = ''
						if y == None:
							y = anchor.position.y
							if y == round( y, 3 ):
								y = int( y )
						elif y != round( anchor.position.y, 3 ):
							y = ''
			if x == '':
				getattr( self, 'posx' + str( i ) ).setStringValue_( '' )
			else:
				getattr( self, 'posx' + str( i ) ).setIntValue_( x )
			if y == '':
				getattr( self, 'posy' + str( i ) ).setStringValue_( '' )
			else:
				getattr( self, 'posy' + str( i ) ).setIntValue_( y )
			self.anchorNames.append( anchorName )
		if collapsed:
			height = VERTICAL_MARGIN + MIN_NUMBER_OF_LINES * self.lineheight
			self.heightConstrains.setConstant_( height )
			self.allFieldsHidden = True
			return
		lines = max( MIN_NUMBER_OF_LINES, len( anchorStats ) )
		height = VERTICAL_MARGIN + lines * self.lineheight
		# we are never reducing the height of the palette
		# so as to minimize the changes (frequent height change
		# would be very distracting as we step through glyphs
		# in edit view)
		if height > self.heightConstrains.constant():
			self.heightConstrains.setConstant_( height )

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
	
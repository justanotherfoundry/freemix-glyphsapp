# encoding: utf-8

###########################################################################################################
#
#
#	Palette Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Palette
#
#
###########################################################################################################

from GlyphsApp import *
from GlyphsApp.plugins import *
import operator

MIN_NUMBER_OF_LINES = 4
MAX_NUMBER_OF_LINES = 10
VERTICAL_MARGIN = 5

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

	def start(self):
		# Adding a callback for the 'GSUpdateInterface' event
		Glyphs.addCallback(self.update, UPDATEINTERFACE)
	
	def __del__(self):
		Glyphs.removeCallback(self.update)

	def update( self, sender=None ):
		if sender:
			self.font = sender.object()
		if not self.font:
			return
		anchorsNumber = {}
		if self.font.selectedLayers:
			for layer in self.font.selectedLayers:
				for anchor in layer.anchors:
					if anchorsNumber.has_key( anchor.name ):
						anchorsNumber[anchor.name] += 1
					else:
						anchorsNumber[anchor.name] = 1
		anchorsNumber = sorted( anchorsNumber.items(), key=operator.itemgetter(1), reverse=True )
		# trim to max MAX_NUMBER_OF_LINES elements
		del anchorsNumber[MAX_NUMBER_OF_LINES:]
		self.anchorNames = []
		for i in xrange( MAX_NUMBER_OF_LINES ):
			try:
				anchorName, number = anchorsNumber[i]
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
		lines = max( MIN_NUMBER_OF_LINES, len( anchorsNumber ) )
		height = VERTICAL_MARGIN + lines * self.lineheight
		# we are never reducing the height of the palette
		# so as to minimize the changes (frequent height change
		# would be very distracting as we step through glyphs
		# in edit view)
		if height > self.heightConstrains.constant():
			self.heightConstrains.setConstant_( height )

	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
	
	# Temporary Fix
	# Sort ID for compatibility with v919:
	def setSortID_(self, id):
		pass
	def sortID(self):
		return 1000

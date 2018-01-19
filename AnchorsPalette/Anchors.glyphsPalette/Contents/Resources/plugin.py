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
from vanilla import *
import operator

class AnchorsPalette (PalettePlugin):
	
	# dialog = objc.IBOutlet()
	# textField = objc.IBOutlet()

	def settings(self):
		self.name = Glyphs.localize({'en': u'Anchors'})
		
		# Create Vanilla window and group with controls
		width = 150
		height = 80
		self.paletteView = Window( (width, height), minSize=(width, height - 10), maxSize=(width, height + 200 ) )
		self.paletteView.group = Group( (0, 0, width, height ) )

		self.marginTop = 5
		self.lineSpacing = 18
		textFieldHeight = 15
		textFieldWidth = 34
		self.posx_xTextField = width - 2 * textFieldWidth - 5
		self.posx_yTextField = self.posx_xTextField + textFieldWidth + 4
		for i in xrange( 4 ):
			posy = self.lineSpacing * i + self.marginTop
			setattr( self.paletteView.group, 'txt' + str( i ), TextBox( ( 10, posy, 80, 18 ), 'anchornamsdfsdfs fd d', sizeStyle='mini' ) )
			setattr( self.paletteView.group, 'posx' + str( i ), EditText( ( self.posx_xTextField, posy, textFieldWidth, textFieldHeight ), callback=self.editTextCallback, continuous=False, readOnly=False, formatter=None, placeholder='x', sizeStyle='mini' ) )
			setattr( self.paletteView.group, 'posy' + str( i ), EditText( ( self.posx_yTextField, posy, textFieldWidth, textFieldHeight ), callback=self.editTextCallback, continuous=False, readOnly=False, formatter=None, placeholder='y', sizeStyle='mini' ) )
		# Set dialog to NSView
		self.dialog = self.paletteView.group.getNSView()

	def editTextCallback(self, editText):
		xPos, yPos, wd, ht = editText.getPosSize()
		index = ( yPos - self.marginTop ) / self.lineSpacing
		anchorName = self.anchorNames[index]
		try:
			newValue = float( editText.get() )
		except ValueError:
			self.update()
			return
		for layer in self.font.selectedLayers:
			for anchor in layer.anchors:
				if anchor.name == anchorName:
					if xPos == self.posx_xTextField:
						layer.anchors[anchorName].position = NSPoint( newValue, layer.anchors[anchorName].position.y )
					else:
						layer.anchors[anchorName].position = NSPoint( layer.anchors[anchorName].position.x, newValue )


	def start(self):
		# Adding a callback for the 'GSUpdateInterface' event
		Glyphs.addCallback(self.update, UPDATEINTERFACE)
	
	def __del__(self):
		Glyphs.removeCallback(self.update)

	def update( self, sender=None ):
		if sender:
			self.font = sender.object()
		anchorsNumber = {}

		if self.font.selectedLayers:
			for layer in self.font.selectedLayers:
				for anchor in layer.anchors:
					if anchorsNumber.has_key( anchor.name ):
						anchorsNumber[anchor.name] += 1
					else:
						anchorsNumber[anchor.name] = 1
		anchorsNumber = sorted( anchorsNumber.items(), key=operator.itemgetter(1), reverse=True )
		# trim to max 4 elements
		del anchorsNumber[4:]
		# anchorsNumber.sort()
		self.anchorNames = []
		for i in xrange( 4 ):
			try:
				anchorName, number = anchorsNumber[i]
				getattr( self.paletteView.group, 'txt' + str( i ) ).set( anchorName )
				getattr( self.paletteView.group, 'posx' + str( i ) ).show( True )
				getattr( self.paletteView.group, 'posy' + str( i ) ).show( True )
				x = None
				y = None
				multipleX = False
				multipleY = False
				for layer in self.font.selectedLayers:
					for anchor in layer.anchors:
						if anchor.name == anchorName:
							if x == None:
								x = anchor.position.x
								if x == round( x, 3 ):
									x = int( x )
							elif x != round( anchor.position.x, 3 ):
								multipleX = True
								x = ''
							if y == None:
								y = anchor.position.y
								if y == round( y, 3 ):
									y = int( y )
							elif y != round( anchor.position.y, 3 ):
								multipleY = True
								y = ''
				getattr( self.paletteView.group, 'posx' + str( i ) ).set( x )
				getattr( self.paletteView.group, 'posy' + str( i ) ).set( y )
				self.anchorNames.append( anchorName )
			except IndexError:
				getattr( self.paletteView.group, 'txt' + str( i ) ).set( '' )
				getattr( self.paletteView.group, 'posx' + str( i ) ).show( False )
				getattr( self.paletteView.group, 'posy' + str( i ) ).show( False )
	
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
	
	# Temporary Fix
	# Sort ID for compatibility with v919:
	_sortID = 0
	def setSortID_(self, id):
		try:
			self._sortID = id
		except Exception as e:
			self.logToConsole( "setSortID_: %s" % str(e) )
	def sortID(self):
		return self._sortID
	
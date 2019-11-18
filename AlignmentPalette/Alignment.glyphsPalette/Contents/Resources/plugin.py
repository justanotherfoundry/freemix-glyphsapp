# encoding: utf-8

from GlyphsApp.plugins import *
from vanilla import *
import operator
from GlyphsApp import UPDATEINTERFACE

# maximum number of zones to be diasplayed
# increase this value if you have more zones in your font
MAX_ZONES = 10

# if False, this deactivates the grid, i.e. allows fractional positioning
# to achieve exact centering
STICK_TO_GRID = False

# maximum number of glyphs
MAX_GLYPHS_COUNT = 100

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Glyphs constants
COUNTERCLOCKWISE = -1
CLOCKWISE = 1

# sets the center of the bounding box of a layer
def setCenterOfLayer( layer, newCenterX, newCenterY ):
	centerX, centerY = centerOfLayer( layer )
	try:
		shiftX = newCenterX - centerX
	except TypeError:
		shiftX = 0
	try:
		shiftY = newCenterY - centerY
	except TypeError:
		shiftY = 0
	layer.applyTransform( [ 1.0, 0.0, 0.0, 1.0, shiftX, shiftY ] )
	layer.syncMetrics()

# returns the center of the bounding box of a layer
def centerOfLayer( layer ):
	decomposedLayer = layer.copyDecomposedLayer()
	if not decomposedLayer.paths:
		return None, None
	# we have to manually determine the bounds since
	# Glyphs applies the grid when it returns layer.bounds
	left = right = decomposedLayer.paths[0].nodes[0].x
	top = bottom = decomposedLayer.paths[0].nodes[0].y
	for path in decomposedLayer.paths:
		for node in path.nodes:
			if node.y > top:
				top = node.y
			elif node.y < bottom:
				bottom = node.y
			if node.x > right:
				right = node.x
			elif node.x < left:
				left = node.x
	centerX = 0.5 * int( left + right )
	centerY = 0.5 * int( top + bottom )
	return centerX, centerY

# returns the center of the layers,
# x or y might be '' if they vary between layers
def centerOfLayers( layers ):
	globalCenterX = None
	globalCenterY = None
	for layer in layers:
		centerX, centerY = centerOfLayer( layer )
		if globalCenterX is None:
			globalCenterX = centerX
		elif globalCenterX != centerX:
			globalCenterX = ''
		if globalCenterY is None:
			globalCenterY = centerY
		elif globalCenterY != centerY:
			globalCenterY = ''
	return globalCenterX, globalCenterY

# returns a list of tuples with zone name, zone and height,
# sorted by height
def namedZones( layer ):
	font = layer.parent.parent
	masters = [m for m in font.masters if m.id == layer.associatedMasterId]
	if not masters:
		return []
	master = masters[0]
	topHeights = [ ('cap height', master.capHeight), ('ascender', master.ascender), ('x-height', master.xHeight) ]
	bottomHeights = [ ('baseline', 0), ('descender', master.descender) ]
	zones = []
	for zone in master.alignmentZones:
		if zone.size > 0:
			for name, y in topHeights:
				if y >= zone.position and y <= zone.position + zone.size:
					zones.append( ( name, zone, y ) )
					break
			else:
				zones.append( ( str(zone.position), zone, zone.position ) )
		elif zone.size < 0:
			for name, y in bottomHeights:
				if y <= zone.position and y >= zone.position + zone.size:
					zones.append( ( name, zone, y ) )
					break
			else:
				zones.append( ( str(zone.position), zone, zone.position ) )
	# sort by height
	zones.sort(key=lambda x: x[2], reverse = True )
	return zones

# returns a list of tuples (zone name, overshoot) for the layer
# overshoot may be None
def overshootsOfLayer( layer ):
	zones = namedZones( layer )
	overshoots = [ [ name, None ] for name, zone, height in zones ]
	for path in layer.copyDecomposedLayer().paths:
		if path.direction == CLOCKWISE or len( path.nodes ) < 2:
			continue
		node2 = path.nodes[-2]
		node3 = path.nodes[-1]
		if not node2 or not node3:
			# this can happen with open paths
			continue
		for node in path.nodes:
			node1 = node2
			node2 = node3
			node3 = node
			# this means we start with
			# path.nodes[-2], path.nodes[-1] and path.nodes[0]
			if node2.y == node1.y and node2.y == node3.y:
				pass
			# top extremum
			elif node2.y >= node1.y and node2.y >= node3.y and node1.x > node3.x:
				for index, ( name, zone, height ) in enumerate( zones ):
					if zone.size > 0 and node2.y >= zone.position and node2.y <= zone.position + zone.size:
						overshoot = node2.y - height
						existingOvershoot = overshoots[index][1]
						if overshoot > existingOvershoot:
							overshoots[index][1] = overshoot
			# bottom extremum
			elif node2.y <= node1.y and node2.y <= node3.y and node1.x < node3.x:
				for index, ( name, zone, height ) in enumerate( zones ):
					if zone.size < 0 and node2.y <= zone.position and node2.y >= zone.position + zone.size:
						overshoot = height - node2.y
						existingOvershoot = overshoots[index][1]
						if overshoot > existingOvershoot:
							overshoots[index][1] = overshoot
	return overshoots

# returns the overshoots for top and bottom zones,
# might be 'multiple' if they vary between layers.
# layers must not be empty.
def overshootsOfLayers( layers ):
	globalOvershoots = None
	for layer in layers:
		if not globalOvershoots:
			globalOvershoots = overshootsOfLayer( layer )
		else:
			overshoots = overshootsOfLayer( layer )
			for index, ( name, overshoot ) in enumerate( overshoots ):
				assert( name == globalOvershoots[index][0] )
				if overshoot is not None:
					if globalOvershoots[index][1] is None:
						globalOvershoots[index][1] = overshoot
					elif globalOvershoots[index][1] != overshoot:
							globalOvershoots[index][1] = 'multiple'
	return globalOvershoots

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# from https://forum.glyphsapp.com/t/vanilla-make-edittext-arrow-savvy/5894/2

GSSteppingTextField = objc.lookUpClass("GSSteppingTextField")
class ArrowEditText (EditText):
	nsTextFieldClass = GSSteppingTextField
	def _setCallback(self, callback):
		super(ArrowEditText, self)._setCallback(callback)
		if callback is not None and self._continuous:
			self._nsObject.setContinuous_(True)
			self._nsObject.setAction_(self._target.action_)
			self._nsObject.setTarget_(self._target)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class AlignmentPalette (PalettePlugin):

	# seems to be called whenever a new font is opened
	# careful! not called when the user switches to a different, already opened font
	def settings(self):
		width = 150
		self.name = Glyphs.localize({'en': u'Alignment'})
		self.marginTop = 7
		self.marginLeft = 7
		self.lineSpacing = 21
		smallSize = NSFont.systemFontSizeForControlSize_( NSFont.smallSystemFontSize() )
		textFieldHeight = smallSize + 7
		textFieldWidth = 50
		# lockHeight = textFieldHeight
		innerWidth = width - 2 * self.marginLeft
		height = ( MAX_ZONES + 4 ) * self.lineSpacing + self.marginTop * 3
		self.posx_TextField = width - textFieldWidth - self.marginLeft

		# Create Vanilla window and group with controls
		self.paletteView = Window( (width, height), minSize=(width, height - 10), maxSize=(width, height + 200 ) )
		self.paletteView.group = Group( (0, 0, width, height ) )

		posy = self.marginTop
		# set up fields for center
		headlineBbox = NSAttributedString.alloc().initWithString_attributes_( 'Bounding box', { NSFontAttributeName:NSFont.boldSystemFontOfSize_( smallSize ) } )
		self.paletteView.group.headlineBbox = TextBox( ( 10, posy, innerWidth, 18 ), headlineBbox, sizeStyle='small' )
		posy += self.lineSpacing
		self.paletteView.group.centerXLabel = TextBox( ( 10, posy + 3, innerWidth, 18 ), 'center x', sizeStyle='small' )
		self.posy_centerX = posy
		# self.paletteView.group.lockX = ImageButton( ( self.posx_TextField - lockHeight - 5, posy, lockHeight, lockHeight ), imageNamed='GSLockUnlockedTemplate', bordered=False, imagePosition='top', callback=self.lockCallback, sizeStyle='regular' )
		# self.lockXlocked = False
		self.paletteView.group.centerX = ArrowEditText( ( self.posx_TextField, posy, textFieldWidth, textFieldHeight ), callback=self.editTextCallback, continuous=False, readOnly=False, formatter=None, placeholder='multiple', sizeStyle='small' )
		posy += self.lineSpacing
		self.paletteView.group.centerYLabel = TextBox( ( 10, posy + 3, innerWidth, 18 ), 'center y', sizeStyle='small' )
		self.posy_centerY = posy
		# self.paletteView.group.lockY = ImageButton( ( self.posx_TextField - lockHeight - 5, posy, lockHeight, lockHeight ), imageNamed='GSLockUnlockedTemplate', bordered=False, imagePosition='top', callback=self.lockCallback, sizeStyle='regular' )
		# self.lockYlocked = False
		self.paletteView.group.centerY = ArrowEditText( ( self.posx_TextField, posy, textFieldWidth, textFieldHeight ), callback=self.editTextCallback, continuous=False, readOnly=False, formatter=None, placeholder='multiple', sizeStyle='small' )
		posy += self.lineSpacing + self.marginTop
		# set up fields for overshoot
		headlineOvershoot = NSAttributedString.alloc().initWithString_attributes_( 'Overshoot', { NSFontAttributeName:NSFont.boldSystemFontOfSize_( NSFont.systemFontSizeForControlSize_( smallSize ) ) } )
		self.paletteView.group.headlineOvershoot = TextBox( ( 10, posy, innerWidth, 18 ), headlineOvershoot, sizeStyle='small' )
		posy += self.lineSpacing
		self.paletteView.group, 'lineAbove', HorizontalLine( ( self.marginLeft, posy - 3, innerWidth, 1 ) )
		for i in xrange( MAX_ZONES ):
			setattr( self.paletteView.group, 'name' + str( i ), TextBox( ( 10, posy, innerWidth, 18 ), '', sizeStyle='small' ) )
			setattr( self.paletteView.group, 'value' + str( i ), TextBox( ( self.posx_TextField, posy, textFieldWidth - 3, textFieldHeight ), '', sizeStyle='small', alignment='right' ) )
			posy += self.lineSpacing
			setattr( self.paletteView.group, 'line' + str( i ), HorizontalLine( ( self.marginLeft, posy - 3, innerWidth, 1 ) ) )
		# set dialog to NSView
		self.dialog = self.paletteView.group.getNSView()
		# set self.font
		self.font = None
		windowController = self.windowController()
		if windowController:
			self.font = windowController.document().font

	def update( self, sender=None ):
		# do not update in case the palette is collapsed
		if self.dialog.frame().origin.y != 0:
			return
		if sender:
			self.font = sender.object()
		if not self.font:
			return
		# do not update when too may glyphs are selected
		if not self.font.selectedLayers or len( self.font.selectedLayers ) > MAX_GLYPHS_COUNT:
			self.paletteView.group.centerX.show( False )
			self.paletteView.group.centerY.show( False )
			for i in xrange( MAX_ZONES ):
				getattr( self.paletteView.group, 'name' + str( i ) ).set( '' )
				getattr( self.paletteView.group, 'value' + str( i ) ).show( False )
				getattr( self.paletteView.group, 'line' + str( i ) ).show( False )
			return
		# update the center x and y
		if self.font.selectedLayers:
			# determine centers
			globalCenterX, globalCenterY = centerOfLayers( self.font.selectedLayers )
			if globalCenterX is None:
				globalCenterX = ''
			else:
				# display as integers if the numbers are whole numbers
				try:
					if globalCenterX == int( globalCenterX ):
						globalCenterX = int( globalCenterX )
				except ValueError:
					pass
			if globalCenterY is None:
				globalCenterY = ''
			else:
				try:
					if globalCenterY == int( globalCenterY ):
						globalCenterY = int( globalCenterY )
				except ValueError:
					pass
			# update dialog
			self.paletteView.group.centerX.show( True )
			self.paletteView.group.centerX.set( globalCenterX )
			self.paletteView.group.centerY.show( True )
			self.paletteView.group.centerY.set( globalCenterY )
		else:
			self.paletteView.group.centerX.show( False )
			self.paletteView.group.centerY.show( False )
		# update the overshoots
		if self.font.selectedLayers:
			# determine overshoots
			globalOvershoots = overshootsOfLayers( self.font.selectedLayers )
		else:
			globalOvershoots = []
		for i in xrange( MAX_ZONES ):
			try:
				zoneName, overshoot = globalOvershoots[i]
				getattr( self.paletteView.group, 'name' + str( i ) ).set( zoneName )
				getattr( self.paletteView.group, 'line' + str( i ) ).show( True )
				if overshoot is not None:
					# display as integers if the numbers are whole numbers
					try:
						if overshoot == int( overshoot ):
							overshoot = int( overshoot )
					except ValueError:
						pass
					getattr( self.paletteView.group, 'value' + str( i ) ).show( True )
					getattr( self.paletteView.group, 'value' + str( i ) ).set( overshoot )
				else:
					getattr( self.paletteView.group, 'value' + str( i ) ).show( False )
			except IndexError:
				# this hides the excess fields
				getattr( self.paletteView.group, 'name' + str( i ) ).set( '' )
				getattr( self.paletteView.group, 'value' + str( i ) ).show( False )
				getattr( self.paletteView.group, 'line' + str( i ) ).show( False )

	# in future, this could be used to "lock" the x or y value,
	# i.e. auto-update the glyph in a "set up and forget" fashion
	# def lockCallback(self, button):
	# 	posX, posY, w, h = button.getPosSize()
	# 	if posY == self.posy_centerX:
	# 		print 'is X!'
	# 	else:
	# 		print 'is Y!'
	
	def editTextCallback(self, editText):
		if not self.font or not self.font.selectedLayers:
			return
		try:
			newCenterX = float( self.paletteView.group.centerX.get() )
		except ValueError:
			newCenterX = None
		try:
			newCenterY = float( self.paletteView.group.centerY.get() )
		except ValueError:
			newCenterY = None
		if not STICK_TO_GRID:
			# zero subdivisions would not make sense
			if self.font.gridSubDivisions == 0:
				self.font.gridSubDivisions = 1
			# we temporarily double the number of subdivisions to allow for precise centering
			self.font.gridSubDivisions *= 2
		# we first treat only layers without components,
		# so as to make sure we are not updating the referenced glyph after the component
		for hasComponents in [ False, True ]:
			# set the layers' centers
			for layer in self.font.selectedLayers:
				if ( len( layer.components ) > 0 ) == hasComponents:
					print layer.parent.name
					layer.parent.beginUndo()
					setCenterOfLayer( layer, newCenterX, newCenterY )
					layer.parent.endUndo()
		# restore the number of subdivisions
		if not STICK_TO_GRID:
			self.font.gridSubDivisions /= 2
		Glyphs.redraw()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	def start(self):
		# Adding a callback for the 'GSUpdateInterface' event
		Glyphs.addCallback(self.update, UPDATEINTERFACE)
	
	def __del__(self):
		Glyphs.removeCallback(self.update)

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
	
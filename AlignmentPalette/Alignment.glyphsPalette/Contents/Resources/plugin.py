# encoding: utf-8
from __future__ import division, print_function, unicode_literals


import objc
from GlyphsApp import *
from GlyphsApp.plugins import *
from vanilla import *
from AppKit import NSFont, NSAttributedString, NSFontAttributeName, NSMidX, NSMidY
# maximum number of zones to be diasplayed
# increase this value if you have more zones in your font
MAX_ZONES = 10

# if False, this deactivates the grid, i.e. allows fractional positioning
# to achieve exact centering
STICK_TO_GRID = True

# maximum number of glyphs
MAX_GLYPHS_COUNT = 100

# Glyphs constants
COUNTERCLOCKWISE = -1
CLOCKWISE = 1

def displayStrFromNumbers(value1, value2):
	if value1 is None:
		return ''
	str1 = f"{value1:.1f}".rstrip('0').rstrip('.')
	str2 = f'{value2:.1f}'.rstrip('0').rstrip('.')
	if str1 == str2:
		return str1
	return str1 + ' — ' + str2

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

class AlignmentPalette (PalettePlugin):

	# sets the center of the bounding box of a layer
	@objc.python_method
	def setCenterOfLayer(self, layer, newCenterX, newCenterY):
		centerX, centerY = self.centerOfLayer(layer)
		try:
			shiftX = newCenterX - centerX
		except TypeError:
			shiftX = 0
		try:
			shiftY = newCenterY - centerY
		except TypeError:
			shiftY = 0
		layer.applyTransform([1.0, 0.0, 0.0, 1.0, shiftX, shiftY])
		layer.syncMetrics()

	# returns the center of the bounding box of a layer
	@objc.python_method
	def centerOfLayer(self, layer):
		if Glyphs.versionNumber >= 3:
			if len(layer.shapes) == 0:
				return None, None
		bounds = layer.bounds
		centerX = NSMidX(bounds)
		centerY = NSMidY(bounds)
		return centerX, centerY

	# returns the center of the layers,
	# x or y might be '' if they vary between layers
	@objc.python_method
	def centerOfLayers(self, layers):
		globalCenterX = None
		globalCenterY = None
		globalCenterXmax = None
		globalCenterYmax = None
		for layer in layers:
			centerX, centerY = self.centerOfLayer(layer)
			if centerX is None:
				# empty layer (no need to check centerY)
				continue
			if globalCenterX is None:
				globalCenterX    = centerX
				globalCenterXmax = centerX
				globalCenterY    = centerY
				globalCenterYmax = centerY
			else:
				globalCenterX    = min(globalCenterX, centerX)
				globalCenterXmax = max(globalCenterXmax, centerX)
				globalCenterY    = min(globalCenterY, centerY)
				globalCenterYmax = max(globalCenterYmax, centerY)
		return displayStrFromNumbers(globalCenterX, globalCenterXmax), displayStrFromNumbers(globalCenterY, globalCenterYmax)

	# returns a list of tuples with zone name, zone and height,
	# sorted by height
	@objc.python_method
	def namedZones(self, layer):
		metrics = None
		try:
			metrics = layer.metrics
			# ^ this is a new Glyphs 3 thing.
			#   not sure how to use it but sometimes it seems to return
			#   an objc.native_selector object rather than something iterable.
			#   maybe we need try calling layer.metrics() in addition?
			#
			#   so let’s better keep this inside the try block as well:
			if metrics is not None:
				zones = []
				for metric in metrics:
					zones.append((metric.name, metric, metric.position))
				return zones
		except:
			pass
		
		glyph = layer.parent
		if not glyph:
			return []
		font = glyph.parent
		if not font:
			return []
		masters = [m for m in font.masters if m.id == layer.associatedMasterId]
		if not masters:
			return []
		master = masters[0]
		topHeights = [('cap height', master.capHeight), ('ascender', master.ascender), ('x-height', master.xHeight)]
		bottomHeights = [('baseline', 0), ('descender', master.descender)]
		zones = []
		for zone in master.alignmentZones:
			if zone.size > 0:
				for name, y in topHeights:
					if y >= zone.position and y <= zone.position + zone.size:
						zones.append((name, zone, y))
						break
				else:
					zones.append((str(zone.position), zone, zone.position))
			elif zone.size < 0:
				for name, y in bottomHeights:
					if y <= zone.position and y >= zone.position + zone.size:
						zones.append((name, zone, y))
						break
				else:
					zones.append((str(zone.position), zone, zone.position))
		# sort by height
		zones.sort(key=lambda x: x[2], reverse = True)
		return zones

	# returns a list of tuples (zone name, overshoot) for the layer
	# overshoot may be None
	@objc.python_method
	def overshootsOfLayer(self, layer):
		zones = self.namedZones(layer)
		overshoots = [[name, -1] for name, zone, height in zones]
		for path in layer.copyDecomposedLayer().paths:
			if path.direction == CLOCKWISE or len(path.nodes) < 2:
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
					for index, (name, zone, height) in enumerate(zones):
						if zone.size > 0 and node2.y >= zone.position and node2.y <= zone.position + zone.size:
							overshoot = node2.y - height
							existingOvershoot = overshoots[index][1]
							if overshoot > existingOvershoot:
								overshoots[index][1] = overshoot
				# bottom extremum
				elif node2.y <= node1.y and node2.y <= node3.y and node1.x < node3.x:
					for index, (name, zone, height) in enumerate(zones):
						if zone.size < 0 and node2.y <= zone.position and node2.y >= zone.position + zone.size:
							overshoot = height - node2.y
							existingOvershoot = overshoots[index][1]
							if overshoot > existingOvershoot:
								overshoots[index][1] = overshoot
		return overshoots

	# returns the overshoots for top and bottom zones,
	# might be 'multiple' if they vary between layers.
	# layers must not be empty.
	@objc.python_method
	def overshootsOfLayers(self, layers):
		globalOvershoots = None
		for layer in layers:
			if not layer:
				continue
			if not globalOvershoots:
				globalOvershoots = self.overshootsOfLayer(layer)
			else:
				overshoots = self.overshootsOfLayer(layer)
				for index, (name, overshoot) in enumerate(overshoots):
					zone = globalOvershoots[index]
					if zone[1] == overshoot:
						continue
					if len(zone) == 2:
						# need to add a third value.
						# zone[1] is to be interpreted as the min,
						# zone[2] is to be interpreted as the max
						zone.append(zone[1])
					zone[1] = min(zone[1], overshoot)
					zone[2] = max(zone[2], overshoot)
		for zone in globalOvershoots:
			if len(zone) == 3:
				minValue = zone[1]
				maxValue = zone.pop()
				if minValue == -1:
					# some glyphs do not have anything in/on the zone, some do
					zone[1] = 'multiple'
				else:
					zone[1] = displayStrFromNumbers(minValue, maxValue)
		return globalOvershoots

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

	# seems to be called whenever a new font is opened
	# careful! not called when the user switches to a different, already opened font
	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({
			'en': 'Alignment',
			'de': 'Ausrichtung',
			'es': 'Alineación',
			'fr': 'Alignement',
			'pt': 'Alinhamento',
		})
		width = 150
		self.marginTop = 7
		self.marginLeft = 7
		self.lineSpacing = 21
		smallSize = NSFont.systemFontSizeForControlSize_(NSFont.smallSystemFontSize())
		textFieldHeight = smallSize + 7
		textFieldWidth = 70
		# lockHeight = textFieldHeight
		innerWidth = width - 2 * self.marginLeft
		height = (MAX_ZONES + 4) * self.lineSpacing + self.marginTop * 3
		self.posx_TextField = width - textFieldWidth - self.marginLeft

		# Create Vanilla window and group with controls
		self.paletteView = Window((width, height), minSize=(width, height - 10), maxSize=(width, height + 200))
		self.paletteView.group = Group((0, 0, width, height))

		posy = self.marginTop
		# set up fields for center
		headlineBbox = NSAttributedString.alloc().initWithString_attributes_('Bounding box', {NSFontAttributeName: NSFont.boldSystemFontOfSize_(smallSize)})
		self.paletteView.group.headlineBbox = TextBox((10, posy, innerWidth, 18), headlineBbox, sizeStyle='small')
		posy += self.lineSpacing
		self.paletteView.group.centerXLabel = TextBox((10, posy + 3, innerWidth, 18), 'center x', sizeStyle='small')
		self.posy_centerX = posy
		self.paletteView.group.centerX = ArrowEditText((self.posx_TextField, posy, textFieldWidth, textFieldHeight), callback=self.editTextCallback, continuous=False, readOnly=False, formatter=None, sizeStyle='small')
		posy += self.lineSpacing
		self.paletteView.group.centerYLabel = TextBox((10, posy + 3, innerWidth, 18), 'center y', sizeStyle='small')
		self.posy_centerY = posy
		self.paletteView.group.centerY = ArrowEditText((self.posx_TextField, posy, textFieldWidth, textFieldHeight), callback=self.editTextCallback, continuous=False, readOnly=False, formatter=None, sizeStyle='small')
		posy += self.lineSpacing + self.marginTop
		# set up fields for overshoot
		headlineOvershoot = NSAttributedString.alloc().initWithString_attributes_('Overshoot', {NSFontAttributeName: NSFont.boldSystemFontOfSize_(NSFont.systemFontSizeForControlSize_(smallSize))})
		self.paletteView.group.headlineOvershoot = TextBox((10, posy, innerWidth, 18), headlineOvershoot, sizeStyle='small')
		posy += self.lineSpacing
		self.paletteView.group, 'lineAbove', HorizontalLine((self.marginLeft, posy - 3, innerWidth, 1))
		for i in range(MAX_ZONES):
			setattr(self.paletteView.group, 'name' + str(i), TextBox((10, posy, innerWidth, 18), '', sizeStyle='small'))
			setattr(self.paletteView.group, 'value' + str(i), TextBox((self.posx_TextField, posy, textFieldWidth - 3, textFieldHeight), '', sizeStyle='small', alignment='right'))
			posy += self.lineSpacing
			setattr(self.paletteView.group, 'line' + str(i), HorizontalLine((self.marginLeft, posy - 3, innerWidth, 1)))
		# set dialog to NSView
		self.dialog = self.paletteView.group.getNSView()
		# set self.font
		self.font = None
		windowController = self.windowController()
		if windowController:
			self.font = windowController.document().font

	@objc.python_method
	def update(self, sender=None):
		# do not update in case the palette is collapsed
		if self.dialog.frame().origin.y != 0:
			return
		if sender:
			self.font = sender.object()
			if isinstance(self.font, GSEditViewController): # it is GSEditViewController in Glyphs3
				try:
					self.font = self.font.representedObject()
				except:
					pass
		if not self.font:
			return
		# do not update when too may glyphs are selected
		if not self.font.selectedLayers or len(self.font.selectedLayers) > MAX_GLYPHS_COUNT:
			self.paletteView.group.centerX.show(False)
			self.paletteView.group.centerY.show(False)
			for i in range(MAX_ZONES):
				getattr(self.paletteView.group, 'name' + str(i)).set('')
				getattr(self.paletteView.group, 'value' + str(i)).show(False)
				getattr(self.paletteView.group, 'line' + str(i)).show(False)
			return
		# update the center x and y
		if self.font.selectedLayers:
			# determine centers
			globalCenterX, globalCenterY = self.centerOfLayers(self.font.selectedLayers)
			# update dialog
			self.paletteView.group.centerX.show(True)
			self.paletteView.group.centerX.set(globalCenterX)
			self.paletteView.group.centerY.show(True)
			self.paletteView.group.centerY.set(globalCenterY)
		else:
			self.paletteView.group.centerX.show(False)
			self.paletteView.group.centerY.show(False)
		# update the overshoots
		if self.font.selectedLayers:
			# determine overshoots
			globalOvershoots = self.overshootsOfLayers(self.font.selectedLayers)
		else:
			globalOvershoots = []
		for i in range(MAX_ZONES):
			try:
				zoneName, overshoot = globalOvershoots[i]
				getattr(self.paletteView.group, 'name' + str(i)).set(zoneName)
				getattr(self.paletteView.group, 'line' + str(i)).show(True)
				assert(overshoot is not None)
				if overshoot == -1:
					# nothing in the zone
					overshoot = ''
				getattr(self.paletteView.group, 'value' + str(i)).show(True)
				getattr(self.paletteView.group, 'value' + str(i)).set(overshoot)
			except IndexError:
				# this hides the excess fields
				getattr(self.paletteView.group, 'name' + str(i)).set('')
				getattr(self.paletteView.group, 'value' + str(i)).show(False)
				getattr(self.paletteView.group, 'line' + str(i)).show(False)

	# in future, this could be used to "lock" the x or y value,
	# i.e. auto-update the glyph in a "set up and forget" fashion
	# def lockCallback(self, button):
	# 	posX, posY, w, h = button.getPosSize()

	@objc.python_method	
	def editTextCallback(self, editText):
		if not self.font or not self.font.selectedLayers:
			return
		try:
			newCenterX = float(self.paletteView.group.centerX.get())
		except ValueError:
			newCenterX = None
		try:
			newCenterY = float(self.paletteView.group.centerY.get())
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
		for hasComponents in [False, True]:
			# set the layers' centers
			for layer in self.font.selectedLayers:
				if (len(layer.components) > 0) == hasComponents:
					layer.parent.beginUndo()
					self.setCenterOfLayer(layer, newCenterX, newCenterY)
					layer.parent.endUndo()
		# restore the number of subdivisions
		if not STICK_TO_GRID:
			self.font.gridSubDivisions /= 2
		Glyphs.redraw()

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
	
#MenuTitle: Toggle Backup Layer
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__="""
This script toggles between the currently selected layer and the master layer (alternatively, between the master and the last backup layer in the list).

If given a keyboard shortcut, this is very useful for comparing two versions of a glyph.
"""

font = Glyphs.font
currentTab = font.currentTab

text = currentTab.graphicView().textStorage().text()
selectedRange = currentTab.graphicView().selectedRange()
selectedRange.length = 1
try:
	layerIdAttribute = text.attributesAtIndex_effectiveRange_( selectedRange.location, None )[0]['GSLayerIdAttrib']
except KeyError:
	layerIdAttribute = None

currentLayer = font.selectedLayers[0]
if layerIdAttribute == currentLayer.layerId:
	# ^ it’s not sufficient to only check layerIdAttribute 
	#   because Glyphs may use an invalid GSLayerIdAttrib
	
	# currently on backup layer. switch to master layer:
	text.setAttributes_range_( { "GSLayerIdAttrib": None }, selectedRange )
	backupLayerId = layerIdAttribute
else:
	# currently on master layer.
	currentGlyph = currentLayer.parent
	try:
		backupLayer = currentGlyph.layers[backupLayerId]
	except NameError:
		# uninitialized backupLayerId
		backupLayer = None
	if not backupLayer:
		# backup layer not specified (remembered). use the last layer:
		backupLayer = currentGlyph.layers[-1]
		backupLayerId = backupLayer.layerId
	text.setAttributes_range_( { "GSLayerIdAttrib": backupLayerId }, selectedRange )

currentTab.textCursor = currentTab.textCursor
# ^ this makes Glyphs update the UI (couldn’t find a more elegant way of triggering this)

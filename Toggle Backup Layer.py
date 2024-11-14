#MenuTitle: Toggle Backup Layer
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__="""
This script toggles between the currently selected layer and the master layer (alternatively, between the master and the last backup layer in the list).

If given a keyboard shortcut, this is very useful for comparing two versions of a glyph.
"""

font = Glyphs.font
currentTab = font.currentTab

textStorage = currentTab.graphicView().textStorage()
text = textStorage.text()

selectedRange = currentTab.graphicView().selectedRange()
selectedRange.length = 1
try:
	layerIdAttribute = text.attribute_atIndex_effectiveRange_("GSLayerIdAttrib", selectedRange.location, None)[0]
except KeyError:
	layerIdAttribute = None
currentLayer = font.selectedLayers[0]

textStorage.willChangeValueForKey_("text")
if layerIdAttribute == currentLayer.layerId:
	# currently on backup layer. switch to master layer:
	text.removeAttribute_range_("GSLayerIdAttrib", selectedRange)
	backupLayerId = layerIdAttribute
else:
	# currently on master layer.
	currentGlyph = currentLayer.parent
	try:
		backupLayer = currentGlyph.layers[backupLayerId]
	except NameError:
		# uninitialized backupLayerId
		backupLayer = None
	if backupLayer and backupLayer.associatedMasterId != currentLayer.layerId:
		# remembered layer is from a different master. let’s not switch to that one.
		backupLayer = None
	if not backupLayer:
		# backup layer not specified (remembered). use the last layer:
		for layer in currentGlyph.layers:
			if layer.layerId == currentLayer.layerId:
				continue
			if layer.associatedMasterId == currentLayer.associatedMasterId:
				backupLayerId = layer.layerId
	text.addAttribute_value_range_("GSLayerIdAttrib", backupLayerId, selectedRange)

# trigger UI update:
textStorage.didChangeValueForKey_("text")
currentTab.textCursor = currentTab.textCursor

#MenuTitle: Toggle Backup Layer

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
This script toggles between the currently selected layer and the master layer (alternatively, between the master and the last backup layer in the list).

If given a keyboard shortcut, this is very useful for comparing two versions of a glyph.
'''

font = Glyphs.font
currentTab = font.currentTab
currentLayer = font.selectedLayers[0]
currentGlyph = currentLayer.parent

textStorage = currentTab.graphicView().textStorage()
text = textStorage.text()

selectedRange = currentTab.graphicView().selectedRange()
selectedRange.length = 1
try:
	layerIdAttribute = text.attribute_atIndex_effectiveRange_("GSLayerIdAttrib", selectedRange.location, None)[0]
except KeyError:
	layerIdAttribute = None

# determine last layer:
for layer in currentGlyph.layers:
	if layer.associatedMasterId == currentLayer.associatedMasterId:
		lastLayerId = layer.layerId

textStorage.willChangeValueForKey_("text")
if layerIdAttribute == currentLayer.layerId:
	# currently on backup layer. switch to master layer:
	text.removeAttribute_range_("GSLayerIdAttrib", selectedRange)
	backupLayerId = layerIdAttribute
else:
	# currently on master layer.
	try:
		backupLayer = currentGlyph.layers[backupLayerId]
	except (TypeError, NameError):
		# uninitialized backupLayerId
		backupLayer = None
	if backupLayer and backupLayer.associatedMasterId != currentLayer.layerId:
		# remembered layer is from a different master. let’s not switch to that one.
		backupLayer = None
	if not backupLayer:
		# backup layer not specified (remembered). use the last layer:
		backupLayerId = lastLayerId
	text.addAttribute_value_range_("GSLayerIdAttrib", backupLayerId, selectedRange)

if backupLayerId == lastLayerId:
	# “forget” the used backup layer:
	backupLayerId = None
	# the effect is that when new backup layers are added,
	# it will switch to the last (added) layer instead of the current one

# trigger UI update:
textStorage.didChangeValueForKey_("text")
currentTab.textCursor = currentTab.textCursor

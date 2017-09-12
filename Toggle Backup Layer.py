#MenuTitle: Toggle Backup Layer
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__="""
This script toggles between the master layer and
the last backup layer in the list.

Given a keyboard shortcut, this is useful for
comparing two versions of a glyph.

"""

from GlyphsApp import *

font = Glyphs.font
currentTab = font.currentTab

layers = currentTab.layers.values()
print layers
currentLayer = layers[currentTab.layersCursor]
if currentLayer.layerId == font.selectedFontMaster.id:
	# Current layer is the selected master layer.
	print 'Current layer is the selected master layer.'
	# Switch current glyph to the last associated non-master layer.
	for layer in currentLayer.parent.layers:
		if layer.associatedMasterId == font.selectedFontMaster.id:
			layers[currentTab.layersCursor] = layer
else:
	# Current layer is not the selected master layer.
	print 'Current layer is NOT the selected master layer.'
	# Switch each glyph in the current tab to its currently active master layer.
	for layer_index in range( len( layers ) ):
		layer = layers[layer_index]
		glyph = layer.parent
		master_layer = glyph.layers[ font.selectedFontMaster.id ]
		layers[layer_index] = master_layer
currentTab.layers.setter( layers )

# explicit redraw (does not seem to be necessary)
# currentTab.redraw()
# Glyphs.redraw()

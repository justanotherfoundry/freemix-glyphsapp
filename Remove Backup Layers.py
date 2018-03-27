#MenuTitle: Remove Backup Layers
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__='''
Removes all backup layers (i.e. those created using the "Copy" button) from the selected glyphs.

'''

import re

font = Glyphs.currentDocument.font
selected_glyphs = set( [ layer.parent for layer in font.selectedLayers ] )

for glyph in selected_glyphs:
	associated_layers = [ layer.layerId for layer in glyph.layers if layer.layerId != layer.associatedMasterId and ( not layer.name or not re.search( r"(\{[^a-zA-Z]+\})|([\[\]][^a-zA-Z]+\])", layer.name ) ) ]
	for layerId in associated_layers:
		print 'deleting extra layer from', glyph.name
		del glyph.layers[layerId]

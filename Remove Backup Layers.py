#MenuTitle: Remove Backup Layers
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

'''
Removes all backup layers (i.e. those created using the "Copy" button) from the font.

'''

from GlyphsApp import *

font = Glyphs.currentDocument.font

for glyph in font.glyphs:
	associated_layers = [ layer.layerId for layer in glyph.layers if layer.layerId != layer.associatedMasterId and not '[' in layer.name and not ']' in layer.name ]
	for layerId in associated_layers:
		print 'deleting extra layer from', glyph.name
		del glyph.layers[layerId]

#MenuTitle: Remove Backup Layers
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

from __future__ import division, print_function, unicode_literals

__doc__='''
Removes all backup layers (i.e. those created using the "Copy" button) from the selected glyphs.

'''

font = Glyphs.currentDocument.font
selected_glyphs = set( [ layer.parent for layer in font.selectedLayers ] )

for glyph in selected_glyphs:
	for i in range(len(glyph.layers) - 1, -1, -1):
		if not glyph.layers[i].isSpecialLayer and not glyph.layers[i].isMasterLayer:
			del glyph.layers[i]

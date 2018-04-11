#MenuTitle: Delete All Hints
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__='''
Removes all hints from the selected glyphs.

'''

from GlyphsApp import *

doc = Glyphs.currentDocument
font = doc.font
layers = doc.selectedLayers()

for layer in layers:
	for i in range( len( layer.hints ) -1, -1, -1 ):
		if layer.hints[i].type != CORNER and layer.hints[i].type != CAP:
			del layer.hints[i]

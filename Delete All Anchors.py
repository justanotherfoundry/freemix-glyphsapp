#MenuTitle: Delete All Anchors
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__='''
Removes all anchors from the selected glyphs.
'''

from GlyphsApp import *

doc = Glyphs.currentDocument
font = doc.font

for selectedLayer in doc.selectedLayers():
	glyph = selectedLayer.parent
	for layer in glyph.layers:
		layer.anchors = []

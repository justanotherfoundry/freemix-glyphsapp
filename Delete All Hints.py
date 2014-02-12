#MenuTitle: Delete All Hints
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

'''
Removes all hints from the selected glyphs.

'''

from GlyphsApp import *

doc = Glyphs.currentDocument
font = doc.font
layers = doc.selectedLayers()

for layer in layers:
	layer.hints = []

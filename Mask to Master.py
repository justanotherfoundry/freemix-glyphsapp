#MenuTitle: mask to master
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

'''
Simulates the good ol' Mask to Master function we know from FontLab
(i.e. replaces the current outline with the background).

You can give it the familiar Cmd+J shortcut via App Shortcuts
in the Mac OS System Preferences.
'''

from GlyphsApp import *

font = Glyphs.font
layers = font.selectedLayers
glyph = layers[0].parent

glyph.beginUndo()

for layer in layers:
	# remove outline
	for i in range( len ( layer.paths ) ):
		del layer.paths[0]
	# paste in background
	for path in layer.copyDecomposedLayer().background.paths:
		layer.paths.append( path )

glyph.endUndo()

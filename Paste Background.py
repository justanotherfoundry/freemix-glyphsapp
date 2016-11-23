#MenuTitle: Paste Background
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__='''
Pastes the background contours into the current layer.

Former FontLab users can give it the familiar Cmd+L shortcut via App Shortcuts
in the Mac OS System Preferences.
'''

from GlyphsApp import *

doc = Glyphs.currentDocument
font = doc.font
layers = doc.selectedLayers()
glyph = layers[0].parent

glyph.beginUndo()

for layer in layers:
	# deselect all
	for path in layer.paths:
		for node in path.nodes:
			layer.removeObjectFromSelection_( node )
		# layer.removeObjectsFromSelection_( path.pyobjc_instanceMethods.nodes() )

	# paste in background
	for path in layer.copyDecomposedLayer().background.paths:
		# copy across path
		layer.paths.append( path )
		# select path
		for node in layer.paths[-1].nodes:
			layer.addSelection_( node )

glyph.endUndo()

#MenuTitle: Paste Background
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__='''
Pastes the background into the current layer.

Components are pasted as paths (i.e. decomposed).
'''

from GlyphsApp import *

doc = Glyphs.currentDocument
font = doc.font
layers = doc.selectedLayers()
glyph = layers[0].parent

glyph.beginUndo()

for layer in layers:
	# deselect all in the foreground
	for path in layer.paths:
		for node in path.nodes:
			layer.removeObjectFromSelection_( node )
		# layer.removeObjectsFromSelection_( path.pyobjc_instanceMethods.nodes() )
	# insert the background contents and select them
	for path in layer.background.copyDecomposedLayer().paths:
		layer.paths.append( path.copy() )
		# select path
		try:
			# Glyphs 2
			for node in layer.paths[-1].nodes:
				layer.addSelection_( node )
		except:
			# Glyphs 3
			for node in layer.shapes[-1].nodes:
				layer.addSelection_( node )

glyph.endUndo()

#MenuTitle: Paste Background

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
Pastes the background into the current layer.

Components are pasted as paths (i.e. decomposed).
'''

from GlyphsApp import Glyphs

doc = Glyphs.currentDocument
layers = doc.selectedLayers()
glyph = layers[0].parent

for layer in layers:
	selection = []
	# insert the background contents and select them
	for path in layer.background.copyDecomposedLayer().paths:
		newPath = path.copy()
		if Glyphs.versionNumber == 2:
			layer.paths.append( newPath )
		else:
			layer.shapes.append( newPath )
		# select path
		selection.extend( newPath.nodes )
	layer.selection = selection

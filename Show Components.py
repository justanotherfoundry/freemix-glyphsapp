#MenuTitle: Show Components
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__="""
Shows the glyphs contained within the selected glyph(s).
Useful for “dissolving” ligatures, or to determine glyph set dependencies
(i.e. glyphs that cannot be deleted if the selected ones are to be retained).
"""

tabLayers = Glyphs.font.currentTab.layers
for layer in Glyphs.font.selectedLayers:
	masterId = layer.master.id
	for component in layer.components:
		glyph = Glyphs.font.glyphs[component.name]
		newLayer = glyph.layers[masterId]
		tabLayers.append(newLayer)

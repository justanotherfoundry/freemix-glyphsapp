#MenuTitle: Edit Previous Glyph

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
Activates the previous glyph in the tab for editing. You can give it a keyboard shortcut in the macOS system preferences.
'''

font = Glyphs.font
if font:
	tab = font.currentTab
	if tab:
		while 1:
			newPosition = (tab.layersCursor - 1 + len(tab.layers)) % (len(tab.layers))
			tab.layersCursor = newPosition
			if newPosition == 0 or font.selectedLayers:
				break
		vp = tab.viewPort
		vp.origin.x = tab.selectedLayerOrigin.x + 0.5 * ( font.selectedLayers[0].width * tab.scale - vp.size.width )
		if newPosition == len(tab.layers) - 1:
			print()
		tab.viewPort = vp

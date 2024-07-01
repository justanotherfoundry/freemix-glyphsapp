#MenuTitle: Edit Previous Glyph
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__="""
Activates the previous glyph in the tab for editing. You can give it a keyboard shortcut in the macOS system preferences.
"""

font = Glyphs.font
if font:
	tab = font.currentTab
	if tab:
		# move cursor:
		newPosition = (tab.layersCursor - 1 + len(tab.layers)) % (len(tab.layers))
		tab.layersCursor = newPosition
		# re-center glyph:
		vp = tab.viewPort
		vp.origin.x = tab.selectedLayerOrigin.x + 0.5 * ( font.selectedLayers[0].width * tab.scale - vp.size.width )
		if newPosition == len(tab.layers) - 1:
			print()
			# ^ very strange: if we don’t do this
			#   then the glyph is not centred correctly
			#   if the text cursor is active
			# explanation from Georg:
			# https://forum.glyphsapp.com/t/centering-the-current-glyph-in-tab/29408/18
		tab.viewPort = vp
		# TODO: in case the new glyph is on a different line, also adjust y 

#MenuTitle: Edit Next Glyph

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
Activates the next glyph in the tab for editing. You can give it a keyboard shortcut in the macOS system preferences.
'''

font = Glyphs.font
if font:
	tab = font.currentTab
	if tab:
		# move cursor:
		# (adopted from https://glyphsapp.com/news/glyphs-3-2-released)
		while 1:
			newPosition = (tab.layersCursor + 1) % (len(tab.layers))
			tab.layersCursor = newPosition
			if newPosition == 0 or font.selectedLayers:
				# non-empty font.selectedLayers means the current layer os _not_ a newline (GSControlLayer)
				# the check newPosition == 0 is necessary to avoid an infinite loop in a tab with only newlines
				break
		# re-center glyph:
		vp = tab.viewPort
		vp.origin.x = tab.selectedLayerOrigin.x + 0.5 * ( font.selectedLayers[0].width * tab.scale - vp.size.width )
		if newPosition == 0:
			print()
			# ^ very strange: if we don’t do this
			#   then the glyph is not centred correctly
			#   if the text cursor is active
			# explanation from Georg:
			# https://forum.glyphsapp.com/t/centering-the-current-glyph-in-tab/29408/18
		tab.viewPort = vp
		# TODO: in case the new glyph is on a different line, also adjust y 

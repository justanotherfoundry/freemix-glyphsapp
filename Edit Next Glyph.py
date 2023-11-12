#MenuTitle: Edit Next Glyph
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__="""
Activates the next glyph in the tab for editing. You can give it a keyboard shortcut in the macOS system preferences.
"""

font = Glyphs.font
if font:
	tab = font.currentTab
	if tab:
		initialCursor = tab.textCursor
		while 1:
			tab.textCursor = (tab.textCursor + 1) % len(tab.layers)
			# in case there are no real glyphs in the tab, we need to prevent an infinite loop
			if tab.textCursor == initialCursor:
				break
			try:
				if font.selectedLayers[0].parent.name:
					break
			except:
				# this happens when the cursor reaches a line break
				pass
		layer = font.selectedLayers[0]
		if tab.viewPort.origin.x + tab.viewPort.size.width < tab.bounds.origin.x + tab.bounds.size.width:
			vp = tab.viewPort
			vp.origin.x = tab.selectedLayerOrigin.x + 0.5 * ( layer.width * tab.scale - vp.size.width )
			tab.viewPort = vp

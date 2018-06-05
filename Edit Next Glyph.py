#MenuTitle: Edit Next Glyph
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__="""
Activates the next glyph in the tab for editing. You can give it a keyboard shortcut in the macOS system preferences.
"""

initialCursor = Font.currentTab.textCursor
while 1:
	Font.currentTab.textCursor = (Font.currentTab.textCursor + 1) % len(Font.currentTab.layers)
	# in case there are no real glyphs in the tab, we need to prevent an infinite loop
	if Font.currentTab.textCursor == initialCursor:
		break
	try:
		if Glyphs.font.selectedLayers[0].parent.name:
			break
	except:
		# this happens when the cursor reaches a line break
		pass

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
		view = tab.graphicView()
		selectedLayerRange = view.selectedLayerRange()
		# note: if several glyphs are selected then this will move the whole selection.
		#       not sure whether this is useful but at least it is not an unexpected behaviour.
		if selectedLayerRange.location == len( tab.layers ) - 1:
			# the current glyph is the very last. let’s move to the very first:
			selectedLayerRange.location = 0
		else:
			# move one glyph right:
			selectedLayerRange.location += 1
		view.setSelectedLayerRange_(selectedLayerRange)
		# re-center glyph:
		vp = tab.viewPort
		vp.origin.x = tab.selectedLayerOrigin.x + 0.5 * ( layer.width * tab.scale - vp.size.width )
		tab.viewPort = vp
		# TODO: in case the new glyph is on a different line, also adjust y 

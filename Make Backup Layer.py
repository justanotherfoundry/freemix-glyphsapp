#MenuTitle: Make Backup Layer
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__="""
Same as the “Copy” button on the Layers palette but as a script. Because I really want a keyboard shortcut for this.

Without a keyboard shortcut this script is completely useless. Sorry.
"""

import datetime

for layer in Glyphs.font.selectedLayers:
	glyph = layer.parent
	newLayer = layer.copy()
	newLayer.name = datetime.datetime.now().strftime( "%b %-d %y, %H:%M" )
	glyph.layers.append( newLayer )

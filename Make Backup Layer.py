#MenuTitle: Make Backup Layer

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
Same as the “+” button on the Layers palette.

I wrote this script mostly because it allows me to assign a keyboard shortcut. Also, it correctly copies brace layers, unlike Glyphs’ built-in function.
'''

GSLayer.isBraceLayer = property(lambda self: bool(self.pyobjc_instanceMethods.isBraceLayer()),
								lambda self, value: self.setBraceLayer_(value) )

import datetime

for layer in Glyphs.font.selectedLayers:
	glyph = layer.parent
	newLayer = layer.copy()
	if newLayer.isSpecialLayer:
		newLayer.name = newLayer.name + datetime.datetime.now().strftime( " %b %-d %y, %H:%M" )
		del newLayer.attributes["axisRules"]
		del newLayer.attributes["coordinates"]
	else:
		newLayer.name = datetime.datetime.now().strftime( "%b %-d %y, %H:%M" )
	glyph.layers.append( newLayer )

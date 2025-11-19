#MenuTitle: Make Backup Layer

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
Same as the “+” button on the Layers palette.

I wrote this script mostly because it allows me to assign a keyboard shortcut. Also, it correctly copies brace layers, unlike Glyphs’ built-in function.
'''

import datetime
import Foundation

formatter = Foundation.NSDateFormatter.alloc().init()
formatter.setDateStyle_(Foundation.NSDateFormatterMediumStyle)
formatter.setTimeStyle_(Foundation.NSDateFormatterShortStyle)
now = Foundation.NSDate.date()
nowString = formatter.stringFromDate_(now).replace(' 202', ' 2')
# ^ seems to be the best way to create the same as Glyphs, as of now

for layer in Glyphs.font.selectedLayers:
	glyph = layer.parent
	newLayer = layer.copy()
	if newLayer.isSpecialLayer:
		newLayer.name = '{.} ' + nowString
		del newLayer.attributes["axisRules"]
		del newLayer.attributes["coordinates"]
	else:
		newLayer.name = nowString
	glyph.layers.append( newLayer )

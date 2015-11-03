#MenuTitle: Round Kerning
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

"""
Rounds the kerning values to full integer numbers.

In addition, values smaller than MIN_VALUE are erased.
"""

MIN_VALUE = 1

from GlyphsApp import *
font = Glyphs.font
master_id = font.selectedFontMaster.id

to_be_removed = []
for first, seconds in dict( font.kerning[master_id] ).items():
	if not first.startswith('@'):
		first = font.glyphForId_( first ).name
	for second in seconds:
		if not second.startswith('@'):
			second = font.glyphForId_( second ).name
		# round towards zero
		value = int( font.kerningForPair( master_id, first, second ) )
		if abs( value ) < MIN_VALUE:
			to_be_removed.append( ( first, second ) )
		else:
			font.setKerningForPair( master_id, first, second, value )

for first, second in to_be_removed:
	font.removeKerningForPair( master_id, first, second )

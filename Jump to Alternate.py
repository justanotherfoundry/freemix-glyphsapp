#MenuTitle: Jump to Alternate
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__="""
In the edit view, use this script to “jump” back and forth (or to circle)
between alternate glyphs such as one, one.lf and one.tosf.

Tip: Give it a keyboard shortcut!
"""

def jumpToAlternate():
	font = Glyphs.font
	currentTab = font.currentTab
	layers = currentTab.layers.values()

	string = NSMutableAttributedString.alloc().init()

	for i in xrange( len( layers ) ):
		layer = layers[i]
		try:
			char = font.characterForGlyph_( layer.parent )
		except:
			continue
		if i == currentTab.layersCursor:
			# the currently active glyph
			currGlyphName = layer.parent.name
			currBaseName = currGlyphName.split( '.', 1 )[0]
			if not currBaseName:
				# for example .notdef
				return
			alternates = []
			for glyph in font.glyphs:
				baseName = glyph.name.split( '.', 1 )[0]
				if currBaseName == baseName and not glyph.name.endswith( '.sc' ):
					alternates.append( glyph )
			assert( len( alternates ) >= 1 )
			if len( alternates ) == 1:
				# no others found
				return
			for a in xrange( len( alternates ) ):
				if alternates[a].name == currGlyphName:
					try:
						nextGlyph = alternates[a+1]
					except IndexError:
						nextGlyph = alternates[0]
			char = font.characterForGlyph_( nextGlyph )
			singleChar = NSAttributedString.alloc().initWithString_attributes_( unichr(char), {} )
		else:
			if layer.layerId == layer.associatedMasterId:
				singleChar = NSAttributedString.alloc().initWithString_attributes_( unichr(char), {} )
			else:
				# user-selected layer
				singleChar = NSAttributedString.alloc().initWithString_attributes_( unichr(char), { "GSLayerIdAttrib" : layer.layerId } )
		string.appendAttributedString_( singleChar )
	currentTab.layers._owner.graphicView().textStorage().setText_( string )

jumpToAlternate()

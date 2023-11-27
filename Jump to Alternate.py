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

from builtins import chr

def jumpToAlternate():
	font = Glyphs.font
	tab = font.currentTab
	# find new glyph:
	currentLayer = font.selectedLayers[0]
	currentGlyphName = currentLayer.parent.name
	currentBaseName = currentGlyphName.split( '.', 1 )[0]
	if not currentBaseName:
		# for example .notdef
		return
	alternates = []
	for glyph in font.glyphs:
		baseName = glyph.name.split( '.', 1 )[0]
		if currentBaseName == baseName and not glyph.name.endswith( '.sc' ):
			alternates.append( glyph )
	if len( alternates ) == 1:
		# no others found
		return
	for a in range( len( alternates ) ):
		if alternates[a].name == currentGlyphName:
			try:
				nextGlyph = alternates[a+1]
			except IndexError:
				nextGlyph = alternates[0]
	nextChar = chr( font.characterForGlyph( nextGlyph ) )
	# replace in display string:
	graphicView = tab.graphicView()
	textStorage = graphicView.textStorage()
	text = textStorage.text()
	selectedRange = graphicView.selectedRange()
	selectedRange.length = 1
	while 1:
		selectedRange.length += 1
		try:
			subString = text.attributedSubstringFromRange_( selectedRange )
		except IndexError:
			selectedRange.length -= 1
			break
		if len( subString.string() ) != 1:
			selectedRange.length -= 1
			break
	# note: selectedRange.length will be 2 if the (nominal) Unicode value of the glyph is four-byte
	#       (which is always the case for unencoded glyphs)
	
	textStorage.willChangeValueForKey_('text')
	text.replaceCharactersInRange_withString_( selectedRange, nextChar )
	textStorage.didChangeValueForKey_('text')

jumpToAlternate()

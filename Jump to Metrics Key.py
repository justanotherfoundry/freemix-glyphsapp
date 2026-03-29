#MenuTitle: Jump to Metrics Key

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
In the edit view, use this script to “jump” to the metrics key glyph (if any is used).

Tip: Give it a keyboard shortcut!
'''

from builtins import chr

def getMetricsKeyGlyph():
	font = Glyphs.font
	layer = font.selectedLayers[0]
	try:
		return font.glyphs[layer.leftMetricsKey.strip('=').strip('|')]
	except AttributeError:
		pass
	try:
		return font.glyphs[layer.rightMetricsKey.strip('=').strip('|')]
	except AttributeError:
		pass
	try:
		return font.glyphs[layer.parent.leftMetricsKey.strip('=').strip('|')]
	except AttributeError:
		pass
	try:
		return font.glyphs[layer.parent.rightMetricsKey.strip('=').strip('|')]
	except AttributeError:
		pass

def jumpToMetricsKey():
	font = Glyphs.font
	nextGlyph = getMetricsKeyGlyph()
	if not nextGlyph:
		return
	nextChar = chr(font.characterForGlyph(nextGlyph))
	if not nextChar:
		return
	# replace in display string:
	tab = font.currentTab
	graphicView = tab.graphicView()
	textStorage = graphicView.textStorage()
	text = textStorage.text()
	selectedRange = graphicView.selectedRange()
	selectedRange.length = 1
	while 1:
		selectedRange.length += 1
		try:
			subString = text.attributedSubstringFromRange_(selectedRange)
		except IndexError:
			selectedRange.length -= 1
			break
		if len(subString.string()) != 1:
			selectedRange.length -= 1
			break
	# note: selectedRange.length will be 2 if the (nominal) Unicode value of the glyph is four-byte
	#       (which is always the case for unencoded glyphs)
	textStorage.willChangeValueForKey_('text')
	text.replaceCharactersInRange_withString_(selectedRange, nextChar)
	textStorage.didChangeValueForKey_('text')

jumpToMetricsKey()

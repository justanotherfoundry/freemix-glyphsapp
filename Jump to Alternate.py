#MenuTitle: Jump to Alternate

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
In the edit view, use this script to “jump” back and forth (or to circle)
between alternate glyphs such as one, one.lf and one.tosf.

Tip: Give it a keyboard shortcut!

If several glyphs are selected you can choose to add or remove suffixes.
'''

from builtins import chr
import vanilla
from Foundation import NSString, NSMakeRange
font = Glyphs.font

def sharedSuffix(layers):
	suffix = None
	for layer in layers:
		try:
			glyphSuffix = layer.parent.name.split('.')[-1]
			if not suffix:
				suffix = glyphSuffix
			elif glyphSuffix != suffix:
				return None
		except IndexError:
			return None
	return suffix

def replaceInDisplayString(newString):
	newString = NSString.stringWithString_(newString)
	graphicView = font.currentTab.graphicView()
	selectedRange = graphicView.selectedRange()
	textSelectionLength = selectedRange.length
	if textSelectionLength == 0:
		# no text selection but we want to replace the current glyph,
		# i.e. to the right of the text cursor (which corresponds to font.selectedLayers)
		selectedRange.length = 1
	graphicView.replaceCharactersInRange_withString_(selectedRange, newString)
	if textSelectionLength != 0:
		graphicView.setSelectedRange_(NSMakeRange(selectedRange.location, newString.length()))

class JumpDialog(object):

	def __init__(self):
		windowWidth = 300
		windowHeight = 125
		try:
			self.layer = doc.selectedLayers()[0]
		except TypeError:
			self.layer = None
			return
		self.w = vanilla.FloatingWindow((windowWidth, windowHeight), 'Jump to Alternates', autosaveName='com.freemix.jump_to_alternate.mainwindow')
		leftMargin = 20
		rightMargin = -20
		elementHeight = 20
		posY = 12
		self.w.removeSuffixLabel = vanilla.TextBox((leftMargin, posY + 1, 115, elementHeight), "Remove suffix")
		self.w.removeSuffix = vanilla.EditText((120, posY, rightMargin, elementHeight))
		posY += elementHeight + 10
		self.w.addSuffixLabel = vanilla.TextBox((leftMargin, posY + 1, 115, elementHeight), "Add suffix")
		self.w.addSuffix = vanilla.EditText((120, posY, rightMargin, elementHeight))
		self.w.jumpButton = vanilla.Button((leftMargin, -40, -10, rightMargin), 'Replace with alternates', callback=self.buttonCallback)
		self.w.setDefaultButton(self.w.jumpButton)

	def buttonCallback(self, sender):
		newText = ''
		for layer in font.selectedLayers:
			glyph = layer.parent
			glyphName = glyph.name.replace(self.w.removeSuffix.get(), '')
			glyphName += self.w.addSuffix.get()
			nextGlyph = font.glyphs[glyphName]
			if nextGlyph:
				glyph = nextGlyph
			nextChar = chr(font.characterForGlyph(glyph))
			newText += nextChar
		replaceInDisplayString(newText)
		self.w.close()

def jumpToAlternate():
	if len(font.selectedLayers) > 1:
		dialog = JumpDialog()
		dialog.w.open()
		dialog.w.makeKey()
		suffix = sharedSuffix(font.selectedLayers)
		if suffix:
			dialog.w.removeSuffix.set('.' + suffix)
		return
	# find new glyph:
	try:
		currentLayer = font.selectedLayers[0]
	except IndexError:
		return
	currentGlyphName = currentLayer.parent.name
	currentBaseName = currentGlyphName.split('.', 1)[0]
	if not currentBaseName:
		# for example .notdef
		return
	alternates = []
	for glyph in font.glyphs:
		baseName = glyph.name.split('.', 1)[0]
		if (currentBaseName == baseName and not glyph.name.endswith('.sc')) or glyph == currentLayer.parent:
			# ^ the last condition ensures we add the current glyph (even if .sc) to the list of alterates
			alternates.append(glyph)
	if len(alternates) == 1:
		# no others found
		return
	for a in range(len(alternates)):
		if alternates[a].name == currentGlyphName:
			try:
				nextGlyph = alternates[a+1]
			except IndexError:
				nextGlyph = alternates[0]
	nextChar = chr(font.characterForGlyph(nextGlyph))
	replaceInDisplayString(nextChar)

jumpToAlternate()

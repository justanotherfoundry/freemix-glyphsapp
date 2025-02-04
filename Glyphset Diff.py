# MenuTitle: Glyphset Diff
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
Shows the glyphs that are not present in the other font.
'''

from GlyphsApp import Glyphs, Message
from Cocoa import NSPredicate

if len(Glyphs.documents) == 2:
	thisFont = Glyphs.documents[0].font
	otherFont = Glyphs.documents[1].font

	otherGlyphnames = set(otherFont.glyphNames())
	diff = [glyph.name for glyph in thisFont.glyphs if glyph.name not in otherGlyphnames]
	fontView = thisFont.fontView
	glyphsArrayController = fontView.glyphsArrayController()
	
	predicate = NSPredicate.predicateWithFormat_("name IN %@", diff)
	glyphsArrayController.setFilterPredicate_(predicate)
else:
	Message('Please make sure that\nexactly two fonts are open', '')

#MenuTitle: Select Inaccessible Glyphs
# encoding: utf-8

__doc__='''
Run this macro while in the Font View.

The macro selects all glyphs that
- export
- do not have a Unicode value and 
- are not covered by any OT feature

i.e. are not accessible in the final font.

These glyphs can usually be excluded from the final exported OTF font.

'''

from GlyphsApp import *
import re

doc = Glyphs.currentDocument
font = doc.font

# find all glyphs that are substitutions in the OT features, i.e. after the "sub ... by"

# collect all features and featurePrefixes
all_features = [ f.code for f in font.features ]
all_features.extend( [ f.code for f in font.featurePrefixes ] )

# put all into one string, without linebreaks, without brackets
features_text = ' '.join( ' '.join( all_features ).splitlines() ).replace( ']', ' ' ).replace( '[', ' ' )
# find substitutions via regex
substitutions = ' '.join( re.findall( r" by ([^;]*);", features_text ) ).split()

glyphs_inaccessible = [ glyph for glyph in font.glyphs if glyph.export and not glyph.name in substitutions and not glyph.name.startswith('.') and ( not glyph.glyphInfo or not glyph.glyphInfo.unicode ) ]

# select inaccessible glyphs (and deselect all others)
for glyph in font.glyphs:
	glyph.selected = glyph in glyphs_inaccessible

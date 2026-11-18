#MenuTitle: Expand Kerning

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
Converts the class kerning to glyph-glyph pairs
'''

from GlyphsApp import Glyphs

doc = Glyphs.currentDocument
font = doc.font
master_id = font.selectedFontMaster.id

# expand
flatKerning = []
for left_glyph in font.glyphs:
	if left_glyph.rightKerningGroup:
		left_name = '@MMK_L_' + left_glyph.rightKerningGroup
	else:
		left_name = left_glyph.name
	for right_glyph in font.glyphs:
		if right_glyph.leftKerningGroup:
			right_name = '@MMK_R_' + right_glyph.leftKerningGroup
		else:
			right_name = right_glyph.name
		value = font.kerningForPair( master_id, left_name, right_name )
		if value is not None and value != 0 and value < 77000:
			existing_value = font.kerningForPair( master_id, left_glyph.name, right_glyph.name )
			if existing_value is not None and existing_value < 77000:
				continue
			exception_value = font.kerningForPair( master_id, left_glyph.name, right_name )
			if exception_value is not None and exception_value < 77000:
				value = exception_value
			exception_value = font.kerningForPair( master_id, left_name, right_glyph.name )
			if exception_value is not None and exception_value < 77000:
				value = exception_value
			flatKerning.append((left_glyph.name, right_glyph.name, value))

# remove the existing kerning of this master
# (the kerning of the other masters is not touched)
id_to_name = { glyph.id: glyph.name for glyph in font.glyphs }
def kerning_name( key ):
	if key.startswith('@'):
		return key
	return id_to_name.get(key)
try:
	master_kerning = font.kerning[master_id]
except (KeyError, TypeError):
	master_kerning = None
# Glyphs returns None (rather than raising) for a master without kerning
master_kerning = master_kerning or {}
existing_pairs = [ ( kerning_name(left), kerning_name(right) ) for left in master_kerning for right in ( master_kerning[left] or {} ) ]
for left_side, right_side in existing_pairs:
	if left_side and right_side:
		font.removeKerningForPair( master_id, left_side, right_side )

print(len(flatKerning), 'flat kerning pairs')
for left_glyph_name, right_glyph_name, value in flatKerning:
	font.setKerningForPair( master_id, left_glyph_name, right_glyph_name, value )

#MenuTitle: Expand Kerning
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

'''
Expand Kerning like we know it from FontLab.

'''

doc = Glyphs.currentDocument
font = doc.font
master_id = font.selectedFontMaster.id

right_groups = set( [ '@MMK_R_' + glyph.leftKerningGroup for glyph in font.glyphs if glyph.leftKerningGroup ] )
left_groups = set( [ '@MMK_L_' + glyph.rightKerningGroup for glyph in font.glyphs if glyph.rightKerningGroup ] )
glyph_names = set( [ glyph.name for glyph in font.glyphs ] )
right_sides = right_groups.union( glyph_names )

# expand
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
		if value is not None and value < 77000:
			existing_value = font.kerningForPair( master_id, left_glyph.name, right_glyph.name )
			if existing_value is not None and existing_value < 77000:
				continue
			exception_value = font.kerningForPair( master_id, left_glyph.name, right_name )
			if exception_value is not None and exception_value < 77000:
				value = exception_value
			exception_value = font.kerningForPair( master_id, left_name, right_glyph.name )
			if exception_value is not None and exception_value < 77000:
				value = exception_value
			font.setKerningForPair( master_id, left_glyph.name, right_glyph.name, value )

# remove group kerning
for left_side in left_groups:
	for right_side in right_sides:
		font.removeKerningForPair( master_id, left_side, right_side )
for left_side in glyph_names:
	for right_side in right_groups:
		font.removeKerningForPair( master_id, left_side, right_side )

# remove kerning groups
# (TODO)

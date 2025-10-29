#MenuTitle: Expand Kerning

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
Converts the class kerning to glyph-glyph pairs
'''

doc = Glyphs.currentDocument
font = doc.font
master_id = font.selectedFontMaster.id

right_groups = set( [ '@MMK_R_' + glyph.leftKerningGroup for glyph in font.glyphs if glyph.leftKerningGroup ] )
left_groups = set( [ '@MMK_L_' + glyph.rightKerningGroup for glyph in font.glyphs if glyph.rightKerningGroup ] )
glyph_names = set( [ glyph.name for glyph in font.glyphs ] )
right_sides = right_groups.union( glyph_names )

# expand
flatKerning = { master_id: {} }
kerningDict = flatKerning[master_id]
for leftGlyph in font.glyphs:
	leftLayer = leftGlyph.layers[master_id]
	for rightGlyph in font.glyphs:
		rightLayer = rightGlyph.layers[master_id]
		kernValue = font.kerningFirstLayer_secondLayer_(leftLayer, rightLayer)

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
			try:
				glyphKerningDict = kerningDict[left_glyph.id]
			except KeyError:
				kerningDict[left_glyph.id] = {}
				glyphKerningDict = kerningDict[left_glyph.id]
# 			glyphKerningDict[right_glyph.id] = value
# 			font.setKerningForPair( master_id, left_glyph.name, right_glyph.name, value )
			flatKerning.append((left_glyph.name, right_glyph.name, value))

font.kerning = {}
print(len(flatKerning), 'flat kerning pairs')
for left_glyph_name, right_glyph_name, value in flatKerning:
	font.setKerningForPair( master_id, left_glyph_name, right_glyph_name, value )

# remove kerning groups
# (TODO)

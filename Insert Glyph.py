#MenuTitle: Insert Glyph
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__="""
1. Enter a glyph name.
2. Press the left align or right align button.
3. This script will clear the mask, then insert the specified glyph into the mask.

- With right align selected, the contours will be pasted as if the advance widths were aligned.
- The keyboard shortcuts for left and right aligned are Enter and Esc.
- It is sufficient to enter the beginning of the glyph name, e.g. "deg" for "degree".

"""

from vanilla import Window, EditText, Button

LEFT = '<'
RIGHT = '>'

font = Glyphs.font

def insert_paths( to_layer, from_layer, alignment = LEFT ):
	# insert all paths
	for path in from_layer.copyDecomposedLayer().paths:
		if alignment == RIGHT:
			shift = to_layer.width - from_layer.width
			for node in path.nodes:
				node.x = node.x + shift
		to_layer.paths.append( path )
		# select path (makes is quicker to move around the shape later)
		to_layer.paths[-1].selected = True

class GlyphnameDialog( object):

	def __init__( self ):
		x = 10
		y = 10
		height = 20
		button_width = 30
		glyphname_width = 180
		gap = 6
		self.w = Window( ( x + button_width + gap + glyphname_width + gap + button_width + x, y + height + y ), "insert glyph" )
		self.w.center()
		self.w.glyphname = EditText( ( x, y, glyphname_width, height ), '')
		x += glyphname_width + gap
		self.w.alignleft = Button( ( x, y, button_width, height ), LEFT, callback = self.buttonCallback )
		x += button_width + gap
		self.w.alignright = Button( ( x, y, button_width, height ), RIGHT, callback = self.buttonCallback )
		self.w.setDefaultButton( self.w.alignleft )
		self.w.alignright.bind( "\x1b", [] )
		self.w.open()

	def buttonCallback( self, sender ):
		title = sender.getTitle()
		glyphname = self.w.glyphname.get()
		if not glyphname:
			self.w.close()
			return
		if len( glyphname ) == 1:
			uni = ord(glyphname)
			g = font.glyphForUnicode_("%.4X" % uni)
			if g:
				glyphname = g.name
		other_glyph = font.glyphs[ glyphname ]
		if not other_glyph:
			for glyph in font.glyphs:
				if glyph.name.startswith( glyphname ):
					other_glyph = glyph
					break
			else:
				print 'No matching glyph found.'
				self.w.close()
				return
		
		for layer in font.selectedLayers:
			glyph = layer.parent
			glyph.beginUndo()
			# deselect all
			for path in layer.paths:
				for node in path.nodes:
					layer.removeObjectFromSelection_( node )
			# find other layer
			for other_layer in other_glyph.layers:
				if other_layer.name == layer.name:
					# insert paths
					for path in other_layer.copyDecomposedLayer().paths:
						if title == RIGHT:
							shift = layer.width - other_layer.width
							for node in path.nodes:
								node.x = node.x + shift
						layer.paths.append( path )
						# select path
						layer.paths[-1].selected = True
					break
			glyph.endUndo()
		self.w.close()

GSSelectGlyphsDialogController = objc.lookUpClass("GSSelectGlyphsDialogController")
selectGlyphPanel = GSSelectGlyphsDialogController.alloc().init()
selectGlyphPanel.setTitle_("Find Glyphs")

master = Font.masters[0] # Pick with master you are interested in, e.g., currentTab.masterIndex
selectGlyphPanel.setMasterID_(master.id)
selectGlyphPanel.setContent_(list(Font.glyphs))
PreviousSearch = Glyphs.defaults["PickGlyphsSearch"]
if PreviousSearch and len(PreviousSearch) > 0:
	selectGlyphPanel.setSearch_(PreviousSearch)

if selectGlyphPanel.runModal():
	alignment = LEFT
	Glyphs.defaults["PickGlyphsSearch"] = selectGlyphPanel.glyphsSelectSearchField().stringValue()
	other_glyph = selectGlyphPanel.selectedGlyphs()[0]
else:
	alignment = RIGHT
	glyphname =  selectGlyphPanel.glyphsSelectSearchField().stringValue()
	other_glyph = font.glyphs[ glyphname ]
for layer in font.selectedLayers:
	glyph = layer.parent
	glyph.beginUndo()
	# deselect all
	for path in layer.paths:
		for node in path.nodes:
			layer.removeObjectFromSelection_( node )
	# find other layer
	for other_layer in other_glyph.layers:
		if other_layer.name == layer.name:
			insert_paths( layer, other_layer, alignment )
			'''
			# insert paths
			for path in other_layer.copyDecomposedLayer().paths:
				if alignment == RIGHT:
					shift = layer.width - other_layer.width
					for node in path.nodes:
						node.x = node.x + shift
				layer.paths.append( path )
				# select path
				for node in layer.paths[-1].nodes:
					layer.addSelection_( node )
			'''
			break
	else:
		insert_paths( layer, other_glyph.layers[layer.associatedMasterId], alignment )
	glyph.endUndo()


# GlyphnameDialog()

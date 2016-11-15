#MenuTitle: Insert Glyph to Background
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

"""
1. Enter a glyph name.
2. Press the left align or right align button.
3. This script will clear the mask, then insert the specified glyph into the mask.

- With right align selected, the contours will be pasted as if the advance widths were aligned.
- The keyboard shortcuts for left and right aligned are Enter and Esc.
- It is sufficient to enter the beginning of the glyph name, e.g. "deg" for "degree".

"""

from GlyphsApp import *
from vanilla import *

LEFT = '<'
RIGHT = '>'

font = Glyphs.font
active_layerId = Glyphs.font.selectedLayers[0].layerId

def insert_paths( to_layer, from_layer, alignment = LEFT ):
	# clear layer
	to_layer.background.clear()
	# insert all paths
	for path in from_layer.copyDecomposedLayer().paths:
		if alignment == RIGHT:
			shift = to_layer.width - from_layer.width
			for node in path.nodes:
				node.x = node.x + shift
		to_layer.background.paths.append( path )
		# select path (makes is quicker to move around the shape later)
		to_layer.background.paths[-1].selected = True

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
		alignment = sender.getTitle()
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
					print 'Using', glyph.name
					break
			else:
				print 'No matching glyph found.'
				self.w.close()
				return
		
		selected_glyphs = set( [ layer.parent for layer in font.selectedLayers ] )
		
		for glyph in selected_glyphs:
			glyph.beginUndo()
			for layer in glyph.layers:
				# find other layer
				for other_layer in other_glyph.layers:
					if other_layer.name == layer.name:
						insert_paths( layer, other_layer, alignment )
						break
				else:
					if active_layerId == layer.layerId:
						insert_paths( layer, other_glyph.layers[layer.associatedMasterId], alignment )
			glyph.endUndo()
		self.w.close()

GlyphnameDialog()

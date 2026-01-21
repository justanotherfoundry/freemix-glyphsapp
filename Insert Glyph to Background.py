#MenuTitle: Insert Glyph to Background

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
1. Enter a glyph name.
2. Press the left align or right align button.
3. This script will clear the mask, then insert the specified glyph into the mask.

• With right align selected, the contours will be pasted as if the advance widths were aligned.

• The keyboard shortcuts for left and right aligned are Enter and Esc.

• It is sufficient to enter the beginning of the glyph name, e.g. “deg” for “degree”.
'''

from vanilla import Window, EditText, Button, CheckBox
from AppKit import NSPoint, NSTextField, NSButton, NSBeep

LEFT = '<'
RIGHT = '>'

font = Glyphs.font
active_layerId = Glyphs.font.selectedLayers[0].layerId

def insert_paths( to_layer, from_layer, alignment, as_component, clear_contents ):
	# clear layer
	if clear_contents:
		to_layer.background.clear()
	if as_component:
		# insert as component
		shift = ( to_layer.width - from_layer.width ) if alignment == RIGHT else 0
		from_glyph_name = from_layer.parent.name
		to_layer.background.components.append( GSComponent( from_glyph_name, NSPoint( shift, 0 ) ) )
		# select component (makes is quicker to move around the shape later)
		try:
			# Glyphs 3
			to_layer.background.shapes[-1].selected = True
		except:
			# Glyphs 2
			if to_layer.background.components:
				to_layer.background.components[-1].selected = True
	else:
		# insert all paths
		for path in from_layer.copyDecomposedLayer().paths:
			if alignment == RIGHT:
				shift = to_layer.width - from_layer.width
				for node in path.nodes:
					node.x = node.x + shift
			try:
				# Glyphs 3
				to_layer.background.shapes.append( path )
				to_layer.background.shapes[-1].selected = True
			except:
				# Glyphs 2
				to_layer.background.paths.append( path )
				to_layer.background.paths[-1].selected = True

class GlyphnameDialog( object):

	def __init__( self ):
		self.selected_glyphs = set( [ layer.parent for layer in font.selectedLayers ] )
		hori_margin = 10
		verti_margin = hori_margin
		button_width = 30
		glyphname_width = 180
		line_height = 20
		gap = 9
		dialog_height = line_height + gap + line_height + gap + line_height
		dialog_width = button_width + gap + glyphname_width + gap + button_width
		self.w = Window( ( hori_margin + dialog_width + hori_margin, verti_margin + dialog_height + verti_margin ), "insert glyph" )
		self.w.center()
		x = hori_margin
		y = verti_margin
		# glyph name
		self.w.glyphname = EditText( ( x, y, glyphname_width, line_height ), '')
		self.w.glyphname.getNSTextField().setToolTip_( u'Enter the name of the glyph to be inserted. It is sufficient to enter the beginning of the glyph name, e.g. “deg” for “degree”.' )
		# buttons
		x += glyphname_width + gap
		self.w.alignleft = Button( ( x, y, button_width, line_height ), LEFT, callback = self.buttonCallback )
		self.w.alignleft.getNSButton().setToolTip_( 'Insert the other glyph left-aligned, i.e. at its original same position. Keyboard shortcut: Enter' )
		x += button_width + gap
		self.w.alignright = Button( ( x, y, button_width, line_height ), RIGHT, callback = self.buttonCallback )
		self.w.alignright.getNSButton().setToolTip_( 'Insert the other glyph right-aligned with respect to the advance widths. Keyboard shortcut: Esc' )
		self.w.setDefaultButton( self.w.alignleft )
		self.w.alignright.bind( "\x1b", [] )
		# quick-insert
		self.find_metrics_keys()
		self.find_suffixless()
		if self.lmk or self.rmk:
			y += line_height + gap
			quick_button_width = dialog_width / 2 - hori_margin / 2
			if self.lmk:
				x = hori_margin
				self.w.quickleft = Button( ( x, y, quick_button_width, line_height ), LEFT + ' ' + self.lmk, callback = self.buttonCallback )
			if self.rmk:
				x = hori_margin + ( dialog_width + hori_margin ) / 2
				self.w.quickright = Button( ( x, y, quick_button_width, line_height ), self.rmk + ' ' + RIGHT, callback = self.buttonCallback )
		# insert as component
		as_component_is_checked = True
		if Glyphs.defaults["com.FMX.InsertGlyphToBackground.AsCompoment"]  is not None:
			as_component_is_checked = Glyphs.defaults["com.FMX.InsertGlyphToBackground.AsCompoment"]
		y += line_height + gap
		x = hori_margin
		self.w.as_component = CheckBox( ( x, y, dialog_width, line_height ), 'Insert as component', callback=None, value=as_component_is_checked )
		self.w.as_component.getNSButton().setToolTip_( 'If checked, the other glyph is inserted to the background as a component. Otherwise, it is inserted as paths (even if the other glyph is made of components).' )
		# clear current contents
		y += line_height + gap
		clear_contents_is_checked = True
		if Glyphs.defaults["com.FMX.InsertGlyphToBackground.ClearContents"]  is not None:
			clear_contents_is_checked = Glyphs.defaults["com.FMX.InsertGlyphToBackground.ClearContents"]
		self.w.clear_contents = CheckBox( ( x, y, dialog_width, line_height ), 'Clear current contents', callback=None, value=clear_contents_is_checked )
		self.w.clear_contents.getNSButton().setToolTip_( 'Check this to clear the background before inserting the other glyph. Uncheck to keep the current contents of the background.' )
		self.w.open()

	def find_metrics_keys( self ):
		self.lmk = None
		self.rmk = None
		for glyph in self.selected_glyphs:
			try:
				if font.glyphs[glyph.leftMetricsKey]:
					self.lmk = glyph.leftMetricsKey
			except TypeError:
				pass
			try:
				if font.glyphs[glyph.rightMetricsKey]:
					self.rmk = glyph.rightMetricsKey
			except TypeError:
				pass
	
	def find_suffixless( self ):
		if self.lmk or self.rmk:
			return
		for glyph in self.selected_glyphs:
			name_components = glyph.name.split('.')
			if len(name_components) > 1:
				basename = name_components[0]
				try:
					if font.glyphs[basename]:
						self.lmk = basename
						self.rmk = basename
				except TypeError:
					pass
			break
	
	def buttonCallback( self, sender ):
		alignment = sender.getTitle()
		glyphname = self.w.glyphname.get().strip(" /")
		if len( alignment ) != 1:
			# this implies that a quick-insert button was pressed
			title_split = alignment.split()
			assert len( title_split ) == 2
			if title_split[0] == LEFT:
				alignment = LEFT
				glyphname = title_split[1]
			else:
				assert title_split[1] == RIGHT
				alignment = RIGHT
				glyphname = title_split[0]
		as_component_is_checked = self.w.as_component.get()
		clear_contents_is_checked = self.w.clear_contents.get()
		if not glyphname:
			self.w.close()
			return
		if len( glyphname ) == 1:
			uni = ord(glyphname)
			g = font.glyphForUnicode_("%.4X" % uni)
			if g:
				glyphname = g.name
		try:
			this_glyph = font.selectedLayers[0].parent
		except IndexError:
			return
		other_glyph = font.glyphs[ glyphname ]
		if not other_glyph:
			# this means the user typed only the beginning of the intended glyph’s name
			for glyph in font.glyphs:
				if glyph.name.startswith( glyphname ) and not glyph.name == this_glyph.name:
					other_glyph = glyph
					break
			else:
				NSBeep()
				self.w.close()
				return
		for glyph in self.selected_glyphs:
			glyph.beginUndo()
			for layer in glyph.layers:
				# find other layer
				for other_layer in other_glyph.layers:
					if other_layer.name == layer.name:
						insert_paths( layer, other_layer, alignment, as_component_is_checked, clear_contents_is_checked )
						break
				else:
					if layer.isBraceLayer():
						# the corresponding brace layer was not found in other_glyph.
						# let’s interpolate it on-the-fly:
						other_glyph_copy = other_glyph.copy()
						other_glyph_copy.setUndoManager_(None)
						other_glyph_copy.parent = font
						# ^ Glyphs needs the font’s master coordinates for the re-interpolation
						interpolatedLayer = layer.copy()
						# ^ in Glyphs 3, it seems starting with a blank GSLayer() does not work.
						interpolatedLayer.name = layer.name
						# ^ necessary for the re-interpolation
						other_glyph_copy.layers.append( interpolatedLayer )
						interpolatedLayer.reinterpolate()
						insert_paths( layer, interpolatedLayer, alignment, as_component = False, clear_contents = clear_contents_is_checked )
					elif active_layerId == layer.layerId:
						insert_paths( layer, other_glyph.layers[layer.associatedMasterId], alignment, as_component_is_checked, clear_contents_is_checked )
			glyph.endUndo()
		Glyphs.defaults["com.FMX.InsertGlyphToBackground.AsCompoment"] = as_component_is_checked
		Glyphs.defaults["com.FMX.InsertGlyphToBackground.ClearContents"] = clear_contents_is_checked
		self.w.close()

GlyphnameDialog()

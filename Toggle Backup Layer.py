#MenuTitle: Toggle Backup Layer
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__="""
This script toggles between the master layer and
the last backup layer in the list.

Given a keyboard shortcut, this is useful for
comparing two versions of a glyph.

"""

from GlyphsApp import *

font = Glyphs.font
currentTab = font.currentTab
layers = currentTab.layers.values()

string = NSMutableAttributedString.alloc().init()
for i in xrange( len( layers ) ):
	layer = layers[i]
	try:
		char = font.characterForGlyph_( layer.parent )
	except:
		continue
	# initialise single char without attributes
	# which switches the glyph to the active master
	singleChar = NSAttributedString.alloc().initWithString_attributes_( unichr(char), {} )
	if i == currentTab.layersCursor:
		# we are at the currently active glyph
		if layer.layerId == font.selectedFontMaster.id:
			# current layer is the selected master layer.
			# switch current glyph to the last associated non-master layer.
			for glyphLayer in layer.parent.layers:
				if glyphLayer.associatedMasterId == font.selectedFontMaster.id:
					# this may happen multiple times
					singleChar = NSAttributedString.alloc().initWithString_attributes_( unichr(char), { "GSLayerIdAttrib" : glyphLayer.layerId } )
	else:
		if layer.layerId != layer.associatedMasterId:
			# user-selected layer
			singleChar = NSAttributedString.alloc().initWithString_attributes_( unichr(char), { "GSLayerIdAttrib" : layer.layerId } )
	string.appendAttributedString_( singleChar )
currentTab.layers._owner.graphicView().textStorage().setText_(string)

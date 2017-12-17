#MenuTitle: Toggle Backup Layer
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__="""
This script toggles between the currently selected layer and the master layer (alternatively, between the master and the last backup layer in the list).

If given a keyboard shortcut, this is very useful for comparing two versions of a glyph.
"""

from GlyphsApp import *

font = Glyphs.font
currentTab = font.currentTab
layers = currentTab.layers.values()
try:
	backupLayerId
except NameError:
	backupLayerId = None

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
			foundBackupLayer = False
			if backupLayerId:
				# try to switch current glyph to the stored backupLayerId
				for glyphLayer in layer.parent.layers:
					if glyphLayer.layerId == backupLayerId:
						# do not switch to layers that belong to a different master
						if glyphLayer.associatedMasterId == font.selectedFontMaster.id:
							singleChar = NSAttributedString.alloc().initWithString_attributes_( unichr(char), { "GSLayerIdAttrib" : glyphLayer.layerId } )
							foundBackupLayer = True
							break
			if not foundBackupLayer:
				backupLayerId = None
				# switch current glyph to the last associated non-master layer.
				for glyphLayer in layer.parent.layers:
					if glyphLayer.associatedMasterId == font.selectedFontMaster.id and glyphLayer.layerId != font.selectedFontMaster.id:
						# this may happen multiple times
						singleChar = NSAttributedString.alloc().initWithString_attributes_( unichr(char), { "GSLayerIdAttrib" : glyphLayer.layerId } )
						backupLayerId = glyphLayer.layerId
		else:
			# current layer is a backup layer
			backupLayerId = layer.layerId
	else:
		if layer.layerId != layer.associatedMasterId:
			# user-selected layer
			singleChar = NSAttributedString.alloc().initWithString_attributes_( unichr(char), { "GSLayerIdAttrib" : layer.layerId } )
	string.appendAttributedString_( singleChar )
currentTab.layers._owner.graphicView().textStorage().setText_(string)

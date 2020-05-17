#MenuTitle: Toggle Backup Layer
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__="""
This script toggles between the currently selected layer and the master layer (alternatively, between the master and the last backup layer in the list).

If given a keyboard shortcut, this is very useful for comparing two versions of a glyph.
"""

from AppKit import NSAttributedString, NSMutableAttributedString

font = Glyphs.font
masterId = font.selectedFontMaster.id
currentTab = font.currentTab
rawTextLayers = currentTab.layers
layers = currentTab.composedLayers
try:
	backupLayerId
except NameError:
	backupLayerId = None

string = NSMutableAttributedString.alloc().init()
i_composed = -1
i_raw = -1
while i_composed < len( layers ) - 1:
	i_raw += 1
	i_composed += 1
	while rawTextLayers[i_raw].parent.name != layers[i_composed].parent.name:
		i_composed += 1
		if i_composed >= len( layers ):
			break
		for i_raw_candidate in range( i_raw, len( layers ) ):
			if rawTextLayers[i_raw_candidate].parent.name == layers[i_composed].parent.name:
				for i_raw_add in range( i_raw, i_raw_candidate ):
					rawTextGlyph = rawTextLayers[i_raw_add].parent
					try:
						char = font.characterForGlyph_( rawTextGlyph )
					except:
						continue
					singleChar = NSAttributedString.alloc().initWithString_attributes_( unichr(char), {} )
					string.appendAttributedString_( singleChar )
				i_raw = i_raw_candidate
				break
	if i_composed >= len( layers ):
		break
	rawTextGlyph = rawTextLayers[i_raw].parent
	try:
		char = font.characterForGlyph_( rawTextGlyph )
	except:
		continue
	# initialise single char without attributes
	# which switches the glyph to the active master
	singleChar = NSAttributedString.alloc().initWithString_attributes_( unichr(char), {} )
	layer = rawTextLayers[i_raw]
	if i_composed == currentTab.layersCursor:
		# we are at the currently active glyph
		if layer.layerId == masterId:
			# current layer is the selected master layer.
			foundBackupLayer = False
			if backupLayerId:
				# try to switch current glyph to the stored backupLayerId
				for glyphLayer in layer.parent.layers:
					if glyphLayer.layerId == backupLayerId:
						# do not switch to layers that belong to a different master
						if glyphLayer.associatedMasterId == masterId:
							singleChar = NSAttributedString.alloc().initWithString_attributes_( unichr(char), { "GSLayerIdAttrib" : glyphLayer.layerId } )
							foundBackupLayer = True
							break
			if not foundBackupLayer:
				backupLayerId = None
				# switch current glyph to the last associated non-master layer.
				for glyphLayer in layer.parent.layers:
					if glyphLayer.associatedMasterId == masterId and glyphLayer.layerId != masterId:
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

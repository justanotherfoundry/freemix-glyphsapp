# MenuTitle: Delete Zero-Thickness Hints
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

from __future__ import division, print_function, unicode_literals
from GlyphsApp import Glyphs, Message


__doc__ = '''
Removes all zero-thickness,
or otherwise invalid hints
from all glyphs in the font.
'''

doc = Glyphs.currentDocument
font = doc.font

deletions_count = 0
for glyph in font.glyphs:
	for layer in glyph.layers:
		for indx in range( len( layer.hints ) - 1, -1, -1 ):
			hint = layer.hints[indx]
			if hint.originNode is None:
				# this is an invalid hint that was probably set by Glyphs’ auto-instructing
				print( "deleting invalid hint from", layer.parent.name )
				del layer.hints[indx]
				deletions_count += 1
				continue
			if hint.targetNode:
				if hint.horizontal:
					if hint.originNode.y == hint.targetNode.y:
						del layer.hints[indx]
						deletions_count += 1
						print( 'deleted zero-width hint from', glyph.name )
				else:
					if hint.originNode.x == hint.targetNode.x:
						del layer.hints[indx]
						deletions_count += 1
						print( 'deleted zero-width hint from', glyph.name )


Message( '', 'Deleted %i hints.' % deletions_count )

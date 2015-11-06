#MenuTitle: Mask to Master
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

'''
Simulates the good ol' Mask to Master function we know from FontLab
(i.e. replaces the current outline with the background).

You can give it the familiar Cmd+J shortcut via App Shortcuts
in the Mac OS System Preferences.
'''

from GlyphsApp import *
import sys

def counterparts( selection, background ):
	len_selection = len( selection )
	best_point_range = []
	best_deviation = sys.maxint
	# search in each path
	for bg_path in background.paths:
		bg_nodes = bg_path.nodes
		# try each starting point
		for start in range( len( bg_nodes ) ):
			indx = start
			deviation = 0
			point_range = []
			# calculate deviation
			for node in selection:
				bg_node = bg_nodes[indx]
				if node.type != bg_node.type:
					break
				deviation += abs( node.x - bg_node.x )
				deviation += abs( node.y - bg_node.y )
				if deviation > best_deviation:
					break
				point_range.append( bg_node )
				# increase index looping around
				indx = ( indx + 1 ) % len( bg_nodes )
			else:
				best_deviation = deviation
				best_point_range = point_range
	return zip( selection, best_point_range )

layer = Glyphs.font.selectedLayers[0]
glyph = layer.parent
selection = [ node for path in layer.paths for node in path.nodes if node in layer.selection ]

# if the selection contains the starting node: re-arrange selection to be consecutive
for path in layer.paths:
	if path.nodes[0] in layer.selection:
		first_node = 0
		while path.nodes[first_node-1] in layer.selection:
			first_node -= 1
			selection.insert( 0, selection.pop() )
		break

glyph.beginUndo()

if selection:
	for node, bg_node in counterparts( selection, layer.background ):
		node.position = bg_node.position
else:
	# delete all paths
	while layer.paths:
		del(layer.paths[0])
	# insert background
	for path in layer.copyDecomposedLayer().background.paths:
		# copy across path
		layer.paths.append( path )
glyph.endUndo()

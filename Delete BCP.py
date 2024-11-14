#MenuTitle: Delete BCP
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__='''
This literally deletes the selected BCP(s):
If you delete one of the two BCPs in a cubic curve then it becomes quadratic.
'''

for selectedLayer in Glyphs.currentDocument.selectedLayers():
	glyph = selectedLayer.parent
	glyph.beginUndo()
	for layer in glyph.layers:
		for path in layer.paths:
			for i in range(len(path.nodes) - 1, -1, -1):
				node = path.nodes[i]
				if node.selected and node.type == OFFCURVE:
					if node.nextNode.type == OFFCURVE:
						# node is the first cubic BCP
						node.nextNode.nextNode.type = QCURVE
						if node.position == node.prevNode.position:
							# to-be-deleted BCP is retracted
							bcp = node.nextNode.position
							h2_x = node.nextNode.nextNode.position.x - bcp.x
							h2_y = node.nextNode.nextNode.position.y - bcp.y
							bcp.x = round( node.nextNode.nextNode.position.x - h2_x * 0.9 )
							bcp.y = round( node.nextNode.nextNode.position.y - h2_y * 0.9 )
							node.nextNode.position = bcp
					elif node.prevNode.type == OFFCURVE:
						# node is the second cubic BCP
						node.nextNode.type = QCURVE
						if node.position == node.nextNode.position:
							bcp = node.prevNode.position
							h1_x = bcp.x - node.prevNode.prevNode.position.x
							h1_y = bcp.y - node.prevNode.prevNode.position.y
							bcp.x = round( node.prevNode.prevNode.position.x + h1_x * 0.9 )
							bcp.y = round( node.prevNode.prevNode.position.y + h1_y * 0.9 )
							node.prevNode.position = bcp
					else:
						# curve is quadratic and is becoming a straight line
						node.nextNode.type = LINE
						node.nextNode.smooth = False
						node.prevNode.smooth = False
					del path.nodes[i]
	glyph.endUndo()

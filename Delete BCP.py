#MenuTitle: Delete BCP
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__='''
Deletes the selected BCP(s).
If only one BCP in the curve remains then this makes it a quadratic Bézier.
'''

doc = Glyphs.currentDocument
layers = doc.selectedLayers()

for layer in layers:
	glyph = layer.parent
	glyph.beginUndo()
	for path in layer.paths:
		for i in range(len(path.nodes) - 1, -1, -1):
			node = path.nodes[i]
			if node.selected and node.type == OFFCURVE:
				if node.nextNode.type == OFFCURVE:
					# node is the first cubic BCP
					node.nextNode.nextNode.type = QCURVE
				elif node.prevNode.type == OFFCURVE:
					# node is the second cubic BCP
					node.nextNode.type = QCURVE
				else:
					# curve is quadratic and is becoming a straight line
					node.nextNode.type = LINE
					node.nextNode.smooth = False
					node.prevNode.smooth = False
				del path.nodes[i]
	glyph.endUndo()

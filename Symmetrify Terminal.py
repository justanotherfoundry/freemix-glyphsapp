#MenuTitle: Symmetrify Terminal
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__='''
	Select a stroke end (i.e. the two nodes). This script makes the terminal perpendicular (symmetrical).
'''

import math

def samePosition(node1, node2):
	return node1.position.x == node2.position.x and node1.position.y == node2.position.y

def intersection(p1, p2, p3, p4):
	x1, y1 = p1
	x2, y2 = p2
	x3, y3 = p3
	x4, y4 = p4
	A1 = y2 - y1
	B1 = x1 - x2
	C1 = A1 * x1 + B1 * y1
	A2 = y4 - y3
	B2 = x3 - x4
	C2 = A2 * x3 + B2 * y3
	det = A1 * B2 - A2 * B1
	if det == 0:
		# lines are parallel
		return None
	x = (B2 * C1 - B1 * C2) / det
	y = (A1 * C2 - A2 * C1) / det
	return (x, y)

def vPlus(v1, v2):
	x1, y1 = v1
	x2, y2 = v2
	return (x1 + x2, y1 + y2)

def vMinus(v1, v2):
	x1, y1 = v1
	x2, y2 = v2
	return (x1 - x2, y1 - y2)

def vMult(v, s):
	x, y = v
	return (x * s, y * s)

def vectorLengthSquared(v):
	x, y = v
	return x * x + y * y

def vectorLength(v):
	x, y = v
	return math.sqrt(x * x + y * y)

def pointDist(p1, p2):
	return vectorLength(vMinus(p1, p2))

def dotProduct(v1, v2):
	x1, y1 = v1
	x2, y2 = v2
	return x1 * x2 + y1 * y2

def aligned(v1, v2):
	x1, y1 = v1
	x2, y2 = v2
	if x2 == 0:
		return (0, y1)
	elif y2 == 0:
		return (x1, 0)
	else:
		return vMult(v2, dotProduct(v1, v2) / vectorLengthSquared(v2))

def rounded(v):
	x, y = v
	return (round(x), round(y))

def setNodePosition(node, p):
	pos = node.position
	pos.x, pos.y = p
	node.position = pos

for selectedLayer in Font.selectedLayers:
	glyph = selectedLayer.parent
	for path in selectedLayer.paths:
		for node in path.nodes:
			if node.selected and node.nextNode.selected:
				n0 = node.prevNode
				n1 = node
				n2 = n1.nextNode
				n3 = n2.nextNode
				if samePosition(n0, n1):
					# retracted BCP
					n0 = n0.prevNode
				if samePosition(n2, n3):
					# retracted BCP
					n3 = n3.nextNode
				p0 = (n0.position.x, n0.position.y)
				p1 = (n1.position.x, n1.position.y)
				p2 = (n2.position.x, n2.position.y)
				p3 = (n3.position.x, n3.position.y)
				vertex = intersection(p0, p1, p2, p3)
				if vertex and pointDist(p1, vertex) > 32000:
					vertex = None
				if vertex:
					v1 = vMinus(p1, vertex)
					v2 = vMinus(p2, vertex)
					d1 = vectorLength(v1)
					d2 = vectorLength(v2)
					d_new = (d1 + d2) / 2
					f1 = d_new / d1
					f2 = d_new / d2
					p1_new = vPlus(vertex, vMult(v1, f1))
					p2_new = vPlus(vertex, vMult(v2, f2))
				else:
					v1 = vMinus(p1, p0)
					v12 = vMinus(p2, p1)
					v1_shift = vMult(aligned(v12, v1), 0.5)
					p1_new = vPlus(p1, v1_shift)
					p2_new = vMinus(p2, v1_shift)
				if Font.grid != 0:
					p1_rounded = rounded(p1_new)
					p2_rounded = rounded(p2_new)
					p1_roundingError = vMinus(p1_rounded, p1_new)
					p2_roundingError = vMinus(p2_rounded, p2_new)
					if vectorLengthSquared(p1_roundingError) < vectorLengthSquared(p2_roundingError):
						# use p1_rounded (as it has a smaller rounding error):
						setNodePosition(n1, p1_rounded)
						if vertex:
							# tweak v2 so as to adopt the rounding error:
							v2 = vPlus(v2, p1_roundingError)
							# update values:
							v1 = vMinus(p1_rounded, vertex)
							d1 = vectorLength(v1)
							d2 = vectorLength(v2)
							# set node 2 to match d1:
							f2 = d1 / d2
							p2_new = vPlus(vertex, vMult(v2, f2))
						else:
							p2 = vPlus(p2, p1_roundingError)
							v21 = vMinus(p1_rounded, p2)
							v2_shift = aligned(v21, v1)
							p2_new = vPlus(p2, v2_shift)
						setNodePosition(n2, p2_new) # Glyphs will do the rounding
					else:
						setNodePosition(n2, p2_rounded)
						if vertex:
							v1 = vPlus(v1, p2_roundingError)
							v2 = vMinus(p2_rounded, vertex)
							d1 = vectorLength(v1)
							d2 = vectorLength(v2)
							f1 = d2 / d1
							p1_new = vPlus(vertex, vMult(v1, f1))
						else:
							p1 = vPlus(p1, p2_roundingError)
							v12 = vMinus(p2_rounded, p1)
							v1_shift = aligned(v12, v1)
							p1_new = vPlus(p1, v1_shift)
						setNodePosition(n1, p1_new) # Glyphs will do the rounding
				else:
					setNodePosition(n1, p1_new)
					setNodePosition(n2, p2_new)

#MenuTitle: Symmetrify Terminal
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__='''
	Select a stroke end (i.e. the two nodes). This script makes the terminal perpendicular (symmetrical).
'''

import math
from Cocoa import NSPoint, NSMakePoint

class FMXpoint:
	def __init__(self, x, y=None):
		if isinstance(x, GSNode):
			x, y = x.position
		elif isinstance(x, NSPoint):
			x, y = x
		self.x = x
		self.y = y

	def assignToNode(self, glyphsNode):
		pos = glyphsNode.position
		pos.x = self.x
		pos.y = self.y
		glyphsNode.position = pos
		# note: Glyphs will do the rounding as applicable

	def __repr__(self):
		return f"FMXpoint(x={self.x}, y={self.y})"

	def __add__(self, other):
		return FMXpoint(self.x + other.x, self.y + other.y)

	def __iadd__(self, other):
		self.x += other.x
		self.y += other.y
		return self

	def __sub__(self, other):
		return FMXpoint(self.x - other.x, self.y - other.y)

	def __isub__(self, other):
		self.x -= other.x
		self.y -= other.y
		return self

	def __mul__(self, scalar):
		return FMXpoint(self.x * scalar, self.y * scalar)

	def __imul__(self, scalar):
		self.x *= scalar
		self.y *= scalar

	def lengthSquared(self):
		return self.x ** 2 + self.y ** 2

	def normal(self):
		return FMXpoint(self.y, self.x)

	def length(self):
		return math.sqrt(self.lengthSquared())

	def atLength(self, newLength):
		if isinstance(newLength, FMXpoint):
			return self * math.sqrt(newLength.lengthSquared() / self.lengthSquared())
		else:
			return self * (newLength / self.length())

	def isShorterThan(self, other):
		if isinstance(newLength, FMXpoint):
			return self.lengthSquared() < other.lengthSquared()
		else:
			return self.lengthSquared() < other ** 2

	def rounded(self):
		return FMXpoint(round(self.x), round(self.y))

	# returns the rounding error
	def roundInPlace(self):
		unrounded = self
		self.x = round(self.x)
		self.y = round(self.y)
		return self - unrounded

	# returns the dor product
	def dot(self, other):
		return self.x * other.x + self.y * other.y

	# projects the vector onto another
	# • the returned vector is parallel to other
	# • self and the returned vector form a rectangular triangle
	def alignedTo(self, other):
		if other.x == 0:
			return (0, y)
		elif other.y == 0:
			return (x, 0)
		else:
			return other * (self.dot(other) / other.lengthSquared())

	@classmethod
	#  this seems more sensible as a class method
	#  so as to reflect the conceptual symmetry
	def dist(cls, p1, p2):
		return (p1 - p2).length()

def intersection(p1, p2, p3, p4):
	A1 = p2.y - p1.y
	B1 = p1.x - p2.x
	C1 = A1 * p1.x + B1 * p1.y
	A2 = p4.y - p3.y
	B2 = p3.x - p4.x
	C2 = A2 * p3.x + B2 * p3.y
	det = A1 * B2 - A2 * B1
	if det == 0:
		# lines are parallel
		return None
	x = (B2 * C1 - B1 * C2) / det
	y = (A1 * C2 - A2 * C1) / det
	return FMXpoint(x, y)

# if the vertex is further away that this
# the sides of the stroke will be considered parallel:
# (this is mostly because of float imprecision)
MAX_VERTEX_DIST = 3000

for selectedLayer in Font.selectedLayers:
	glyph = selectedLayer.parent
	for path in selectedLayer.paths:
		for node in path.nodes:
			if node.selected and node.nextNode.selected:
				n0 = node.prevNode
				n1 = node
				n2 = n1.nextNode
				n3 = n2.nextNode
				if n1.position == n2.position:
					# pointed terminal, perpendicularity not applicable
					continue
				if n0.position == n1.position:
					# retracted BCP
					n0 = n0.prevNode
				if n2.position == n3.position:
					# retracted BCP
					n3 = n3.nextNode
				p0 = FMXpoint(n0)
				p1 = FMXpoint(n1)
				p2 = FMXpoint(n2)
				p3 = FMXpoint(n3)
				vertex = intersection(p0, p1, p2, p3)
				if vertex and FMXpoint.dist(p1, vertex) > MAX_VERTEX_DIST:
					vertex = None
				if vertex:
					v1 = p1 - vertex
					v2 = p2 - vertex
					lenNew = (v1.length() + v2.length()) / 2
					p1new = vertex + v1.atLength(lenNew)
					p2new = vertex + v2.atLength(lenNew)
					if Font.grid != 0:
						p1roundingError = p1new.roundInPlace()
						p2roundingError = p2new.roundInPlace()
						if p1roundingError.isShorterThan(p2roundingError):
							# seems better to keep p1new and update p2new.
							# let’s tweak p2 so as to adopt the rounding error:
							# (we prefer to shift the stroke rather than changing its weight)
							p2 += p1roundingError
							# updating the vertex may be overly perfectionist
							# but let’s do all we can to end up with perpendicularity:
							vertex = intersection(p0, p1new, p2, p3)
							v1 = p1new - vertex
							v2 = p2 - vertex
							# we prioritise perpendicularity over stroke length
							# so let’s adopt the given v1 length:
							# (this means p1p2 does not generally rotate around its middle)
							p2new = vertex + v2.atLength(v1)
						else:
							# same process as above:
							p1 += p2roundingError
							vertex = intersection(p0, p1, p2new, p3)
							v1 = p1 - vertex
							v2 = p2new - vertex
							p1new = vertex + v1.atLength(v2)
				else:
					# parallel sides
					shift = (p2 - p1).alignedTo(p1 - p0) * 0.5
					p1new = p1 + shift
					if Font.grid != 0:
						# note: because of symmetry, the rounding error 
						#       would be the same for p1 and p2
						p1roundingError = p1new.roundInPlace()
						# similar to the above, adopt the rounding error:
						p2 += p1roundingError
						# update the shift for p2new:
						shift = (p2 - p1new).alignedTo(p1new - p0)
					p2new = p2 - shift
				p1new.assignToNode(n1)
				p2new.assignToNode(n2)

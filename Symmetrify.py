#MenuTitle: Symmetrify
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

from __future__ import division
import math

__doc__='''
Symmetrifies the glyph shape.

S - creates point reflection (rotational symmetry)
T - creates horizontal reflection symmetry
C - creates vertical reflection symmetry
H - creates 2-axis symmetry (ie. all the above)
* - creates 5-fold rotational symmetry

The buttons are available only as far as the node structure allows.
'''

from AppKit import NSPoint

doc = Glyphs.currentDocument
font = doc.font

try:
	from vanilla import Window, SquareButton
except:
	if Glyphs.versionNumber >= 3:
		Message("This script requires the Vanilla module. You can install it from the Modules tab of the Plugin Manager.", "Missing module")
	else:
		Message("This script requires the Vanilla module. To install it, go to Glyphs > Preferences > Addons > Modules and click the Install Modules button.", "Missing module")


class SymmetrifyDialog(object):

	def __init__(self):
		try:
			self.layer = doc.selectedLayers()[0]
		except TypeError:
			self.layer = None
			return
		self.init_contours()
		self.init_center()
		# determine the buttons (i.e. possible symmetry types):
		button_titles = []
		if self.can_rotate():
			button_titles.append('S')
		if self.can_rotate5():
			button_titles.append('*')
		if all(self.get_flip_partner(contour, is_horizontal=False) is not None for contour in self.contours):
			# ^ note: here, it does not matter whether we is_horizontal is Ture or False
			button_titles.extend(['T', 'C', 'H'])
		if not button_titles:
			self.layer = None
			return
		# dialog layout:
		margin = 10
		size = 40
		self.w = Window((len(button_titles) * (margin + size) + margin, 2 * margin + size), "Symmetrify")
		top = margin
		left = margin
		for title in button_titles:
			button = SquareButton((left, top, size, size), title, callback = self.buttonCallback)
			setattr(self.w, title, button)
			left += size + margin

	def init_contours(self):
		self.contours = [[node for node in path.nodes if node.selected] for path in self.layer.paths]
		self.contours = [contour for contour in self.contours if len(contour) >= 2]
		if not self.contours:
			self.contours = [[node for node in path.nodes] for path in self.layer.paths]

	def init_center(self):
		max_x = max([node.position.x for contour in self.contours for node in contour])
		min_x = min([node.position.x for contour in self.contours for node in contour])
		max_y = max([node.position.y for contour in self.contours for node in contour])
		min_y = min([node.position.y for contour in self.contours for node in contour])
		self.cx = 0.5 * (max_x + min_x)
		self.cy = 0.5 * (max_y + min_y)

	def run(self):
		self.w.open()

	# returns the best partner index for point 0
	def get_flip_partner(self, contour, is_horizontal):
		min_sum = float('inf')
		best_partner_index_for_0 = None
		for tested_partner_index_for_0 in range(len(contour)):
			current_sum = 0
			point_index = tested_partner_index_for_0
			for other_point_index in range(len(contour)):
				point = contour[point_index]
				other_point = contour[other_point_index]
				if (point.type == OFFCURVE) != (other_point.type == OFFCURVE):
					break
				if is_horizontal:
					current_sum += abs(other_point.x + point.x - 2 * self.cx)
					current_sum += abs(other_point.y - point.y) * 2
				else:
					current_sum += abs(other_point.y + point.y - 2 * self.cy)
					current_sum += abs(other_point.x - point.x) * 2
				if point_index == 0:
					point_index = len(contour) - 1
				else:
					point_index -= 1
			else:
				# all compared points have the same type
				if current_sum < min_sum:
					min_sum = current_sum
					best_partner_index_for_0 = tested_partner_index_for_0
		return best_partner_index_for_0

	def flip(self, flip_horizontal, flip_vertical):
		flips = [flip_horizontal] + [False] * flip_vertical
		for contour in self.contours:
			if self.get_flip_partner(contour, is_horizontal=False) % 2 == 0:
				self.cy = round(self.cy)
			if self.get_flip_partner(contour, is_horizontal=True) % 2 == 0:
				self.cx = round(self.cx)
		for contour in self.contours:
			xy = [(p.x, p.y) for p in contour]
			for current_is_horizontal in flips:
				partner_index = self.get_flip_partner(contour, current_is_horizontal)
				assert partner_index is not None
				for point_index in range(len(contour)):
					if point_index <= partner_index:
						# ^ this check is for performance only,
						#   to avoid treating point pairs twice
						x, y = xy[point_index]
						partner_x, partner_y = xy[partner_index]
						if current_is_horizontal:
							x = 0.50001 * x - 0.50001 * partner_x + self.cx
							y = 0.5 * y + 0.5 * partner_y + 0.00001 * (x - 0.5 * partner_x)
							xy[partner_index] = (2 * self.cx - x, y)
						else:
							x = 0.5 * x + 0.5 * partner_x + 0.00001 * (y - 0.5 * partner_y)
							y = 0.50001 * y - 0.50001 * partner_y + self.cy
							xy[partner_index] = (x, 2 * self.cy - y)
						xy[point_index] = (x, y)
					if partner_index == 0:
						partner_index = len(contour) - 1
					else:
						partner_index -= 1
			for point_index in range(len(contour)):
				point = contour[point_index]
				point.x, point.y = xy[point_index]

	def can_rotate(self):
		for contour in self.contours:
			if len(contour) % 2 != 0:
				return False
			other_point_index = len(contour)//2
			for point_index in range(other_point_index):
				point = contour[point_index]
				other_point = contour[other_point_index]
				if (point.type == OFFCURVE) != (other_point.type == OFFCURVE):
					return False
				other_point_index = (other_point_index + 1) % len(contour)
		return True

	def rotate(self):
		for contour in self.contours:
			other_point_index = len(contour)//2
			for point_index in range(other_point_index):
				point = contour[point_index]
				other_point = contour[other_point_index]
				point.x	 = 0.50001*point.x - 0.50001*other_point.x + self.cx
				other_point.x = 2.0*self.cx - point.x
				point.y	 = 0.50001*point.y - 0.50001*other_point.y + self.cy
				other_point.y = 2.0*self.cy - point.y
				other_point_index = (other_point_index + 1) % len(contour)

	def blend_points(p0, p1, p2, p3, p4):
		return NSPoint(0.2 * (p0.x + p1.x + p2.x + p3.x + p4.x), 0.2 * (p0.y + p1.y + p2.y + p3.y + p4.y))
	
	# returns the vector p-center, rotated around center by angle (given in radians)
	def rotated_vector(p, angle, center = NSPoint(0, 0)):
		v = NSPoint(p.x - center.x, p.y - center.y)
		result = NSPoint()
		result.x += v.x * math.cos(angle) - v.y * math.sin(angle)
		result.y += v.x * math.sin(angle) + v.y * math.cos(angle)
		return result

	def can_rotate5(self):
		for contour in self.contours:
			if len(contour) % 5 != 0:
				return False
			i1 = len(contour)//5
			i2 = 2 * i1
			i3 = 3 * i1
			i4 = 4 * i1
			for i0 in range(i1):
				if (contour[i0].type == OFFCURVE) != (contour[i1].type == OFFCURVE):
					return False
				if (contour[i0].type == OFFCURVE) != (contour[i2].type == OFFCURVE):
					return False
				if (contour[i0].type == OFFCURVE) != (contour[i3].type == OFFCURVE):
					return False
				if (contour[i0].type == OFFCURVE) != (contour[i4].type == OFFCURVE):
					return False
				i1 = (i1 + 1) % len(contour)
				i2 = (i2 + 1) % len(contour)
				i3 = (i3 + 1) % len(contour)
				i4 = (i4 + 1) % len(contour)

	def rotate5(self):
		fifth_circle = - math.pi * 2 / 5;
		sum_x = sum([p.x for c in self.contours for p in c])
		sum_y = sum([p.y for c in self.contours for p in c])
		num_p = sum([len(c) for c in self.contours])
		cgx = sum_x / num_p
		cgy = sum_y / num_p
		cg = NSPoint(cgx, cgy)
		for contour in self.contours:
			i1 = len(contour)//5
			i2 = 2 * i1
			i3 = 3 * i1
			i4 = 4 * i1
			for i0 in range(i1):
				vector = blend_points(subtractPoints(contour[i0].position, cg),
					rotated_vector(contour[i1].position, fifth_circle, cg),
					rotated_vector(contour[i2].position, fifth_circle * 2, cg),
					rotated_vector(contour[i3].position, fifth_circle * 3, cg),
					rotated_vector(contour[i4].position, fifth_circle * 4, cg))
				contour[i0].position = addPoints(cg, vector)
				contour[i1].position = addPoints(cg, rotated_vector(vector, -fifth_circle))
				contour[i2].position = addPoints(cg, rotated_vector(vector, -fifth_circle * 2))
				contour[i3].position = addPoints(cg, rotated_vector(vector, -fifth_circle * 3))
				contour[i4].position = addPoints(cg, rotated_vector(vector, -fifth_circle * 4))
				i1 = (i1 + 1) % len(contour)
				i2 = (i2 + 1) % len(contour)
				i3 = (i3 + 1) % len(contour)
				i4 = (i4 + 1) % len(contour)

	def buttonCallback(self, sender):
		button = sender.getTitle()
		font.disableUpdateInterface()
		glyph = self.layer.parent
		glyph.beginUndo()
		if button == 'S':
			self.rotate()
		if button == 'T':
			self.flip(flip_horizontal=True, flip_vertical=False)
		if button == 'C':
			self.flip(flip_horizontal=False, flip_vertical=True)
		if button == 'H':
			self.flip(flip_horizontal=True, flip_vertical=True)
		if button == '*':
			self.rotate5()
			self.flip(flip_horizontal=True, flip_vertical=False)
			self.rotate5()
			self.flip(flip_horizontal=True, flip_vertical=False)
			self.rotate5()
			self.flip(flip_horizontal=True, flip_vertical=False)
			self.rotate5()
			self.flip(flip_horizontal=True, flip_vertical=False)
		self.layer.syncMetrics()
		glyph.endUndo()
		font.enableUpdateInterface()
		self.w.close()

	
dialog = SymmetrifyDialog()
if dialog.layer is not None:
	dialog.run()

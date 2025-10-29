#MenuTitle: Symmetrify

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/freemix-glyphsapp

__doc__ = '''
Symmetrifies the glyph shape.

S - creates point reflection (rotational symmetry)
T - creates horizontal reflection symmetry
C - creates vertical reflection symmetry
H - creates 2-axis symmetry (ie. all the above)
* - creates 5-fold rotational symmetry

The buttons are available only as far as the node structure allows.
'''

import math
from AppKit import NSPoint

doc = Glyphs.currentDocument
font = doc.font

PERFECT_SYMMETRY = None
# • with PERFECT_SYMMETRY, the result is guaranteeed to be symmetrical
# • without PERFECT_SYMMETRY, the bounding box is guaranteed to be retained
# This affects 'T', 'C' and 'H' symmetrification when a node is in the centre
# and the bounding box has uneven dimensions.

INSTANT_SYMMETRIFICATION = None
# set INSTANT_SYMMETRIFICATION to 'S', 'T', 'C', 'H' or '*'
# to perform the symmetrification without showing the dialogue

SMALL_NEG = -1.0 / 4096
SMALL_POS = 1.0 / 4096

try:
	from vanilla import Window, SquareButton
except:
	if Glyphs.versionNumber >= 3:
		Message("This script requires the Vanilla module. You can install it from the Modules tab of the Plugin Manager.", "Missing module")
	else:
		Message("This script requires the Vanilla module. To install it, go to Glyphs > Preferences > Addons > Modules and click the Install Modules button.", "Missing module")

def swapped_if(t, do_swap):
	if do_swap:
		return (t[1], t[0])
	return t

def apply_grid(v):
	if font.grid > 0:
		return round(v / font.grid) * font.grid
	else:
		return v

def apply_half_grid(v):
	return 0.5 * apply_grid(v * 2)

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
		flips = [True] * flip_horizontal + [False] * flip_vertical
		for contour in self.contours:
			if PERFECT_SYMMETRY and self.get_flip_partner(contour, is_horizontal=False) % 2 == 0:
				# we have points on the line of symmetry
				self.cy = apply_grid(self.cy)
			else:
				# this is relevant if we have fractional input
				self.cy = apply_half_grid(self.cy)
			if PERFECT_SYMMETRY and self.get_flip_partner(contour, is_horizontal=True) % 2 == 0:
				self.cx = apply_grid(self.cx)
			else:
				self.cx = apply_half_grid(self.cx)
		for contour in self.contours:
			xy = [(p.x, p.y) for p in contour]
			for current_is_horizontal in flips:
				is_last_round = current_is_horizontal == flips[-1]
				almost_one = 1023 / 1024 if font.grid > 0 else 1
				if is_last_round:
					almost_one *= almost_one
				partner_index = self.get_flip_partner(contour, current_is_horizontal)
				assert partner_index is not None
				for point_index in range(len(contour)):
					if point_index <= partner_index:
						# ^ this check is for performance only,
						#   to avoid treating point pairs twice
						x, y = swapped_if(xy[point_index], current_is_horizontal)
						partner_x, partner_y = swapped_if(xy[partner_index], current_is_horizontal)
						c_x, c_y = swapped_if((self.cx, self.cy), current_is_horizontal)
						# at this point, we are assuming a horizontal axis (vertical flipping).
						# the x values will be (nearly) the same.
						correction_x = 0.5 * (partner_x - x)
						correction_y = (c_y - 0.5 * (partner_y + y))
						# ensure we don’t end up with .5 coordinates:
						correction_x *= almost_one if partner_x >= x else 1.0/almost_one
						correction_y *= almost_one if partner_y >= y else 1.0/almost_one
						x += correction_x
						y += correction_y
						xy[point_index] = swapped_if((x, y), current_is_horizontal)
						if point_index != partner_index:
							partner_y = 2 * c_y - y
							if is_last_round:
								# we can use the perfectly mirrored x here:
								xy[partner_index] = swapped_if((x, partner_y), current_is_horizontal)
							else:
								partner_x -= correction_x
								xy[partner_index] = swapped_if((partner_x, partner_y), current_is_horizontal)
					if partner_index == 0:
						partner_index = len(contour) - 1
					else:
						partner_index -= 1
			for point_index in range(len(contour)):
				point = contour[point_index]
				new_x, new_y = xy[point_index]
				point.x, point.y = apply_grid(new_x), apply_grid(new_y)

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
				rx = 0.5 * (point.x - other_point.x)
				ry = 0.5 * (point.y - other_point.y)
				rx += SMALL_POS if rx > 0 else SMALL_NEG
				ry += SMALL_POS if ry > 0 else SMALL_NEG
				point.x = apply_grid(self.cx + rx)
				point.y = apply_grid(self.cy + ry)
				other_point.x = apply_grid(self.cx - rx)
				other_point.y = apply_grid(self.cy - ry)
				other_point_index = (other_point_index + 1) % len(contour)

	def blend_points(self, p0, p1, p2, p3, p4):
		return NSPoint(0.2 * (p0.x + p1.x + p2.x + p3.x + p4.x), 0.2 * (p0.y + p1.y + p2.y + p3.y + p4.y))
	
	# returns the vector p-center, rotated around center by angle (given in radians)
	def rotated_vector(self, p, angle, center = NSPoint(0, 0)):
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
		return True

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
				vector = self.blend_points(subtractPoints(contour[i0].position, cg),
					self.rotated_vector(contour[i1].position, fifth_circle, cg),
					self.rotated_vector(contour[i2].position, fifth_circle * 2, cg),
					self.rotated_vector(contour[i3].position, fifth_circle * 3, cg),
					self.rotated_vector(contour[i4].position, fifth_circle * 4, cg))
				contour[i0].position = addPoints(cg, vector)
				contour[i1].position = addPoints(cg, self.rotated_vector(vector, -fifth_circle))
				contour[i2].position = addPoints(cg, self.rotated_vector(vector, -fifth_circle * 2))
				contour[i3].position = addPoints(cg, self.rotated_vector(vector, -fifth_circle * 3))
				contour[i4].position = addPoints(cg, self.rotated_vector(vector, -fifth_circle * 4))
				i1 = (i1 + 1) % len(contour)
				i2 = (i2 + 1) % len(contour)
				i3 = (i3 + 1) % len(contour)
				i4 = (i4 + 1) % len(contour)

	def performSymmetrification(self, button):
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

	def buttonCallback(self, sender):
		self.performSymmetrification(sender.getTitle())
		self.w.close()
	
dialog = SymmetrifyDialog()
if dialog.layer is not None:
	if INSTANT_SYMMETRIFICATION:
		dialog.performSymmetrification(INSTANT_SYMMETRIFICATION)
	else:
		dialog.run()

#MenuTitle: Symmetrify
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

from __future__ import division

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
layers = doc.selectedLayers()
glyph = layers[0].parent

try:
	from vanilla import Window, SquareButton
except:
	if Glyphs.versionNumber >= 3:
		Message( "This script requires the Vanilla module. You can install it from the Modules tab of the Plugin Manager.", "Missing module" )
	else:
		Message( "This script requires the Vanilla module. To install it, go to Glyphs > Preferences > Addons > Modules and click the Install Modules button.", "Missing module" )

class SymmetrifyDialog( object ):

	def buttonCallback( self, sender ):
		button = sender.getTitle()
		
		font.disableUpdateInterface()
		glyph.beginUndo()
		if button == 'S':
			rotate()
		if button == 'T':
			horiflip()
		if button == 'C':
			vertiflip()
		if button == 'H':
			bothflip()
		if button == '*':
			rotate5()
			horiflip()
			rotate5()
			horiflip()
			rotate5()
			horiflip()
			rotate5()
			horiflip()
		glyph.endUndo()
		font.enableUpdateInterface()
		
		self.w.close()

	def __init__( self, titles ):
		self.button = ''
		margin = 10
		size = 40
		self.w = Window( ( len( titles ) * ( margin + size ) + margin, 2 * margin + size ), "Symmetrify" )
		top = margin
		left = margin

		for title in titles:
			button = SquareButton( ( left, top, size, size ), title, callback = self.buttonCallback )
			setattr( self.w, title, button )
			left += size + margin

	def run( self ):
		self.w.open()

node_types = { 	GSLINE: 'o', GSCURVE: 'o', GSOFFCURVE: '.' }

for layer in layers:

	# all the nodes, sorted by contour
	contours = [ [ node for node in path.nodes if node.selected ] for path in layer.paths ]
	contours = [ contour for contour in contours if contour ]
	if not contours:
		contours = [ [ node for node in path.nodes ] for path in layer.paths ]
	# node structures of the contours
	structures = [ [ node_types[node.type] for node in contour ] for contour in contours ]

	# center x and y
	max_x = max( [ node.position.x for contour in contours for node in contour ] )
	min_x = min( [ node.position.x for contour in contours for node in contour ] )
	max_y = max( [ node.position.y for contour in contours for node in contour ] )
	min_y = min( [ node.position.y for contour in contours for node in contour ] )
	cx = 0.5 * ( max_x + min_x )
	cy = 0.5 * ( max_y + min_y )

	# can it be rotated?
	allow_rotate = 0
	for c in range( len( contours ) ):
		if len( contours[c] ) % 2 == 1:
			break
		else:
			rotated_structure = structures[c][len(structures[c])//2:] + structures[c][:len(structures[c])//2]
			if structures[c] != rotated_structure:
				break
	else:
		allow_rotate = 1

	# can it be 5-fold?
	allow_rotate5 = 0
	for c in range( len( contours ) ):
		if len( contours[c] ) % 5 == 1:
			break
		else:
			rotated_structure = structures[c][len(structures[c])//5:] + structures[c][:len(structures[c])//5]
			if structures[c] != rotated_structure:
				break
			rotated_structure2 = structures[c][2*len(structures[c])//5:] + structures[c][:2*len(structures[c])//5]
			if structures[c] != rotated_structure2:
				break
	else:
		allow_rotate5 = 1

	# can it be flipped?
	allow_flip = 0
	for c in range( len( contours ) ):
		allow_flip_temp = 0
		reversed_temp = structures[c][:]
		reversed_temp.reverse()
		for centre in range( len( contours[c] ) ):
			flipped_structure = reversed_temp[centre:] + reversed_temp[:centre]
			if structures[c] == flipped_structure:
				break
		else:
			break
	else:
		allow_flip = 1

	####################################################################################################

	def get_horipartner(c):
		for test in range(len(contours[c])):
			sum_temp = 0
			testpartner = test
			for n in range(len(contours[c])):
				sum_temp += abs(contours[c][n].x + contours[c][testpartner].x - 2*cx)
				sum_temp += abs(contours[c][n].y - contours[c][testpartner].y)*2
				if testpartner == 0:
					testpartner = len(contours[c])-1
				else:
					testpartner -= 1
			if test==0 or sum_temp < c_sum:
				c_sum = sum_temp
				result = test
		return result
	
	####################################################################################################

	def get_vertipartner(c):
		for test in range(len(contours[c])):
			sum_temp = 0
			testpartner = test
			for n in range(len(contours[c])):
				sum_temp += abs(contours[c][n].y + contours[c][testpartner].y - 2*cy)
				sum_temp += abs(contours[c][n].x - contours[c][testpartner].x)*2
				if testpartner == 0:
					testpartner = len(contours[c])-1
				else:
					testpartner -= 1
			if test==0 or sum_temp < c_sum:
				c_sum = sum_temp
				partner = test
				result = test
		return result
	
	####################################################################################################

	def horiflip():
		global cx, cy
		for c in range(len(contours)):
			if get_horipartner(c) % 2 == 0:
				cx = round(cx)
		for c in range(len(contours)):
			partner = get_horipartner(c)
			for n in range(len(contours[c])):
				contours[c][n].x	 = 0.50001*contours[c][n].x - 0.50001*contours[c][partner].x + cx
				contours[c][partner].x = 2*cx - contours[c][n].x
				contours[c][n].y	 = 0.5*contours[c][n].y + 0.5*contours[c][partner].y + 0.00001*(contours[c][n].x - 0.5*contours[c][partner].x)
				contours[c][partner].y = contours[c][n].y
				if partner == 0:
					partner = len(contours[c])-1
				else:
					partner -= 1
		layer.syncMetrics()
	
	####################################################################################################
	
	def vertiflip():
		global cx, cy
		for c in range(len(contours)):
			if get_vertipartner(c) % 2 == 0:
				cy = round(cy)
		for c in range(len(contours)):
			partner = get_vertipartner(c)
			for n in range(len(contours[c])):
				contours[c][n].x	 = 0.5*contours[c][n].x + 0.5*contours[c][partner].x + 0.00001*(contours[c][n].y - 0.5*contours[c][partner].y)
				contours[c][partner].x = contours[c][n].x
				contours[c][n].y	 = 0.50001*contours[c][n].y - 0.50001*contours[c][partner].y + cy
				contours[c][partner].y = 2*cy - contours[c][n].y
				if partner == 0:
					partner = len(contours[c])-1
				else:
					partner -= 1
		layer.syncMetrics()
	
	####################################################################################################

	def bothflip():
		global cx, cy
		for c in range(len(contours)):
			if get_vertipartner(c) % 2 == 0:
				cy = round(cy)
			if get_horipartner(c) % 2 == 0:
				cx = round(cx)
		for c in range(len(contours)):
			partner_hflip  = get_horipartner(c)
			partner_rotate = len(contours[c])//2
			partner_vflip  = partner_hflip + partner_rotate
			if partner_vflip >= len(contours[c]):
				partner_vflip -= len(contours[c])
			for point in contours[c]:
				point.x = 0.5001*(0.50001*point.x - 0.50001*contours[c][partner_hflip ].x)   +   0.4999*(0.50001*contours[c][partner_vflip].x - 0.50001*contours[c][partner_rotate].x)  + cx + 0.000001*(point.y - 0.5*contours[c][partner_vflip].y)
				contours[c][partner_hflip].x  = 2*cx - point.x
				contours[c][partner_rotate].x = contours[c][partner_hflip].x
				contours[c][partner_vflip].x  = point.x

				point.y = 0.5001*(0.50001*point.y - 0.50001*contours[c][partner_vflip ].y)   +   0.4999*(0.50001*contours[c][partner_hflip].y - 0.50001*contours[c][partner_rotate].y)  + cy + 0.000001*(point.x - 0.5*contours[c][partner_hflip].x)
				contours[c][partner_vflip].y  = 2*cy - point.y
				contours[c][partner_rotate].y = contours[c][partner_vflip].y
				contours[c][partner_hflip].y  = point.y

				if partner_hflip == 0:
					partner_hflip = len(contours[c])-1
				else:
					partner_hflip -= 1

				if partner_vflip == 0:
					partner_vflip = len(contours[c])-1
				else:
					partner_vflip -= 1

				if partner_rotate == len(contours[c])-1:
					partner_rotate = 0
				else:
					partner_rotate += 1
		layer.syncMetrics()
	
	####################################################################################################

	def rotate():
		global cx, cy
		for contour in contours:
			partner = len(contours[c])//2
			for n in range(partner):
				contour[n].x	 = 0.50001*contour[n].x - 0.50001*contour[partner].x + cx
				contour[partner].x = 2.0*cx - contour[n].x
				contour[n].y	 = 0.50001*contour[n].y - 0.50001*contour[partner].y + cy
				contour[partner].y = 2.0*cy - contour[n].y
				partner = ( partner + 1 ) % len(contour)
		layer.syncMetrics()
	
	####################################################################################################

	def blend_points( p0, p1, p2, p3, p4 ):
		return NSPoint( 0.2 * ( p0.x + p1.x + p2.x + p3.x + p4.x ), 0.2 * ( p0.y + p1.y + p2.y + p3.y + p4.y ) )
	
	import math
	# returns the vector p-center, rotated around center by angle (given in radians)
	def rotated_vector( p, angle, center = NSPoint( 0, 0 ) ):
		v = NSPoint( p.x - center.x, p.y - center.y )
		result = NSPoint()
		result.x += v.x * math.cos( angle ) - v.y * math.sin( angle )
		result.y += v.x * math.sin( angle ) + v.y * math.cos( angle )
		return result

	def rotate5():
		fifth_circle = - math.pi * 2 / 5;
		sum_x = sum( [ p.x for c in contours for p in c ] )
		sum_y = sum( [ p.y for c in contours for p in c ] )
		num_p = sum( [ len( c ) for c in contours ] )
		cgx = sum_x / num_p
		cgy = sum_y / num_p
		cg = NSPoint( cgx, cgy )
		for contour in contours:
			partner1 = len(contour)//5
			partner2 = 2 * partner1
			partner3 = 3 * partner1
			partner4 = 4 * partner1
			for n in range(partner1):
				vector = blend_points( subtractPoints( contour[n].position, cg ),
					rotated_vector( contour[partner1].position, fifth_circle, cg ),
					rotated_vector( contour[partner2].position, fifth_circle * 2, cg ),
					rotated_vector( contour[partner3].position, fifth_circle * 3, cg ),
					rotated_vector( contour[partner4].position, fifth_circle * 4, cg ) )
				contour[n].position = addPoints( cg, vector )
				contour[partner1].position = addPoints( cg, rotated_vector( vector, -fifth_circle ) )
				contour[partner2].position = addPoints( cg, rotated_vector( vector, -fifth_circle * 2 ) )
				contour[partner3].position = addPoints( cg, rotated_vector( vector, -fifth_circle * 3 ) )
				contour[partner4].position = addPoints( cg, rotated_vector( vector, -fifth_circle * 4 ) )
				partner1 = ( partner1 + 1 ) % len(contour)
				partner2 = ( partner2 + 1 ) % len(contour)
				partner3 = ( partner3 + 1 ) % len(contour)
				partner4 = ( partner4 + 1 ) % len(contour)
	
	####################################################################################################

	buttons = []
	
	if allow_rotate:
		buttons += [ 'S' ]
	if allow_flip:
		buttons += [ 'T', 'C' ]
		if 'S' in buttons:
			buttons += [ 'H' ]
	if allow_rotate5:
		buttons += [ '*' ]
	if buttons:
		dialog = SymmetrifyDialog( buttons )
		button = dialog.run()

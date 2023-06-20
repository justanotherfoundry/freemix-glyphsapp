#FLM: Optimiser

# v 1.0
# (c) Tim Ahrens, 2004

from FL import *
from math import *

#   This FL macro optimises the glyph outlines in two ways:
#
#   1. Continuous Curve
#     The macro compares the radius of curvature to both sides of a tangent node.
#     The node will be shifted until the radius of curvature is continuous.
#     This optimisation will be applied to single master as well as MM fonts.
#
#   2. MM Consistency
#
#     In MM fonts the macro will equalise
#     (a) the ratio of the length of the two handles within every curve (relaitve to the intersection)
#     (b) the ratio of the length of the two handles at every tangent point - unless the direction is the same in all masters
#     (c) the ratio of the length of the handle and the line wherever a curve and a straight line meet smoothely - unless the direction is the same in all masters
#
#     (a) will provide only minor improvement of interpolated instances
#     but can significantly improve the quality of extrapolations.
#
#     (b) and (c) are more important and will be performed after c.
#     this is very important in order to avoid kinks in interpolations and
#     extrapolations (according to the intercept theorems).
#     In the case of conflicts an iterative algorithm will try to find a solution.
#
#     This optimisation is meant to be 'invisible' regarding the masters and reveal the improvements
#     only in the interpolations. Don't be disappointed if the glyphs still 'look the same'.
#
#   If you select nodes only the selection will be optimised.
#   Note that the macro might have to adjust the adjacent nodes, too.

#   In other words, the macro will remove dents and bumps and allow you to inter- and extrapolate like crazy.
#   It may not greatly improve outlines that were drawn by experienced designers
#   but it can show beginners 'how to do it' and reveal problems even if you decide not to take the changes.


#   If the result is 'too smooth' you may want to switch off the continuous curve improvement
#   of tangents that are not horizontal or vertical.

diagonal_tangents_improvement = 1  # 1 = on, 0 = off

#   Alternatively, you can try adding more nodes.
#   Although the number of nodes should be kept as small as possible as a general rule,
#   this will be the best solution if you do not intend to work on the outlines a lot any more.
#   This macro will also make handling many nodes a lot easier.

#   You can even switch off continuous curve improvement completely:

tangents_improvement = 1  # 1 = on, 0 = off


#   If you want to lock any of the masters it will not be changed at all.
#   ! Note that the first layer is layer 0.

locklayer = -1 # -1 = no layer


#   You can switch off equalisation according to 2(a):

intra_curve = 1  # 1 = on, 0 = off


#   If the macro runs too slow you can decrease this value:

area_precision = 6 # Should not be larger than 15


################################################################################################
################################################################################################

nom = fl.font[2].layers_number
op0 = [] # list of original points 0 (actally a redundancy)
op1 = [] # list of original points 1 (BCP)
op2 = [] # list of original points 2 (BCP)
op3 = [] # list of original points 3 (the node itself)
np0 = [] # list of new points
np1 = []
np2 = []
np3 = []
oa = [] # list of original areas
internals = [] # list of nodes that are processed by internal()
tangents = [] # list of nodes that are processed by tangents()
cas = [] # list of nodes that are processed by curve_after_straight()
sac = [] # list of nodes that are processed by straight_after_curve()
tsc = [] # = tangents + cas + cas
shift_nodes = []
shift_total = []
shiftvector = []
todo_nodes  = []


def init(f, g, gindex):
  del op0[:]
  del op1[:]
  del op2[:]
  del op3[:]
  del np0[:]
  del np1[:]
  del np2[:]
  del np3[:]
  del oa[:]
  del internals[:]
  del tangents[:]
  del cas[:]
  del sac[:]
  del tsc[:]
  del shift_nodes[:]
  del shift_total[:]
  del shiftvector[:]
  del todo_nodes[:]
  fl.EditGlyph(gindex)
  fl.CallCommand(32907) # MaskClear
  fl.CallCommand(32904) # MaskCopy

  for n in range(len(g)):
    op0.append([])
    op1.append([])
    op2.append([])
    op3.append([])
    oa.append([])
    for m in range(nom):
      op3[n].append(Point(g[n].Layer(m)[0]))
      if n != 0:
        op0[n].append(Point(g[n-1].Layer(m)[0]))
      if g[n].count==3:
        op1[n].append(Point(g[n].Layer(m)[1]))
        op2[n].append(Point(g[n].Layer(m)[2]))
        oa[n].append(area(op0[n][m],op1[n][m],op2[n][m],op3[n][m]))
    np0.append([])
    np1.append([])
    np2.append([])
    np3.append([])
    for m in range(nom):
      np3[n].append(Point(g[n].Layer(m)[0]))
      if n != 0:
        np0[n].append(Point(g[n-1].Layer(m)[0]))

      if g[n].count==3:
        np1[n].append(Point(g[n].Layer(m)[1]))
        np2[n].append(Point(g[n].Layer(m)[2]))

  for n in range(len(g)):
    if g[n].count==3 and n!=0:
      for m in range(nom):
        if not is_hv(np0[n][m] - np3[n][m]):
          break
      else: continue
      intra_coeffs = []
      for m in range(nom):
        intra_coeffs.append( intra_coeff(np0[n][m],np1[n][m],np2[n][m],np3[n][m]) )
      for m in range(nom):
        if intra_coeffs[m] < 0 :
          break
      else: internals.append(n)
    ja = 0
    sum = Point(0,0)
    for m in range(nom): sum += np3[prevnode(prevnode(n,g),g)][m] - np3[prevnode(n,g)][m]
    for m in range(nom):
      if g[n].count == 3 and angle(np3[prevnode(prevnode(n,g),g)][m] - np3[prevnode(n,g)][m], sum) > 0.004 and prevnode(n,g) == prevnode(prevnode(n,g),g)+1 and g[prevnode(n,g)].type != nCURVE and g[prevnode(n,g)].alignment != nSHARP and g[prevnode(n,g)].alignment != 8192:
        ja = 1
#        g[prevnode(n,g)].selected = 1
    if ja: cas.append(n)

    ja = 0
    sum = Point(0,0)
    for m in range(nom): sum += np3[n][m] - np3[nextnode(n,g)][m]
    for m in range(nom):
      if g[n].count == 3 and angle(np3[n][m] - np3[nextnode(n,g)][m], sum) > 0.004 and g[nextnode(n,g)].type != nCURVE and g[n].alignment != nSHARP and g[n].alignment != 8192:
        ja = 1
#        g[n].selected = 1
    if ja: sac.append(n)

    ja = 0
    sum = Point(0,0)
    if g[n].count == 3 and g[nextnode(n,g)].count == 3:
      for m in range(nom): sum += np2[n][m] - np1[nextnode(n,g)][m]
    for m in range(nom):
      if g[n].count == 3 and g[nextnode(n,g)].count == 3 and angle(np2[n][m] - np1[nextnode(n,g)][m], sum) > 0.004 and g[n].alignment != nSHARP and g[n].alignment != 8192:
        ja = 1
#        g[n].selected = 1
    if ja: tangents.append(n)

  for n in range(len(g)):
    shift_total.append([])
    shiftvector.append([])
    for m in range(nom):
      if (not n in internals) or (not nextnode(n,g) in internals) or g[nextnode(n,g)].type != nCURVE or g[n].alignment == nSHARP or g[n].alignment == 8192:
        break
    else:
      shift_nodes.append(n)
      for m in range(nom):
        shift_total[n].append(0)
        if abso(op3[n][m] - op2[n][m])  <  abso(op3[n][m] - op1[nextnode(n,g)][m]):
          shiftvector[n].append(    (op1[nextnode(n,g)][m] - op2[n][m]) * (0.01*abso(op3[n][m] - op2[n][m])               / abso(op1[nextnode(n,g)][m] - op2[n][m]))  )
        else:
          shiftvector[n].append(    (op1[nextnode(n,g)][m] - op2[n][m]) * (0.01*abso(op3[n][m] - op1[nextnode(n,g)][m]) / abso(op1[nextnode(n,g)][m] - op2[n][m]))  )
  if g.isAnySelected():
    for n in range(len(g)):
      if not g[n].selected:
        if n in shift_nodes:  shift_nodes.remove(n)
        if n in internals:    internals.remove(n)
        if n in tangents:     tangents.remove(n)
        if n in sac:          sac.remove(n)
        if n in cas:          cas.remove(n)
        if n in tsc:          tsc.remove(n)
# # # # init) # # # # #


def abso(p): # length of a vector
  return abs(complex(p.x, p.y))


def roundedvector(p):
  p.x = int(round(p.x))
  p.y = int(round(p.y))
  return p


def intra_coeff(p0, p1, p2, p3): # coefficient that reflects the ratio of the length of BCPs within a curve segment
  sp = intersection(p0, p1, p2, p3)
  if sp.x != -1111:
    if abso(p3-p2)==0 or abso(p0-sp)==0:
      w = -1
    else:
      w = ( (abso(p0-p1)) / abso(p3-p2) )  *  ( abso(p3-sp) / abso(p0-sp) )**(1.0 - cos_angle(p0-p1, p2-p3) )
    if abso(sp-p1) > abso(sp-p0) or abso(sp-p2) > abso(sp-p3):
      w = -1
  else:
    w = -2
  return(w)


def angle(p1, p2):
  temp = (p1.x*p2.x + p1.y*p2.y) / (abso(p1)*abso(p2))
  if temp >= 1: return 0
  else: return acos(temp)


def cos_angle(p1, p2):
  return abs(  (p1.x*p2.x + p1.y*p2.y) / (abso(p1)*abso(p2))  )


def dist(p1,p2,p): # distance between p and the line defined by p1, p2
    return abs( (p1.x *(p2.y - p.y) + p2.x *(p.y - p1.y) + p.x *(p1.y - p2.y)) / abso(p1-p2) )


def area(p0, p1, p2, p3): # area of a B-spline
  app1   = area_precision+1
  app1_3 = app1**3
  p0x = int(p0.x)
  p1x = int(p1.x)
  p2x = int(p2.x)
  p3x = int(p3.x)
  p0y = int(p0.y)
  p1y = int(p1.y)
  p2y = int(p2.y)
  p3y = int(p3.y)
  midx = []
  midy = []
  midx.append( app1_3 * p0x )
  midy.append( app1_3 * p0y )
  for i in range(1,area_precision+1):
    tempx = p0x*(app1-i)**3  +  p1x*3*(app1-i)**2 *i  +  p2x*3*(app1-i)* (i)**2  + p3x*(i)**3
    tempy = p0y*(app1-i)**3  +  p1y*3*(app1-i)**2 *i  +  p2y*3*(app1-i)* (i)**2  + p3y*(i)**3
    midx.append( tempx )
    midy.append( tempy )
  midx.append( app1_3 * p3x)
  midy.append( app1_3 * p3y)
  a = 0
  for i in range(1,area_precision+2):
    a += ( p3x*app1**3*(midy[i] - midy[i-1]) + midx[i]*(midy[i-1] - p3y*app1**3) + midx[i-1]*(p3y*app1**3 - midy[i]) )
  return 1.0 * a / app1_3**2


def area_quad(p0, p1, p2, p3): # area of a quad
  a = 0
  mid = [p0, p1, p2, p3]
  for i in range(1,3):
    a+= p3.x*(mid[i].y - mid[i-1].y) + mid[i].x*(mid[i-1].y - p3.y) + mid[i-1].x*(p3.y - mid[i].y)
  return -a


def area_triangle(p0, p1, p2): # area of a triangle
  return p0.x*(p1.y - p2.y) + p1.x*(p2.y - p0.y) + p2.x*(p0.y - p1.y)


def intersection(p0, p1, p2, p3): # intersection between lines (p0, p1) and (p2, p3)
  s = Point()
  if p0.x == p1.x and p2.x != p3.x :
    s.x = p0.x
    s.y = ((p2.y - p3.y) / (p2.x - p3.x))*s.x + (p2.y - ((p2.y - p3.y) / (p2.x - p3.x))*p2.x)
  elif p2.x == p3.x and p0.x != p1.x :
    s.x = p2.x
    s.y = ((p0.y - p1.y) / (p0.x - p1.x))*s.x + (p1.y - ((p0.y - p1.y) / (p0.x - p1.x))*p1.x)
  elif p2.x != p3.x and p0.x != p1.x :
    if ((p0.y - p1.y) / (p0.x - p1.x)) == ((p2.y - p3.y) / (p2.x - p3.x)):
      s.x = -1111
      s.y = -1111
    else:
      s.x = ((p2.y - ((p2.y - p3.y) / (p2.x - p3.x))*p2.x)-(p1.y - ((p0.y - p1.y) / (p0.x - p1.x))*p1.x)) / (((p0.y - p1.y) / (p0.x - p1.x))-((p2.y - p3.y) / (p2.x - p3.x)))
      s.y = ((p0.y - p1.y) / (p0.x - p1.x))*s.x + (p1.y - ((p0.y - p1.y) / (p0.x - p1.x))*p1.x)
  else:
    s.x = -1111
    s.y = -1111
  return(s)


def nextnode(n,g):
  for c in range(g.GetContoursNumber()):
    if n == g.GetContourBegin(c) + g.GetContourLength(c) - 1 :
      if g[n].point == g[g.GetContourBegin(c)].point:
        return g.GetContourBegin(c) + 1
      else:
        return g.GetContourBegin(c)
      break
  else:
    return n+1


def prevnode(n,g):
  for c in range(g.GetContoursNumber()):
    if n == g.GetContourBegin(c):
      if g[n].point == g[g.GetContourBegin(c) + g.GetContourLength(c) - 1].point:
        return g.GetContourBegin(c) + g.GetContourLength(c) - 2
      else:
        return g.GetContourBegin(c) + g.GetContourLength(c) - 1
      break
  else:
    return n-1


def is_hv(p): # check if p is horizontal or vertical
  if abs(p.x) < 0.02 * abs(p.y) or abs(p.y) < 0.02 * abs(p.x): return 1
  else:
    return 0




def fit_first(g,n): # adjusts the first BCP so that the spline fits the original as close as possible
  for m in range(nom):
    if m == locklayer: continue
    normvector1 = (op1[n][m] - np0[n][m]) * ( 1.0 / abso(op1[n][m] - np0[n][m]) )
    if g[prevnode(n,g)].alignment != nSHARP and g[prevnode(n,g)].alignment != 8192 and g[prevnode(n,g)].type == nCURVE:
      normvector1 = (np3[prevnode(n,g)][m] - op2[prevnode(n,g)][m]) * ( 1.0 / abso(np3[prevnode(n,g)][m] - op2[prevnode(n,g)][m]) )
    if g[prevnode(n,g)].alignment != nSHARP and g[prevnode(n,g)].alignment != 8192 and g[prevnode(n,g)].type == nLINE:
      normvector1 = (np3[prevnode(n,g)][m] - np3[prevnode(prevnode(n,g),g)][m]) * ( 1.0 / abso(np3[prevnode(n,g)][m] - np3[prevnode(prevnode(n,g),g)][m]) )
    ti = abso(np0[n][m] - np1[n][m])
    tp1 = np0[n][m] + normvector1*ti
    ta = area(np0[n][m],tp1,np2[n][m],np3[n][m]) + area_quad(op3[n][m], np3[n][m], np0[n][m], op0[n][m])
    na = area(np0[n][m],np1[n][m],np2[n][m],np3[n][m]) + area_quad(op3[n][m], np3[n][m], np0[n][m], op0[n][m])
    dti = 3.0
    while 1:
      if abs(ta) < abs(oa[n][m]) : ti += dti
      else: ti -= dti
      tp1 = np0[n][m] + normvector1*ti
      if ti > 5:
        tp1 = roundedvector(tp1)
      ta = area(np0[n][m], tp1, np2[n][m], np3[n][m]) + area_quad(op3[n][m], np3[n][m], np0[n][m], op0[n][m])
      if abs(ta - oa[n][m]) < abs(na - oa[n][m]):
        np1[n][m].Assign(tp1)
        na = ta
      elif dti > 0.2: dti = dti * 0.67
      else: break
    if ti < 0:
      print "Warning: BCP after node", prevnode(n,g), "in master", m, "in", g.name,"could not be set properly."
      np1[n][m].Assign(np0[n][m] + normvector1 * 5)
      np1[n][m].Assign(roundedvector(np1[n][m]))


def fit_second(g,n): # adjusts the second BCP so that the spline fits the original as close as possible
  for m in range(nom):
    if m == locklayer: continue
    normvector2 = (op2[n][m] - np3[n][m]) * ( 1.0 / abso(op2[n][m] - np3[n][m]) )
    if g[n].alignment != nSHARP and g[n].alignment != 8192 and g[nextnode(n,g)].type == nCURVE:
      normvector2 = (op2[n][m] - op1[nextnode(n,g)][m]) * ( 1.0 / abso(op2[n][m] - op1[nextnode(n,g)][m]) )
    if g[n].alignment != nSHARP and g[n].alignment != 8192 and g[nextnode(n,g)].type == nLINE:
      normvector2 = (np3[n][m] - np3[nextnode(n,g)][m]) * ( 1.0 / abso(np3[n][m] - np3[nextnode(n,g)][m]) )
    ti = abso(np2[n][m] - np3[n][m])
    tp2 = np3[n][m] + normvector2*ti
    ta = area(np0[n][m],np1[n][m],tp2,np3[n][m]) + area_quad(op3[n][m], np3[n][m], np0[n][m], op0[n][m])
    na = area(np0[n][m],np1[n][m],np2[n][m],np3[n][m]) + area_quad(op3[n][m], np3[n][m], np0[n][m], op0[n][m])
    dti = 3.0
    while 1:
      if abs(ta) < abs(oa[n][m]) : ti += dti
      else: ti -= dti
      tp2 = np3[n][m] + normvector2*ti
      if ti > 5:
        tp2 = roundedvector(tp2)
      ta = area(np0[n][m], np1[n][m], tp2, np3[n][m]) + area_quad(op3[n][m], np3[n][m], np0[n][m], op0[n][m])
      if abs(ta - oa[n][m]) < abs(na - oa[n][m]):
        np2[n][m].Assign(tp2)
        na = ta
      elif dti > 0.2: dti = dti * 0.67
      else: break
    if ti < 0:
      print "Warning: BCP before node", n, "in master", m, "in", g.name,"could not be set properly."
      np2[n][m].Assign(np3[n][m] + normvector2 * 5)
      np2[n][m].Assign(roundedvector(np2[n][m]))

def fit_both(g,n,m,intra_coeffn): # adjusts both BCPs so that the spline fits the original as close as possible, coeff given
  sp = intersection( np0[n][m],op1[n][m],op2[n][m],np3[n][m] )
  normvector1 = (op1[n][m] - op0[n][m]) * ( 1.0 / abso(op1[n][m] - op0[n][m]) )
  normvector2 = (op2[n][m] - op3[n][m]) * ( 1.0 / abso(op2[n][m] - op3[n][m]) )
  if g[prevnode(n,g)].alignment != nSHARP and g[prevnode(n,g)].alignment != 8192 and g[prevnode(n,g)].type == nCURVE:
    normvector1 = (op3[prevnode(n,g)][m] - op2[prevnode(n,g)][m]) * ( 1.0 / abso(op3[prevnode(n,g)][m] - op2[prevnode(n,g)][m]) )
  if g[prevnode(n,g)].alignment != nSHARP and g[prevnode(n,g)].alignment != 8192 and g[prevnode(n,g)].type == nLINE:
    normvector1 = (op3[prevnode(n,g)][m] - op3[prevnode(prevnode(n,g),g)][m]) * ( 1.0 / abso(op3[prevnode(n,g)][m] - op3[prevnode(prevnode(n,g),g)][m]) )
  if g[n].alignment != nSHARP and g[n].alignment != 8192 and g[nextnode(n,g)].type == nCURVE:
    normvector2 = (op2[n][m] - op1[nextnode(n,g)][m]) * ( 1.0 / abso(op2[n][m] - op1[nextnode(n,g)][m]) )
  if g[n].alignment != nSHARP and g[n].alignment != 8192 and g[nextnode(n,g)].type == nLINE:
    normvector2 = (op3[n][m] - op3[nextnode(n,g)][m]) * ( 1.0 / abso(op3[n][m] - op3[nextnode(n,g)][m]) )
  f = intra_coeffn * ( abso(sp - np0[n][m]) / abso(sp - np3[n][m]) )**(1.0 - cos_angle(op0[n][m]-op1[n][m], op2[n][m]-op3[n][m]) )
  if f < 1:
    normvector1 = normvector1 * f
    ti = abso(np2[n][m] - np3[n][m])
  else:
    normvector2 = normvector2 * ( 1.0 / f )
    ti = abso(np0[n][m] - np1[n][m])
  tp1 = np0[n][m] + normvector1*ti
  tp2 = np3[n][m] + normvector2*ti
  np1[n][m].Assign(tp1)
  np2[n][m].Assign(tp2)
  ta = area(np0[n][m],tp1,tp2,np3[n][m]) + area_quad(op3[n][m], np3[n][m], np0[n][m], op0[n][m])
  na = ta
  dti = 3.0
  while 1:
    if abs(ta) < abs(oa[n][m]) : ti += dti
    else: ti -= dti
    tp1 = np0[n][m] + normvector1*ti
    tp2 = np3[n][m] + normvector2*ti
    if ti > 5:
      tp1 = roundedvector(tp1)
      tp2 = roundedvector(tp2)
    ta = area(np0[n][m], tp1, tp2, np3[n][m]) + area_quad(op3[n][m], np3[n][m], np0[n][m], op0[n][m])
    if abs(ta - oa[n][m]) < abs(na - oa[n][m]):
      np1[n][m].Assign(tp1)
      np2[n][m].Assign(tp2)
      na = ta
    elif dti > 0.2: dti *= 0.5
    else: break

def internal(g,n): # equalises the coeffs of all masters
  intra_coeffs = []
  intra_coeffnew = 1
  for m in range(nom):
    intra_coeffs.append( intra_coeff(np0[n][m],np1[n][m],np2[n][m],np3[n][m]) )
    if intra_coeffs[m] < 0:
      intra_coeffnew = 0
  if intra_coeffnew == 0: return
  for m in range(nom):
    intra_coeffnew = intra_coeffnew * sqrt(intra_coeffs[m])
  intra_coeffnew = intra_coeffnew**(2.0/nom)
  if locklayer != -1: intra_coeffnew = intra_coeffs[locklayer]
  for m in range(nom):
    if m == locklayer: continue
    fit_both(g,n,m,intra_coeffnew)


def straight_after_curve(g,n):  # equalises the ratio of length of BCP and line segment in all masters
  ratios = []
  for m in range(nom): ratios.append( abso( np2[n][m] - np3[n][m] ) / abso( np3[n][m] - np3[nextnode(n,g)][m] ) )
  rationew = 1
  for m in range(nom): rationew = rationew * sqrt(ratios[m])
  rationew = rationew**(2.0/nom)
  if locklayer != -1: rationew = ratios[locklayer]
  for m in range(nom):
    if m == locklayer: continue
    np2[n][m].Assign(np3[n][m] + ( np3[n][m] - np3[nextnode(n,g)][m] ) * rationew)
    np2[n][m].Assign(roundedvector(np2[n][m]))
    tp042 = (np3[n][m] - np3[nextnode(n,g)][m]) * (0.42 / abso(np3[n][m] - np3[nextnode(n,g)][m]) )
    for i in range(-2,3):
      tp = tp042*i + np3[n][m] + ( np3[n][m] - np3[nextnode(n,g)][m] ) * rationew
      tp = roundedvector(tp)
      if dist(np3[n][m], np3[nextnode(n,g)][m], tp) < dist(np3[n][m], np3[nextnode(n,g)][m], np2[n][m]):
        np2[n][m].Assign(tp)
  fit_first(g,n)
  if n in todo_nodes: todo_nodes.remove(n)
  if prevnode(n,g) in tsc  and  not prevnode(n,g) in todo_nodes: todo_nodes.append(prevnode(n,g))


def curve_after_straight(g,n):  # equalises the ratio of length of BCP and line segment in all masters
  ratios = []
  for m in range(nom): ratios.append( abso( np1[n][m] - np0[n][m] ) / abso( np3[prevnode(prevnode(n,g),g)][m] - np3[prevnode(n,g)][m] ) )
  rationew = 1
  for m in range(nom): rationew = rationew * sqrt(ratios[m])
  rationew = rationew**(2.0/nom)
  if locklayer != -1: rationew = ratios[locklayer]
  for m in range(nom):
    if m == locklayer: continue
    np1[n][m].Assign( np0[n][m] + ( np3[prevnode(n,g)][m] - np3[prevnode(prevnode(n,g),g)][m] ) * rationew )
    np1[n][m].Assign( roundedvector(np1[n][m]) )
    tp042 = (np3[prevnode(n,g)][m] - np3[prevnode(prevnode(n,g),g)][m]) * (0.42 / abso(np3[prevnode(n,g)][m] - np3[prevnode(prevnode(n,g),g)][m]) )
    for i in range(-2,3):
      tp = tp042*i + np0[n][m] + ( np3[prevnode(n,g)][m] - np3[prevnode(prevnode(n,g),g)][m] ) * rationew
      tp = roundedvector(tp)
      if dist(np3[prevnode(n,g)][m], np3[prevnode(prevnode(n,g),g)][m], tp) < dist(np3[prevnode(n,g)][m], np3[prevnode(prevnode(n,g),g)][m], np1[n][m]):
        np1[n][m].Assign(tp)
  fit_second(g,n)
  if n in todo_nodes: todo_nodes.remove(n)
  if    n in tangents    or    n in sac    and    not n in todo_nodes: todo_nodes.append(n)


def tangent(g,n):  # equalises the ratio of length of BCPs on one node in all masters
  ratios = []
  for m in range(nom): ratios.append( abso( np2[n][m] - np3[n][m] ) / abso(np3[n][m] - np1[nextnode(n,g)][m]) )
  rationew = 1
  for m in range(nom): rationew = rationew * sqrt(ratios[m])
  rationew = rationew**(2.0/nom)
  if locklayer != -1: rationew = ratios[locklayer]
  for m in range(nom):
    if m == locklayer: continue
    handleweg = (op1[nextnode(n,g)][m] - op2[n][m]) * ( abso(np3[n][m] - np1[nextnode(n,g)][m]) * sqrt(ratios[m]/rationew) / abso(op1[nextnode(n,g)][m] - op2[n][m]) )
    handlehin = handleweg* (0 - rationew)
    np2[n][m].Assign(np3[n][m] + handlehin)
    np1[nextnode(n,g)][m].Assign(np3[n][m] + handleweg)
    np2[n][m].Assign( roundedvector(np2[n][m]) )
    np1[nextnode(n,g)][m].Assign(roundedvector(np1[nextnode(n,g)][m]))
    tp032 = (op2[n][m] - op1[nextnode(n,g)][m]) * (0.32 / abso(op2[n][m] - op1[nextnode(n,g)][m]) )
    for i in range(-4,4):
      for j in range(-4,4):
        if i+j < 5:
          tphin = tp032*i + np3[n][m] + handlehin
          tpweg = tp032*i + np3[n][m] + handleweg
          tphin = roundedvector(tphin)
          tpweg = roundedvector(tpweg)
          if dist(tphin, tpweg, np3[n][m]) < dist(np2[n][m],np1[nextnode(n,g)][m],np3[n][m]):
            np2[n][m].Assign(tphin)
            np1[nextnode(n,g)][m].Assign(tpweg)
  fit_first(g,n)
  fit_second(g,nextnode(n,g))
  if n in todo_nodes: todo_nodes.remove(n)
  if nextnode(n,g) in tsc  and  not nextnode(n,g) in todo_nodes: todo_nodes.append(nextnode(n,g))
  if prevnode(n,g) in tsc  and  not prevnode(n,g) in todo_nodes: todo_nodes.append(prevnode(n,g))


def fine_tuning(g,n):
# maybe BCP should not be constrained to the original angle
  for m in range(nom):
    if m == locklayer: continue
    if is_hv(op1[n][m] - np0[n][m]):
      normvector1 = (op1[n][m] - np0[n][m]) * ( 1.0 / abso(op1[n][m] - np0[n][m]) )
      normvector1 = roundedvector(normvector1 )
      na = area(np0[n][m],np1[n][m],np2[n][m],np3[n][m]) + area_quad(op3[n][m], np3[n][m], np0[n][m], op0[n][m])
      tp1 = np1[n][m]
      ta = na
      while 1:
        if abs(ta) < abs(oa[n][m]) : tp1 += normvector1
        else: tp1 -= normvector1
        ta = area(np0[n][m], tp1,np2[n][m], np3[n][m]) + area_quad(op3[n][m], np3[n][m], np0[n][m], op0[n][m])
        if abs(ta - oa[n][m]) < abs(na - oa[n][m]):
          np1[n][m].Assign(tp1)
          na = ta
        else: break
    if is_hv(op2[n][m] - np3[n][m]):
      normvector1 = (op2[n][m] - np3[n][m]) * ( 1.0 / abso(op2[n][m] - np3[n][m]) )
      normvector1 = roundedvector(normvector1 )
      na = area(np0[n][m],np1[n][m],np2[n][m],np3[n][m]) + area_quad(op3[n][m], np3[n][m], np0[n][m], op0[n][m])
      tp2 = np2[n][m]
      ta = na
      while 1:
        if abs(ta) < abs(oa[n][m]) : tp2 += normvector1
        else: tp2 -= normvector1
        ta = area(np0[n][m],np1[n][m], tp2, np3[n][m]) + area_quad(op3[n][m], np3[n][m], np0[n][m], op0[n][m])
        if abs(ta - oa[n][m]) < abs(na - oa[n][m]):
          np2[n][m].Assign(tp2)
          na = ta
        else: break


def shifter(g): # shifts the nodes ubtil the radiuses to both sides are equalised
  en = 80
  for m in range(nom):
    if m == locklayer: continue
    breakoff = []
    diff = []
    intra_coeffn1 = []
    intra_coeffn2 = []

    for n in range(len(g)):
      if n in shift_nodes: breakoff.append(0)
      else: breakoff.append(1)
      diff.append(16)
      intra_coeffn1.append(0)
      intra_coeffn2.append(0)
    for n in shift_nodes:
      if not diagonal_tangents_improvement and not is_hv(np2[n][m] - np1[nextnode(n,g)][m]):
        breakoff[n] = 1
        continue
      if not is_hv(np2[n][m] - np1[nextnode(n,g)][m]):
        diff[n] = diff[n]/4
      intra_coeffn1[n] = intra_coeff(np0[n][m],np1[n][m],np2[n][m],np3[n][m])
      intra_coeffn2[n] = intra_coeff(np0[nextnode(n,g)][m],np1[nextnode(n,g)][m],np2[nextnode(n,g)][m],np3[nextnode(n,g)][m])

    it = 0
    while 0 in breakoff:
      if it < 30: it += 1
      else: break
      for n in shift_nodes:
        if breakoff[n] == 1: continue
        en1x = (int(np0[n][m].x)  +                int(np1[n][m].x              )*3*(en-1)  +  int(np2[n][m].x              )*3*((en-1)**2)  +  int(np3[n][m].x              )*((en-1)**3 - en**3) )
        en1y = (int(np0[n][m].y)  +                int(np1[n][m].y              )*3*(en-1)  +  int(np2[n][m].y              )*3*((en-1)**2)  +  int(np3[n][m].y              )*((en-1)**3 - en**3) )
        en2x = (int(np3[nextnode(n,g)][m].x)  +  int(np2[nextnode(n,g)][m].x)*3*(en-1)  +  int(np1[nextnode(n,g)][m].x)*3*((en-1)**2)  +  int(np0[nextnode(n,g)][m].x)*((en-1)**3 - en**3) )
        en2y = (int(np3[nextnode(n,g)][m].y)  +  int(np2[nextnode(n,g)][m].y)*3*(en-1)  +  int(np1[nextnode(n,g)][m].y)*3*((en-1)**2)  +  int(np0[nextnode(n,g)][m].y)*((en-1)**3 - en**3) )
        radius1 = abs( 1.0* (en1x**2 + en1y**2) /  ( ( en1y*(np2[n][m].x              -np3[n][m].x              ) - en1x*(np2[n][m].y-              np3[n][m].y              ) ) ) )      * abso( np2[n][m]-              np3[n][m]               )
        radius2 = abs( 1.0* (en2x**2 + en2y**2) /  ( ( en2y*(np1[nextnode(n,g)][m].x-np0[nextnode(n,g)][m].x) - en2x*(np1[nextnode(n,g)][m].y-np0[nextnode(n,g)][m].y) ) ) )      * abso( np1[nextnode(n,g)][m]-np0[nextnode(n,g)][m] )

        bak_3 = Point(np3[n][m])
        bak_nach1 = Point(np1[nextnode(n,g)][m])
        bak_nach2 = Point(np2[nextnode(n,g)][m])
        bak_1 = Point(np1[n][m])
        bak_2 = Point(np2[n][m])
        bak_radius1 = radius1
        bak_radius2 = radius2
        shift_total_bak = shift_total[n][m]

        if radius1 < radius2:
          shift_total[n][m] += diff[n]
        else:
          shift_total[n][m] -= diff[n]
        np3[n][m].Assign( roundedvector(op3[n][m] + shiftvector[n][m]*shift_total[n][m]) )
        np3[prevnode(nextnode(n,g),g)][m].Assign(np3[n][m])
        np3[nextnode(prevnode(n,g),g)][m].Assign(np3[n][m])
        np0[nextnode(n,g)][m].Assign(np3[n][m])

        fit_both(g,n,m, intra_coeffn1[n])
        fit_both(g,nextnode(n,g),m, intra_coeffn2[n])

        en1x = (int(np0[n][m].x)  +                int(np1[n][m].x              )*3*(en-1)  +  int(np2[n][m].x              )*3*((en-1)**2)  +  int(np3[n][m].x              )*((en-1)**3 - en**3) )
        en1y = (int(np0[n][m].y)  +                int(np1[n][m].y              )*3*(en-1)  +  int(np2[n][m].y              )*3*((en-1)**2)  +  int(np3[n][m].y              )*((en-1)**3 - en**3) )
        en2x = (int(np3[nextnode(n,g)][m].x)  +  int(np2[nextnode(n,g)][m].x)*3*(en-1)  +  int(np1[nextnode(n,g)][m].x)*3*((en-1)**2)  +  int(np0[nextnode(n,g)][m].x)*((en-1)**3 - en**3) )
        en2y = (int(np3[nextnode(n,g)][m].y)  +  int(np2[nextnode(n,g)][m].y)*3*(en-1)  +  int(np1[nextnode(n,g)][m].y)*3*((en-1)**2)  +  int(np0[nextnode(n,g)][m].y)*((en-1)**3 - en**3) )
        radius1 = abs( 1.0* (en1x**2 + en1y**2) /  ( ( en1y*(np2[n][m].x              -np3[n][m].x              ) - en1x*(np2[n][m].y-              np3[n][m].y              ) ) ) )      * abso( np2[n][m]-              np3[n][m]               )
        radius2 = abs( 1.0* (en2x**2 + en2y**2) /  ( ( en2y*(np1[nextnode(n,g)][m].x-np0[nextnode(n,g)][m].x) - en2x*(np1[nextnode(n,g)][m].y-np0[nextnode(n,g)][m].y) ) ) )      * abso( np1[nextnode(n,g)][m]-np0[nextnode(n,g)][m] )

        if abs(bak_radius1-bak_radius2) < abs(radius1-radius2)  or  abso(np2[n][m] - np3[n][m]) < 3  or  abso(np0[nextnode(n,g)][m] - np1[nextnode(n,g)][m]) < 3:
          np3[n][m].Assign(bak_3)
          np3[prevnode(nextnode(n,g),g)][m].Assign(bak_3)
          np3[nextnode(prevnode(n,g),g)][m].Assign(bak_3)
          np0[nextnode(n,g)][m].Assign(bak_3)
          np1[n][m].Assign(bak_1)
          np2[n][m].Assign(bak_2)
          np1[nextnode(n,g)][m].Assign(bak_nach1)
          np2[nextnode(n,g)][m].Assign(bak_nach2)
          shift_total[n][m] = shift_total_bak
          if abso(shiftvector[n][m]*diff[n]) > 1  and   diff[n] > 1:
            diff[n] = diff[n]/2
          else:
            breakoff[n] = 1
            continue

glist = []
def addtoglist(f, g, gindex):
  glist.append(gindex)

def optim(f, g, gindex):
  init(f, g, gindex)

  for n in tangents:
    if not n in todo_nodes: todo_nodes.append(n)
    if not n in tsc: tsc.append(n)
  for n in cas:
    if not n in todo_nodes: todo_nodes.append(n)
    if not n in tsc: tsc.append(n)
  for n in sac:
    if not n in todo_nodes: todo_nodes.append(n)
    if not n in tsc: tsc.append(n)
  for n in internals:
    if intra_curve > 0: internal(g, n)

  if tangents_improvement == 1: shifter(g)

  for i in range(15): # if there are no conflicting tangents this loop will only be run once
    todo_nodes_copy  = todo_nodes[:]
    for n in todo_nodes_copy:
      if n in cas:  curve_after_straight(g,n)
      if n in sac:  straight_after_curve(g,n)
      if n in tangents:  tangent(g,n)
  for n in internals: fine_tuning(g,n)

  # # # # # apply # # # # #
  for n in range(len(g)):
    for m in range(nom):
      if g[n].count==3 and n!=0:
        g[n].Layer(m)[1].Assign(np1[n][m])
        g[n].Layer(m)[2].Assign(np2[n][m])
      g[n].Layer(m)[0].Assign(np3[n][m])
  fl.Select(gindex,0)
  g.mark = 230
  fl.UpdateGlyph()
  fl.UpdateFont()


def shift_only(f, g, gindex):
  init(f, g, gindex)
  shifter(g)
  # # # # # apply # # # # #
  for n in range(len(g)):
    for m in range(nom):
      if g[n].count==3 and n!=0:
        g[n].Layer(m)[1].Assign(np1[n][m])
        g[n].Layer(m)[2].Assign(np2[n][m])
      g[n].Layer(m)[0].Assign(np3[n][m])
  fl.Select(gindex,0)
  g.mark = 230
  fl.UpdateGlyph()
  fl.UpdateFont()

fl.ForSelected(addtoglist)

if nom > 1:
  for i in glist: optim(fl.font, fl.font[i], i)
else:
  for i in glist: shift_only(fl.font, fl.font[i], i)

fl.UpdateFont()
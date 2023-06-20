This add-on for Glyphs displays the relative handle lengths for:
* Smooth nodes that connect two curve elements
* Nodes that connect a straight line and a curve (so-called tangent points)

Note:
* Red labels mean that the handle relation is wrong, and you should correct them as necessary.
* Black labels are close enough to the other masters.
* Light grey labels mean the position is perfect.

If any nodes are selected then only these will be shown.
Horizontal and vertical connections (extrema) are ignored, as they are safe from interpolation kinks.

To do:
* Calculate and display the intra-curve coefficients. For shallow curves, this may be non-trivial.
* Refine the definition of “close enough”.
* Look at the interpolated exports and ignore masters that are not used in interpolations
(to be precise, there may even be independent groups of masters that are only interpolated among themselves).
* Detect if all masters have the same (or similar enough) angle.
What if some masters have the same angle, and some have the same relative handle lengths?
Need to think about that carefully, and respect the interpolated exports.

* Auto-fix the problems (oh wait, that’s a case from [RMX](https://remix-tools.com) 2.0)

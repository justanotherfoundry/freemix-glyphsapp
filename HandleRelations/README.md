# Show Handle Relations

Interpolations can have unintentional kinks in smooth connections between curves,
or nodes that connect a straight line and a curve (so-called tangent points).

There is no risk of kinks if the angle is the same in all masters
(which is always given for horizontal or vertical extrema). However, the design often makes this impossible.
In that case, kinks can be avoided if the relative length of the handles is the same in all masters.

This add-on for Glyphs helps you achieve this by showing the relative handle lengths
for connections that may develop kinks after interpolation.

Furthermore, the label give you a quick overview of the nodes that need to be fixed:
* Red labels mean that the handle relation is wrong, and you should correct them as necessary.
* Black labels are close enough to the other masters.
* Light grey labels mean the position is perfect.

https://github.com/justanotherfoundry/freemix-glyphsapp/assets/1331354/38b19f29-538a-4533-9d61-2e14bd39421e

Note: If any nodes are selected then only these will be shown.

To do:
* Calculate and display the intra-curve coefficients. For shallow curves, this may be non-trivial.
* Refine the definition of “close enough”.
* How about intermediate special layers? 
* Look at the interpolated exports and ignore masters that are not used in interpolations
(to be precise, there may even be independent groups of masters that are only interpolated among themselves).
* Detect if all masters have the same (or similar enough) angle.
What if some masters have the same angle, and some have the same relative handle lengths?
Need to think about that carefully, and respect the interpolated exports.
* Auto-fix the problems (oh wait, that will be a nice feature for [RMX](https://remix-tools.com) 2.0 some day)

Fun fact: I already implemented automatically establishing coefficients consitency
in what was essentially the [very first version](https://forum.fontlab.com/archive-old-fontlab-forum/fl-macro-general-outline-optimiser/msg6314)
of the RMX Harmonizer in 2004. Haha, seems like no-one could be bothered back then, at least there are no replies. 
See [Optimiser.py](Optimiser.py) for details (in the comments).
“In other words, the macro will remove dents and bumps and allow you to inter- and extrapolate like crazy.” Now that’s quite something!

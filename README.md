glyphsapp-scripts
=================

Some Python scripts to be used with the [Glyphs](http://www.glyphsapp.com/) font editor.

Tim Ahrens  
[Font Remix Tools for Glyphs](http://remix-tools.com/glyphsapp) 
[Just Another Foundry](http://justanotherfoundry.com/) 

### Delete All Hints

Removes all hints from the selected glyphs.


### Expand Kerning

Expand Kerning like we know it from FontLab.


### Insert Glyph to Background

1. Enter a glyph name.
2. Press the left align or right align button.
3. This script will clear the mask, then insert the specified glyph into the mask.

- With right align selected, the contours will be pasted as if the advance widths were aligned.
- The keyboard shortcuts for left and right aligned are Enter and Esc.
- It is sufficient to enter the beginning of the glyph name, e.g. "deg" for "degree".


### Insert Glyph

Same as “Insert Glyph to Background” but the glyph is inserted into the active (foreground) layer, not in the background

### Mask to Master

Simulates the good ol' Mask to Master function we know from FontLab
(i.e. replaces the current outline with the background).

You can give it the familiar Cmd+J shortcut via App Shortcuts
in the Mac OS System Preferences.

UPDATE:

- If nodes are selected then Mask to Master detects the counterparts (closest nodes) in the background
and shifts the nodes accordingly. In this case, the node structure and node types are not affected.
- If nothing is selected, it behaves as before (but does not remove existing anchors – this is a fix).


### Paste Background

Pastes the background contours into the current layer.

Former FontLab users can give it the familiar Cmd+L shortcut via App Shortcuts
in the Mac OS System Preferences.


### Remove Backup Layers

Removes all backup layers (i.e. those created using the "Copy" button) from the font.


### Symmetrify

Symmetrifies the glyph shape.

S - creates point reflection (rotational symmetry)

T - creates horizontal reflection symmetry

C - creates vertical reflection symmetry

H - creates 2-axis symmetry (ie. all the above)

The buttons are available only as far as the node structure allows.

### Round Kerning

- Rounds the kerning values to full integer numbers.
- In addition, values smaller than MIN_VALUE are erased.

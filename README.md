Freemix for Glyphs
=================

Some Python scripts to be used with the [Glyphs](http://www.glyphsapp.com/) font editor.

Tim Ahrens  

[Font Remix Tools for Glyphs](http://remix-tools.com/glyphsapp) 

[Just Another Foundry](http://justanotherfoundry.com/) 

### Customize Defaults

This is not a macro you would use daily but more of a documentation of settings that can be accessed in Python via intDefaults.


### Delete All Hints

Removes all hints from the selected glyphs.


### Delete Zero-Thickness Hints

Removes all zero-thickness hints from all glyphs in the font.


### Edit Next Glyph/ Previous Glyph

Activates the next/ previous glyph in the tab for editing. Makes most sense if you give it a keyboard shortcut in the macOS system preferences.


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

The main improvement is that it is appplied only to the selection.
In combination with Insert Glyph to Background, you can easily
transfer parts of the outline between glyphs.


### Paste Background

Pastes the background contours into the current layer.

Former FontLab users can give it the familiar Cmd+L shortcut via App Shortcuts
in the Mac OS System Preferences.


### Print Coeffs

Prints the interpolation coefficients for each master in all instances.


### Remove Backup Layers

Removes all backup layers (i.e. those created using the "Copy" button) from the selected glyphs.


### Round Kerning

Rounds the kerning values to full integer numbers.

In addition, values smaller than MIN_VALUE are erased.


### Select Inaccessible Glyphs

Run this macro while in the Font View.

The macro selects all glyphs that
- export
- do not have a Unicode value and 
- are not covered by any OT feature

i.e. are not accessible in the final font.

These glyphs can usually be excluded from the final exported OTF font.


### Symmetrify

Symmetrifies the glyph shape.

S - creates point reflection (rotational symmetry)

T - creates horizontal reflection symmetry

C - creates vertical reflection symmetry

H - creates 2-axis symmetry (ie. all the above)

* - creates 5-fold rotational symmetry, useful for asterisks (note that this automatically also applies horizontal reflection symmetry)

The buttons are available only as far as the node structure allows.

### Round Kerning

- Rounds the kerning values to full integer numbers.
- In addition, values smaller than MIN_VALUE are erased.

### Toggle Backup Layer

- This script toggles between the master layer and the last backup layer in the list.

- Given a keyboard shortcut, this is useful for quickly comparing two versions of a glyph.

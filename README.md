Freemix for Glyphs
=================

Some Python scripts to be used with the [Glyphs](http://www.glyphsapp.com/) font editor, written by Tim Ahrens.

To install Freemix in Glyphs,

* download the whole freemix package using “Clone or download”, “Download ZIP”.
* in Glyphs, press Cmd+Shift+Y, which opens a Finder window
* move the `.py` files from the freemix package into the `Scripts` subfolder
* move the `.glyphsReporter` and `.glyphsPalette` files into the `Plugins` subfolder
* in Glyphs, open Preferences (Cmd+,) / Addons / Modules and press “Install Modules”
* restart Glyphs

See also: [Font Remix Tools for Glyphs](http://remix-tools.com/glyphsapp), [Kern On for Glyphs](http://kern-on.com), [Just Another Foundry](http://justanotherfoundry.com/)


### Adopt Background

The selected nodes will adopt the position of the corresponding nodes in the background.

This is one of the simplest but probably the most powerful of my scripts. In combination with Insert Glyph to Background, you can easily transfer parts of the outlines between glyphs.

Tip: Give it a keyboard shortcut if you use it a lot!


### Adopt from Other Font

Adopts glyph properties from the same-named glyph(s) in a different font.

<img src="https://raw.githubusercontent.com/justanotherfoundry/freemix-glyphsapp/master/img/AdoptFromOtherFont.png" width="320" />


### Alignment Palette

The palette shows the position of the center of the glphs’s bounding box. This works with components, with multiple glyphs selected and is also editable. Useful for centering all case-sensitive punctuation vertically, or to check whether mathematical operands are on the same x position (use Glyphs’ built-in glyph info to check whether they have the same advance width).
Note that the bounding box center may be .5 even if your font has a grid of 1 without subdivisions (i.e. integer coordinates). The node/path selection is intentionally ignored.

The Overshoots section displays the overshoot of the selected glyph(s) relative to each alignment zone.

<img src="https://raw.githubusercontent.com/justanotherfoundry/freemix-glyphsapp/master/AlignmentPalette/AlignmentPalette.png" width="320" />


### Anchors Palette

The palette shows the position of anchors in the selected glyphs. This helps you check for consistent positioning of anchors if multiple glyphs are selected. For example, select A–Z to see whether all `top` anchors are on the same height, and adjust their position. If the position of the anchors is not identical in all selected glyphs then a gray x or y is shown.

The palette shows the four most frequently used anchors. Setting the x or y position of a particular anchor via the palette only affects glyphs that have an anchor with the respective name (anchors are never inserted or removed).

<img src="https://raw.githubusercontent.com/justanotherfoundry/freemix-glyphsapp/master/AnchorsPalette/AnchorsPalette.png" width="240" />


### Caps and Corners Window

To show this, use Window -> Caps and Corners. This window shows the cap and corner components in the selected glyphs. This helps you check for consistency: just select multiple glyphs. Note that the fields are editable, so you can adjust the scaling of caps and corners for multiple glyphs at once.

<img src="https://raw.githubusercontent.com/justanotherfoundry/freemix-glyphsapp/master/CapsAndCorners/CapsAndCorners.png" width="320" />


### Components Palette

The palette shows the position of components in the selected glyphs. This helps you check for consistent positioning if multiple glyphs are selected.


### Delete All Anchors

Removes all anchors from the selected glyphs.


### Delete Zero-Thickness Hints

Removes all zero-thickness hints from all glyphs in the font.


### Delete BCP

This literally deletes individual BCPs: If you delete one of the two BCPs in a cubic curve then it becomes quadratic.

If the deleted BCP was retracted (i.e. on the node) then the other handle length is adjusted to better retain the shape.


### Edit Next Glyph/ Previous Glyph

Activates the next/ previous glyph in the tab for editing. Makes most sense if you give it a keyboard shortcut in the macOS system preferences.


### Expand Kerning

Expand Kerning like we know it from FontLab.


### Font Book Checker

Outputs information on the supported languages as per Font Book on macOS (make sure the Macro Panel is open).


### Glyphset Diff

Shows the glyphs that are not present in the other font (exactly two fonts need to be open).


### Insert Glyph to Background

This is one of the most powerful scripts in this collection. I highly recommend to give it a keyboard shortcut.

1. Enter a glyph name.
2. Press the left align or right align button.
3. This script will clear the mask, then insert the specified glyph into the mask.

- With right align selected, the contours will be pasted as if the advance widths were aligned. For example, inserting the X into the K right-aligned will instantly give you a visual feedback whether the spacing is consistent.
- The keyboard shortcuts for left and right aligned are Enter and Esc. If you really have to cancel the dialog, use the little button on the dialog’s title bar.
- It is sufficient to enter the beginning of the glyph name, e.g. "deg" for "degree". Be careful if there are several glyphs in the font starting with your entry. The script will simply enter one it finds.
– For non-master layers, the script will try to find matching (by name) non-master layers from the inserted glyph.
– For brace layers, if no corresponding brace layer is found in the inserted glyph, an interpolation is generated on-the-fly. A typical use case would be to set up a brace layer for the E, then insert the L so as to determine the standard (not visually corrected) interpolated stems.


### Insert Glyph

Same as “Insert Glyph to Background” but the glyph is inserted into the active (foreground) layer, not in the background


### Jump to Alternate

In the edit view, use this script to “jump” back and forth (or to circle) between alternate glyphs such as one, one.lf and one.tosf.
If several glyphs are selected you can choose to add or remove suffixes.

### Make Backup Layer

Same as the “Copy” button on the Layers palette but as a script. Because I really want a keyboard shortcut for this. Without a keyboard shortcut this script is completely useless. Sorry.


### Paste Background

Pastes the background contours into the current layer.

Former FontLab users can give it the familiar Cmd+L shortcut via App Shortcuts
in the Mac OS System Preferences.


### Print Coeffs

Prints the interpolation coefficients for each master in all instances (make sure the Macro Panel is open).


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


### Suffixes Palette

The palette shows the name(s) of the selected glyph(s), split by suffix. The fields are editable.

This is useful for quickly changing the suffix of multiple glyphs at once.

<img src="https://raw.githubusercontent.com/justanotherfoundry/freemix-glyphsapp/master/SuffixesPalette/SuffixesPalette.png" width="160" />


### Symmetrify

Symmetrifies the glyph shape.

S - creates point reflection (rotational symmetry)

T - creates horizontal reflection symmetry

C - creates vertical reflection symmetry

H - creates 2-axis symmetry (ie. all the above)

* - creates 5-fold rotational symmetry, useful for asterisks (note that this automatically also applies horizontal reflection symmetry)

The buttons are available only as far as the node structure allows.


### Toggle Backup Layer

- This script toggles between the master layer and the last backup layer in the list.

- Given a keyboard shortcut, this is useful for quickly comparing two versions of a glyph.

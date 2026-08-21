Drop gallery photos in this folder.

The filenames the site is currently waiting for are listed in the GALLERY
table near the bottom of build.py, and every missing one also shows on
gallery.html as a dashed slot naming the file it wants.

Add, remove or rename rows in that table freely — it is the single source
of truth for the gallery. Run `python3 build.py` after any change.

SPECS
  Format      JPG (photos) — not PNG, the files get large
  Size        1600-2400 px on the long edge
  Weight      Under 400 KB each; compress before uploading
  Orientation Landscape. Rows marked wide=True span two columns at 16:9,
              so crop those with room at the sides.

BEFORE YOU UPLOAD ANYTHING — check each photo for:

  1. PPE. Helmets, gloves, and safety harnesses where working at height.
     A utility client WILL notice a photo of your crew without them, and
     it undermines the ISO 45001 claim on every other page.

  2. Client-confidential detail. Single line diagrams on control room
     boards, relay setting screens, nameplate data, drawing title blocks,
     and gate signage identifying a secure installation. Much of this is
     restricted under the client's own site rules.

  3. Faces. Get consent from anyone identifiable, or frame wide enough
     that they are not.

  4. Live equipment. A photo showing work near energised apparatus
     without visible barricading reads as a safety violation whether or
     not it was one.

If in doubt about a photo, leave it out. One bad image costs more
credibility than ten good ones earn.

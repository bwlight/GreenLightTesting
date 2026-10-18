# Operator Interface V0.2.2 — fixed actions and scrollable entry

## Scope
- Converted the entry form to a Tkinter Canvas containing the existing form with a vertical ttk scrollbar.
- Moved the action buttons into a fixed bar outside the scrolling region. The action bar is packed first to reserve height even when the top pane is small.
- Scroll region updates when either conditional Other explanation expands/collapses; form width follows canvas resizing. Mouse wheel over the form scrolls it.
- Preserved all five date/time controls, existing popup behavior, engine, visit model, and explanation validation.
- Updated one pre-existing theme test that relied on a fixed widget-child index; it now locates the primary button through the explicitly named action bar.

## Verification
`xvfb-run -a python -m unittest discover -s tests -q` → 83 tests passed (78 existing + 5 new).
New tests check action-bar independence, both explanations and bottom scrolling, action visibility at 850x620/1000x700/1120x790 with Tk scaling 1.0/1.25/1.5, width resizing, and preserved Other text.

## Limits
Virtual Tk display/scaling checks do not replace founder testing at actual Windows DPI (100%, 125%, 150%) and taskbar/work-area configurations. The app remains fictional-only and session-memory-only; no production or stopwatch functionality.

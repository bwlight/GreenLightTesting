# Operator Interface V0.1.1 — Popup positioning correction

- Calendar popups are anchored to the calendar button that opened them, with a six-pixel vertical gap.
- Popups open below the button when space permits; otherwise they flip above it, and their position is clamped to the reported Tk virtual-screen rectangle.
- Shared `DatePicker` logic applies to Visit Date, Appointment, Arrival, Check-in, and Exit.
- Calendar selection, navigation, and date/time data semantics are unchanged. The calculation engine is unchanged.
- Automated regression coverage includes normal placement, flip, horizontal clamping, tight screens, negative screen origins, and a graphical test using five distinct date controls.
- Windows multi-monitor work-area behavior still requires founder evaluation on actual hardware; Tk virtual-root bounds are not guaranteed to describe every Windows taskbar or multi-monitor configuration.

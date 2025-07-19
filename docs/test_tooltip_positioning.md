# Tooltip Positioning Test

## Changes Made

The tooltip positioning has been updated to follow the mouse pointer instead of using the default "right" side positioning.

### Implementation Details

1. **Mouse Position Tracking**: Added `mousePosition` state to track cursor coordinates
2. **Hover State Management**: Added `hoveredKey` state to control tooltip visibility
3. **Custom Tooltip**: Replaced Radix UI tooltip with custom implementation
4. **Mouse-Relative Positioning**: Tooltip appears 15px to the right of mouse cursor

### Key Changes in cleanup-dialog.tsx

- Added `mousePosition` and `hoveredKey` state variables
- Added `handleMouseMove` function to track mouse position
- Replaced `<Tooltip>` component with custom div positioned using `mousePosition`
- Tooltip positioned at `left: mousePosition.x + 15, top: mousePosition.y - 10`

### Testing Instructions

1. Start backend: `cd backend && python app.py`
2. Start frontend: `cd frontend && npm run dev-with-backend`
3. Open application and navigate to "设置" → "数据清理"
4. Hover over any K value in the cleanup dialog
5. Verify tooltip appears to the right of mouse cursor and follows mouse movement

### Expected Behavior

- Tooltip should appear 15px to the right of the mouse cursor
- Tooltip should follow mouse movement while hovering over K values
- Tooltip should disappear when mouse leaves the K value area
- Tooltip content should show the first 3 V values as before
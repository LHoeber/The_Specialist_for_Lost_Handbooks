/**
 * Direct player input: translates keypresses into calls to
 * RoomState.performAction. Replaces the old mouse-click interface entirely
 * (see docs/design/grid-navigation.md) -- this file does nothing but
 * translate a keypress into a call to that shared, input-agnostic
 * function, so a future scripted agent can drive the exact same function
 * directly without touching the DOM at all.
 */
window.Game = window.Game || {};

Game.UI = (function () {
  const { Direction } = Game.Enums;

  // Arrow keys and WASD both work interchangeably at all times, not a mode
  // the player switches between; "do" is bound to space.
  const KEY_ACTIONS = {
    ArrowUp: Direction.UP,
    w: Direction.UP,
    W: Direction.UP,
    ArrowDown: Direction.DOWN,
    s: Direction.DOWN,
    S: Direction.DOWN,
    ArrowLeft: Direction.LEFT,
    a: Direction.LEFT,
    A: Direction.LEFT,
    ArrowRight: Direction.RIGHT,
    d: Direction.RIGHT,
    D: Direction.RIGHT,
    " ": "do",
  };

  class UIController {
    constructor(roomState) {
      this.roomState = roomState;
    }

    handleKeyDown(event) {
      const action = KEY_ACTIONS[event.key];
      if (action === undefined) return;
      event.preventDefault(); // space/arrows would otherwise scroll the page
      this.roomState.performAction(action);
    }
  }

  return { UIController, KEY_ACTIONS };
})();

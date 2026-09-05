/**
 * Direct player input: translates mouse clicks into interactable actions.
 * Port of Version_1/src/rendering/ui.py; event.pos there was already
 * window-relative, so the one adaptation here is converting the browser's
 * viewport-relative clientX/clientY into canvas-local coordinates via the
 * canvas's own bounding rect.
 */
window.Game = window.Game || {};

Game.UI = (function () {
  class UIController {
    constructor(renderer) {
      this.renderer = renderer;
    }

    handleClick(event, roomState) {
      const rect = this.renderer.canvas.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      const logicalPos = this.renderer.screenToLogical(x, y);
      const interactable = this.renderer.findInteractableAt(logicalPos, roomState);
      if (interactable !== null) {
        interactable.onClick(roomState);
      }
    }
  }

  return { UIController };
})();

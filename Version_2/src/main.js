/**
 * Entry point: wires the environment, renderer, and UI input together.
 * Port of Version_1/src/main.py -- but per ../CLAUDE.md, does NOT port the
 * `while running:` polling loop as a fixed-tick loop. Most of the room is
 * static and only changes on a player action, but some sprites (e.g. the
 * ventilator) animate on their own clock, so rendering still needs to
 * happen every frame -- via requestAnimationFrame, the web equivalent of
 * clock.tick(FPS) -- rather than only in response to input events. Input
 * itself is keyboard-driven grid movement + "do" (see
 * docs/design/grid-navigation.md), not mouse clicks -- the keydown handler
 * below does nothing but call performAction; the continuously-running rAF
 * loop is what actually reflects the resulting state change on screen.
 */
window.Game = window.Game || {};

(function () {
  async function main() {
    const canvas = document.getElementById("game-canvas");

    // Renderer first: mirrors Version_1/src/main.py's ordering (there,
    // because sprite loading needs a display surface; here there's no such
    // requirement, but the ordering is kept for a 1:1 correspondence).
    const renderer = new Game.Renderer.Renderer(canvas);
    const env = new Game.Environment.Environment();
    const ui = new Game.UI.UIController(env.state);

    await Game.Assets.whenAllLoaded();

    window.addEventListener("keydown", (event) => ui.handleKeyDown(event));

    window.addEventListener("resize", () => {
      renderer.handleResize();
    });

    function loop() {
      renderer.render(env.state);
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  }

  window.addEventListener("DOMContentLoaded", () => {
    main().catch((err) => {
      // eslint-disable-next-line no-console
      console.error("Failed to start the game:", err);
    });
  });
})();

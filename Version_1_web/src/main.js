/**
 * Entry point: wires the environment, renderer, and UI input together.
 * Port of Version_1/src/main.py -- but per ../CLAUDE.md, does NOT port the
 * `while running:` polling loop. Nothing in this game animates
 * continuously (it's a static room until a click changes state), so this
 * renders once on load (after every sprite finishes loading) and then only
 * re-renders after a click actually mutates state.
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
    const ui = new Game.UI.UIController(renderer);

    await Game.Assets.whenAllLoaded();

    renderer.render(env.state);

    canvas.addEventListener("click", (event) => {
      ui.handleClick(event, env.state);
      renderer.render(env.state);
    });

    window.addEventListener("resize", () => {
      renderer.handleResize();
      renderer.render(env.state);
    });
  }

  window.addEventListener("DOMContentLoaded", () => {
    main().catch((err) => {
      // eslint-disable-next-line no-console
      console.error("Failed to start the game:", err);
    });
  });
})();

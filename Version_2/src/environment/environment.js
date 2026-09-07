/**
 * Top-level orchestrator tying room state to the rest of the game. Direct
 * port of Version_1/src/environment/environment.py.
 */
window.Game = window.Game || {};

Game.Environment = (function () {
  class Environment {
    constructor() {
      this.state = new Game.State.RoomState();
    }

    reset() {
      this.state = new Game.State.RoomState();
      return this.state;
    }
  }

  return { Environment };
})();

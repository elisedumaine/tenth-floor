# Owners

Every piece of Tenth Floor has an owner: the person who looks after it and reviews every change to it.
This is how big projects stay sane with many hands (Chromium's OWNERS files, Mozilla's module owners).

## How ownership works

- **You own a piece by claiming it.** Open a **Claim a piece** issue. The maintainer writes your name here.
  A piece marked **open** is looked after by the maintainer until someone claims it.
- **The owner reviews every change to their piece**, and the maintainer merges. You can always change your
  own piece, by pull request like everyone else.
- **One piece per pull request.** The check says which piece a pull request touches and who must review
  it, and refuses one that touches two pieces. (Your one line in `CREDITS.md` can come along with anything.)
- **Owning a piece isn't owning the rules.** If a change alters how the game plays (what's in RULES.md),
  it needs a decision first (DECISIONS.md), even when the owner proposes it.
- **A new kit part is a new file** in `engine/kit/`: whoever adds it can claim it.
- **Hand it on.** If you want to give a piece up, say so in its claim issue; it goes back to **open**.
- **The maintainer keeps the contract**: the pieces every floor depends on, where a change can break
  someone else's work. Anyone can propose a change to them; the maintainer decides.

## Pieces

Owner **open** means unclaimed (the maintainer looks after it). The check reads this table, so keep its shape:
`| piece | owner | GitHub | files |`, with each file or pattern in backticks.

### The contract (kept by the maintainer)
| piece | owner | GitHub | files |
|---|---|---|---|
| The game loop | Isaac Holze (maintainer) | @rattlesnake-ike | `engine/game.py` `main.py` `engine/__init__.py` |
| The room contract: rooms, platforms, lifts, furniture | Isaac Holze (maintainer) | @rattlesnake-ike | `engine/room.py` |
| The numbers: screen, jump, speed, clock | Isaac Holze (maintainer) | @rattlesnake-ike | `engine/config.py` |
| The building: floors, elevator stops, the code | Isaac Holze (maintainer) | @rattlesnake-ike | `engine/building.py` |
| The check and CI | Isaac Holze (maintainer) | @rattlesnake-ike | `check.py` `.github/*` |
| The project's docs, rules and decisions | Isaac Holze (maintainer) | @rattlesnake-ike | `README.md` `CONTRIBUTING.md` `AGENTS.md` `CLAUDE.md` `RULES.md` `DECISIONS.md` `OWNERS.md` `.gitignore` `floors/__init__.py` |
| The example floors | Isaac Holze (maintainer) | @rattlesnake-ike | `floors/example_floor.py` `floors/example_kit_floor.py` |

### Game pieces (claim one)
| piece | owner | GitHub | files |
|---|---|---|---|
| Movement: running, jumping, the flip, searching, the character | open | | `engine/player.py` |
| Security: PatrolBot and Zapper | open | | `engine/bots.py` |
| Screens: title, elevator view, HUD, win and lose | open | | `engine/screens.py` |
| The lobby, floor 1: Security Desk and Flatiron Gallery | open | | `engine/lobby.py` |
| Sound: the game's sound effects, made in code | open | | `engine/sound.py` |
| The kit's frame and its docs: KIT.md, the catalog picture | open | | `KIT.md` `docs/*` `engine/kit_catalog.py` `engine/kit/__init__.py` `engine/kit/_base.py` |

### Kit parts (claim one, or add a new one)
| piece | owner | GitHub | files |
|---|---|---|---|
| Kit: Desk | open | | `engine/kit/desk.py` |
| Kit: Bookshelf | open | | `engine/kit/bookshelf.py` |
| Kit: Locker | open | | `engine/kit/locker.py` |
| Kit: FilingCabinet | open | | `engine/kit/filing_cabinet.py` |
| Kit: ServerRack | open | | `engine/kit/server_rack.py` |
| Kit: Printer3D | open | | `engine/kit/printer_3d.py` |
| Kit: Easel | open | | `engine/kit/easel.py` |
| Kit: Couch | open | | `engine/kit/couch.py` |
| Kit: Plant | open | | `engine/kit/plant.py` |
| Kit: VendingMachine | open | | `engine/kit/vending_machine.py` |
| Kit: Plinth | open | | `engine/kit/plinth.py` |
| Kit: Crusher | open | | `engine/kit/crusher.py` |
| Kit: Drone | open | | `engine/kit/drone.py` |
| Kit: FloorLaser | open | | `engine/kit/floor_laser.py` |
| Kit: MovingPlatform | open | | `engine/kit/moving_platform.py` |
| Kit: Window | open | | `engine/kit/window.py` |
| Kit: Poster | open | | `engine/kit/poster.py` |
| Kit: Sign | open | | `engine/kit/sign.py` |
| Kit: CeilingLight | open | | `engine/kit/ceiling_light.py` |

### Floors
Each floor, `floors/<name>.py` and `floors/<name>_assets/`, is owned by its `AUTHOR`. Nobody else edits it.

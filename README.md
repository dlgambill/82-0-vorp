# 82-0 VORP

Can you build a team that never loses?

**Play it here: https://dlgambill.github.io/82-0-vorp/**

No login, no install. It runs in your browser, phone or desktop.

## How it works

1. You get a random NBA team and decade, like the 1990s Bulls.
2. Pick one player from that team and put him in an open spot: PG, SG, SF, PF or C.
3. Do that five times. You get one team reroll and one decade reroll per game, so use them wisely.
4. Hit play and watch all 82 games.

## What decides who wins

This is a fan-made take on the 82-0 roster game, with one big change - wins come from VORP (Value Over Replacement Player), which is basketball's closest thing to baseball's WAR.

- Each player counts for his best VORP season with that team in that decade.
- Add up your five players and you get a team rating.
- Every game is then played out with some luck mixed in, so even a great team can drop one.

To have a real shot at 82-0 you need a combined VORP of about 38 or more. At 41 it is a coin flip.

## A few things to know

- VORP only exists from 1973-74 on. For older players like Wilt and Russell, the number is an estimate based on Win Shares. Those are marked with a ~ in the game.
- Some players can play a second position. Those show up as dashed tags.
- VORP leans on box score stats, so great defenders who did not score much (hello, Dennis Rodman) rate lower than you would expect.
- Turn on "Hide VORP" if you want to draft from memory.

## Where the numbers come from

Player stats are from Basketball-Reference, through the 2025-26 season. This is a hobby project and is not affiliated with the NBA, Basketball-Reference, or the original 82-0 game.

## For the curious

The whole game is one file, `index.html`. The `src` folder has the page template and the scripts that build the player data into it.

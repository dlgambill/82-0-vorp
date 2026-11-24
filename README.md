# Scorer's Table

Free sports stat games. You get a random team, you pick a player, and you try to beat the number.

**Play here: https://dlgambill.github.io/82-0-vorp/**

No login, no install. It runs in your browser, phone or desktop.

## The games

NBA
- **82-0 VORP** - Draft five players from random teams and decades. Can your lineup go 82-0?
- **Bucket List** - 12 random teams, 12 players. Pile up 310,000 career points.
- **Dime Store** - Same idea with career assists. Think point guards.

NFL
- **Touchdown Chase** - 20 random teams, 20 running backs. Reach 1,800 career touchdowns.
- **Home Grown** - Only the touchdowns a back scored for that team count.
- **Air Yards** - 10 quarterbacks, 470,000 career passing yards.

MLB
- **Home Run Chase** - 15 hitters, 7,600 career home runs.
- **K Count** - 15 pitchers, 47,000 career strikeouts.
- **Hit Parade** - Only the hits a player got for that team count.

In most of these you only see names. The numbers show up after you lock in your pick.

## How 82-0 VORP works

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

Stats come from Basketball-Reference (NBA), nflverse and Pro-Football-Reference (NFL), and the Lahman Baseball Database (MLB). This is a hobby project and is not affiliated with any league, any of those sources, or the original 82-0 game.

## For the curious

Each game is one page in its own folder. Most of them share one engine, and the `src` folder has that plus the scripts that build the player data.

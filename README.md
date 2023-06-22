# supremacy

![supremacy](https://github.com/nvaytet/supremacy/assets/39047984/6e800f7c-6eb4-47d4-9621-1465aeaae879)

## What is the tournament about?

We have created a video game that is designed to be played by a small python program, rather than a human.
Conference attendees can participate in a tournament where they (either alone or in a team) each submit a bot that will play the game, and at the end of the conference, we will have a tournament session where everyone can come and watch our strange creations play against each other (either brilliantly or it may all go wrong!).

## Disclaimer

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Ukraine.svg/320px-Flag_of_Ukraine.svg.png" width="50" />

The topic of the game is a sci-fi war on a foreign planet, set far in the future. We understand that the topic of war could upset some people with the unfortunate events that are currently going on in Ukraine. We do not want to promote war, and we fully support Ukraine in their hardship. Development of the game was started before the invasion of Ukraine, it is just a coincidence that this is the game that was ready for the conference.
We just want to make a fun event for EuroPython participants, we do not want to offend anyone.

## How to participate?

- Register your team filling in the form at ....
- You will be given a private GH repository
- Read the game rules below and start working on your bot

## TL;DR

Get started with:

```
conda create -n <NAME> -c conda-forge python=3.10
conda activate <NAME>
git clone git@github.com:europython2023gametournament/supremacy.git
cd supremacy/
python -m pip install -e .
cd tests/
python test.py
```

## The game: Supremacy

Preview

<table>
  <tr>
    <td>Time = 2min</td><td>Time = 4min</td>
  </tr>
  <tr>
    <td><img src="https://github.com/europython2023gametournament/supremacy/assets/39047984/07e66dc0-ed5d-4e2b-91f6-b7302e1e0a4f" width="100%" /></td>
    <td><img src="https://github.com/europython2023gametournament/supremacy/assets/39047984/d1dd0cb0-2b6f-4904-ac99-f842b4771099" width="100%" /></td>
  </tr>
</table>

## Goal

- Mine resources to build an army
- Destroy enemy bases and eliminate other players

## Rounds

- All participants play on the map at the same time
- Each round lasts 8 minutes
- The tournament will consist of 8(?) rounds of 8 minutes

## Game map

- The map is auto-generated every round
- It has periodic boundary conditions (for example when a vehicle arrives at the right edge of the map, it will re-appear at the left edge)
- The map size will scale with the number of players (more players = larger map)
- Coordinate system: lower left corner: `(x=0, y=0)`, upper right corner: `(x=nx, y=ny)`

## Mining

- Everyone starts with 1 base, housing 1 mine
- Every timestep, each mine will extract `crystal = 2 * number_of_mines`
- Crystal is used to build mines and vehicles
- Mines too close to other mines compete for resources: `crystal = 2 * number_of_mines / number_of_bases_inside_square_of_80px`
- Bases that contain mines that are competing with others will have a “C” label on them:

![Screenshot at 2023-06-22 21-58-52](https://github.com/europython2023gametournament/supremacy/assets/39047984/e2df2246-532e-4989-9892-582d53d171a8)

## Fights

- Whenever two or more vehicles or bases from opposing teams come within 5px from each other, they will fight
- During each time step, every object hits all the others with its attack force, and it takes damage from all other objects

## Vehicles

<table>
  <tr>
    <th></th>
    <th>Tank &nbsp;&nbsp;&nbsp; <img src="https://github.com/europython2023gametournament/supremacy/assets/39047984/0be25f1b-9d14-4438-b5cb-3a355a6b088a" />
</th>
    <th>Ship &nbsp;&nbsp;&nbsp; <img src="https://github.com/europython2023gametournament/supremacy/assets/39047984/248ab310-2a53-4132-9179-b360ebbb45f4" />
</th>
    <th>Jet &nbsp;&nbsp;&nbsp; <img src="https://github.com/europython2023gametournament/supremacy/assets/39047984/594f9902-e848-465a-a5f2-5d9081d4b863" />
</th>
  </tr>
  <tr>
    <td>Speed</td>
    <td>10</td>
    <td>5</td>
    <td>20</td>
  </tr>
  <tr>
    <td>Attack</td>
    <td>20</td>
    <td>10</td>
    <td>30</td>
  </tr>
  <tr>
    <td>Health</td>
    <td>50</td>
    <td>80</td>
    <td>50</td>
  </tr>
  <tr>
    <td>Cost</td>
    <td>500</td>
    <td>2000</td>
    <td>4000</td>
  </tr>
  <tr>
    <td>Can travel</td>
    <td>On land</td>
    <td>On sea</td>
    <td>Anywhere</td>
  </tr>
  <tr>
    <td></td>
    <td></td>
    <td>Can turn into base</td>
    <td></td>
  </tr>
</table>



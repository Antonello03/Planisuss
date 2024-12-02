[33mb77482b[m[33m ([m[1;36mHEAD -> [m[1;32mmain[m[33m)[m Merge branch 'main' of https://github.com/Antonello03/Planisuss
[33m8b3f3a5[m[33m ([m[1;31morigin/main[m[33m, [m[1;31morigin/HEAD[m[33m)[m Merge pull request #1 from Antonello03/master
[33m7343332[m[33m ([m[1;31morigin/master[m[33m)[m CHANGES IN CREATURES: new energy function using exponential, added changeEnergy() for animals and groups, ADDEDD CARVIZ LOGIC (missing pride logic), changes in INTERFACE (print statements commented), changes in WORLD: added day counting in the env, making carviz move, FIXED a problem where herds leaving an individual behind make him disappear from the cell
[33m7f9f71f[m merge
[33m087f910[m Merge branch 'main' of https://github.com/Antonello03/Planisuss
[33mf1ff5d9[m minor changes
[33mb878fb8[m Fixed the inverted axis problem
[33m34849b4[m fixed the inverted axis problem in the interface
[33m19fe2d3[m CREATURES.PY added abstract calss Species to avoid redundancy, added MoveChoice to better handles choices and elements like leaving individuals from groups, modified rankMoves (now returns dict + some minor adjustment but still need to fix). CHANGES IN WORLD.PY: added getPrides, getAloneCarviz, extended removeGroup for prides, updated move so that a dictionary can be used which is more straightforward, updated nextDay to allow splitting groups dynamics (only erbasts)
[33m16a4da1[m Merge branch 'main' of https://github.com/Antonello03/Planisuss
[33m796b026[m added herd grazing logic with social attitude reduction and division of available Vegetob, added aging (every 10 days reduction of energy by AGING amount)
[33m51bfa38[m Merge branch 'main' of https://github.com/Antonello03/Planisuss
[33m3f903a5[m some tests on main
[33md47b96f[m Merge branch 'main' of https://github.com/Antonello03/Planisuss
[33m7620831[m minor updates and fix in creatures, fixed move in world.py, updated nextDay to allow herds and staying animals, minor fixes
[33m82107fb[m Merge branch 'main' of https://github.com/Antonello03/Planisuss
[33m3b3503a[m interface changes
[33m74b6594[m creatures: added joinGroups for herds (missing knowledge joining, need to check correct functioning of numcomponents), fixed getHErds, added joining herds in a cell logic
[33m1ffd6bd[m CHANGES in CREATURES: each animal is associated with its social group. CHANGES IN WORLD: now its possible to retrieve all herds from environment and all erbasts that are alone. method add updated which can add animals or herds veryfying the eventual creation of new herds, some logics are still missing like joining herd logic, same thing for remove and move, cells repr now contains their coords. each landcell now contains a dictionary for erbasts and carvizes. SUMMARY:  I added herds initial components
[33m0aaec2b[m Merge branch 'main' of https://github.com/Antonello03/Planisuss
[33mf3a4109[m some tests
[33md342f85[m added function display initial setup, fixed pause and play buttom
[33m1a1a468[m updated herd movement
[33m0a3948d[m minor changes
[33mc18a6cf[m Added Escape logic for an erbast when it sees a Carviz. not added yet to Herd
[33m2936f9c[m Merge branch 'main' of https://github.com/Antonello03/Planisuss
[33mfb81278[m CHANGES IN WORLD.PY : addGroup (tbd), moveAnimals (fixed moving logic problems about shallow copy / deep copy), initial socialGroup implementation in LandCell \n CHANGES IN CREATURES.PY: fixed ID's not being correctly assigned, major SocialGroup update, with getNeighborhood size 2, herd rankMoves implemented (can view up to 2 cells and correctly assign danger)
[33m754a2c5[m Merge branch 'main' of https://github.com/Antonello03/Planisuss
[33m22d5d2d[m updated the code for the visualization, added Erbasts and Carviz. Having some problems with the pause and resume buttoms
[33m0b721ef[m revisited rankMoves (nearby cells to carviz are also dangerous, better internal code of the function), minor new methods
[33mf393303[m Merge branch 'main' of https://github.com/Antonello03/Planisuss
[33m73142c5[m Merge branch 'main' of https://github.com/Antonello03/Planisuss
[33me4dfa89[m updated interface
[33m96d8c0e[m minor changes
[33m391f1d2[m added id for each erbast/carviz, now rankMoves takes as argument the worldgrid, added grazing but not in the environment, now the environment has knowledge of tis individuals, added add remove and move animals methods to env, added a simple dynamic update it nextday where vegetob grow and erbasts move, the main displays and example of these changes
[33mc27acf1[m minor changes
[33m472fe27[m Carviz can now rank moves
[33m6cb1724[m minor changes
[33mea52e7c[m added rankMoves method for Erbast, now they can choose the most suitable nextCell
[33m644fdaf[m vegetob density is not anymore constant
[33m3e509fb[m minor optimization on interface, line 57
[33mdb57fb4[m merging
[33m53817ef[m Merge branch 'main' of https://github.com/Antonello03/Planisuss
[33m292ee10[m now each Animal can perceive its surrounding trough getNeighborhood, other attributes are also added to the animal class
[33m21a79ed[m Merge branch 'main' of https://github.com/Antonello03/Planisuss
[33m821d202[m added first individuals visualization
[33me62e727[m now each landCell is initialized with a Vegetob population with density 25/100
[33m5b4a6f9[m creatures structure step 1
[33m5835aac[m added the dynamic threshold
[33m751ae9a[m Implemented cells and now interface is a classed. Added Main
[33mc510f32[m world islands and water generation with a thing called fbm
[33mda093c4[m minor changes
[33mf8c30cf[m I splitted the environment by the world grid so that one can handle the evolution logic anthe other class can handle world generation and parameters
[33me1e7e69[m I divided the environment and its visualization in two different files
[33m1243e48[m I did some reorganization
[33m7185991[m tutorials and pdfs resources added, also constants
[33mf057617[m funcanimation testing, ready to start?
[33mb09caf4[m test with func matplotlib and game of life from ferrari's lectures
[33m241ec52[m other test
[33m10d6122[m branch test
[33me4e26d1[m Update README.md
[33m2aff348[m Initial commit

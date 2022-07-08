# Random Dungeon Generation with Wave Form Collapse. 


https://user-images.githubusercontent.com/72634238/177887699-98318b7d-b8c9-4840-8ac1-c82b13f7e397.mp4


Poor Wiz the Wizard.  Forever chasing his dog Smog through a dungeon endlessly.

Using Djikstra flooding, and WFC, Smog, in his endless pursuit of strawberries, is being chased by his owner, a drunken Wiz the Wizard.
The dungeon is remade with the current state of the dungeon in the target area acting as an intial condition for WFC.

The constraints are based on the Rooms constraints found in mxgmn git hub.

For easyness, I import constraints as a tiled image.  Such as this:

Rooms Constraints

![crawler_constraints](https://user-images.githubusercontent.com/72634238/177886420-8358fa03-7ddf-48da-bf37-e73cc242b4e8.png)


There are technical difficulties with the approach I have taken and is thus a prototype of integrating WFC in pygame projects.  

Improving the time it takes to solve larger arrays may come from adding backjump to the backtrack algorithm. Or perhaps, allowing the pausing and resuming of a search.  Using numpy arrays in the Wave class may help as well.  And, I am curious how a different algorithm may work as suggested by BorisTheBrave and used by Debroglie.

The main problem of course is just what to do when an area fails to generate according to the constraints.  Perhaps using Djikstra flooding to deal with the closest problem areas first, modifiying tile weights so 'walls' are more likely.  Or expanding the tile set to include safe terminating tiles.  I don't know.

Numpy is Required.

Sources:

https://github.com/mxgmn/WaveFunctionCollapse

https://github.com/PhyM73/WaveFunctionCollapse_DASC_project

https://github.com/BorisTheBrave/DeBroglie


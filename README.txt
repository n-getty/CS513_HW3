Example usage:

python aerial.py --lat1 41.888127 --lat2 41.88447 --long1 -87.633972 --long2 -87.63092 --level 20 --out test.png

The above will produce the resuslts seen in test.png, which show exactly the bounds seen in the bing map image in TestCoords.png

Note that the default level is maximum, if the maximum resolution is not available the image will be blank and you will have to decrease the level.

The tiles are stitched together and the image is cropped according to the pixel location of the original input coordinates.
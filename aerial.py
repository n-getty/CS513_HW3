import argparse
import math
import requests
from PIL import Image
from StringIO import StringIO

level = 23

min_lat = -85.05112878;
max_lat = 85.05112878;
min_long = -180;
max_long = 180;


def get_parser():
    parser = argparse.ArgumentParser(description='Retrieve aerial image given bounding box')
    parser.add_argument("--lat1", default=0.0, type=float, help="first latitude")
    parser.add_argument("--lat2", default=0.1, type=float, help="second latitude")
    parser.add_argument("--long1", default=0.0, type=float, help="first longitude")
    parser.add_argument("--long2", default=0.1, type=float, help="second longitude")
    parser.add_argument("--out", default='out.png', type=str, help="output file location")
    parser.add_argument("--level", default=23, type=int, help="level of detail")
    return parser


def clip(n, minValue, maxValue):
    return min(max(n, minValue), maxValue);


def get_tile(lat,long):
    lat = clip(lat, min_lat, max_lat)
    long = clip(long, min_long, max_long)

    sinLatitude = math.sin(lat * math.pi / 180)

    pixelX = int(((long + 180) / 360.0) * 256 * (2 ** level))

    pixelY = int((0.5 - math.log((1 + sinLatitude) / (1 - sinLatitude)) / (4 * math.pi)) * 256 * 2 ** level)

    map_size = 256 << level

    pixelX = clip(pixelX, 0, map_size - 1)
    pixelY = clip(pixelY, 0, map_size - 1)

    tileX = int(math.floor(pixelX/256))

    tileY = int(math.floor(pixelY/256))

    rX = pixelX % 256
    rY = pixelY % 256

    return tileX, tileY, rX, rY


def get_quadkey(tileX, tileY):
    quadkey = ''
    for i in range(1, level + 1)[::-1]:
        digit = 0;
        mask = 1 << (i - 1);
        if tileX & mask:
            digit += 1
        if tileY & mask:
            digit += 2

        quadkey += str(digit);

    return quadkey


def between_keys(tile1, tile2):
    between = []
    if tile1[0] < tile2[0] and tile1[1] < tile2[1]:
        ne_tile, sw_tile = tile1, tile2
    elif tile1[0] > tile2[0] and tile1[1] > tile2[1]:
        sw_tile, ne_tile = tile1, tile2
    else:
        return [get_quadkey(tile1[0], tile1[1])]
    cur = ne_tile[:]
    while cur[1] <= sw_tile[1]:
        row = []
        while cur[0] <= sw_tile[0]:
            row.append(get_quadkey(cur[0], cur[1]))
            cur[0] += 1
        between.append(row)
        cur[1] += 1
        cur[0] = ne_tile[0]

    return between


def get_imgs(quads):
    base_url = 'http://h0.ortho.tiles.virtualearth.net/tiles/h'
    end_url = '.jpeg?g=131'

    tiles = []
    i=0
    for row in quads:
        t = []
        for q in row:
            i+=1
            url = base_url + q + end_url
            tile = StringIO(requests.get(url).content)
            img = Image.open(tile)
            t.append(img)
        tiles.append(t)

    return tiles


def pil_grid(images, rX1, rX2, rY1, rY2):
    width = len(images[0])
    pix_width = images[0][0].size[0]
    pix_height = images[0][0].size[1]
    shape = (pix_width * width, pix_height * len(images))
    im_grid = Image.new('RGB', shape, color='white')

    for i, row in enumerate(images):
        for j, im in enumerate(row):
            im_grid.paste(im, (pix_width * j, pix_height * i))


    # Crop tile grid by original box specifications
    im_grid = im_grid.crop((rX1, rY1, im_grid.size[0] - (256-rX2), im_grid.size[1] - (256-rY2)))
    return im_grid


def main():
    parser = get_parser()
    args = parser.parse_args()
    global level
    level = args.level

    # Testing coords
    #lat1, long1 = 41.888127, -87.633972
    #lat2, long2 = 41.88447, -87.63092

    #lat1, long1 = 85, -180
    #lat2, long2 = -85, 180

    #tileX1, tileY1, rX1, rY1 = get_tile(lat1, long1)
    #tileX2, tileY2, rX2, rY2 = get_tile(lat2, long2)

    print "Getting input coordinate tiles and pixels"
    tileX1, tileY1, rX1, rX2 = get_tile(args.lat1, args.long1)
    tileX2, tileY2, rY1, rY2 = get_tile(args.lat2, args.long2)

    print "Generating keys between tiles"
    keys = between_keys([tileX1, tileY1], [tileX2, tileY2])

    print "Retrieving images for each key"
    imgs = get_imgs(keys)

    print "Stitching images and cropping to fit box"
    stitched = pil_grid(imgs, rX1, rX2, rY1, rY2)

    print "Saving image"
    stitched.save(args.out)


if __name__ == '__main__':
    main()
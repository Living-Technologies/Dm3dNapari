#!/usr/bin/env python

import binarymeshformat as bmf
from napari.layers import Surface
import napari, numpy

class ImageDetails:
    def __init__(self, img_layer):
        dims = img_layer.data.shape
        scales = img_layer.scale
        self.lx = scales[-1]*dims[-1]
        self.ly = scales[-2]*dims[-2]
        self.lz = scales[-3]*dims[-3]
    def getScale(self):
        f = max(self.lx, self.ly, self.lz)
        return numpy.array([1, f, f, f])
    def getOffset(self):
        return numpy.array([0, self.lz/2, self.ly/2, self.lx/2])

def trackToSurface(track):
    allPositions = None
    allIndexes = None
    for tm in track.meshes:
        mesh = track.meshes[tm]
        pos = numpy.array(mesh.positions).reshape( (len(mesh.positions)//3, 3) )
        pos = numpy.flip(pos, 1)
        t = numpy.ones((pos.shape[0], 1))*tm
        tzyx = numpy.concatenate( (t, pos), axis=1 )
        indexes = numpy.array( mesh.triangles ).reshape( (len(mesh.triangles)//3, 3 ) )
        if allPositions is None:
            allPositions = tzyx
            allIndexes = indexes
        else:
            indexes = indexes + allPositions.shape[0]
            allPositions = numpy.concatenate((allPositions, tzyx), axis=0)
            allIndexes = numpy.concatenate((allIndexes, indexes), axis=0)
    print(allIndexes.dtype)
    return Surface( (allPositions, allIndexes) )


def load_meshes():
    tracks = bmf.loadMeshTracks("sample.bmf");
    viewer = napari.viewer.current_viewer()
    img = viewer.layers[0]
    details = ImageDetails(img)
    for t in tracks:
        surf = trackToSurface(t)
        surf.scale = details.getScale()
        surf.translate = details.getOffset()
        viewer.add_layer(surf)


if __name__=="__main__":
    import skimage
    img = napari.layers.Image(skimage.io.imread("sample.tif"))

    viewer = napari.viewer.Viewer(ndisplay=3)
    viewer.add_layer(img)
    load_meshes()
    napari.run()

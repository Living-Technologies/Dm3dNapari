#!/usr/bin/env python

import binarymeshformat as bmf
from napari.layers import Surface, Layer, Image
from napari.utils import notifications

import napari, numpy
import pathlib

from napari.utils import progress

class ImageDetails:
    def __init__(self, img_layer):
        if img_layer is None:
            dims = [1, 1, 1]
            scales = [1, 1, 1]
        else:
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
    """
        Converts a dm3d track to a napari surface. The track stores
        points as {t : (x, y, z) } and that gets converted to (t, z, y, x)
        vertex values.
    """
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
    return Surface( (allPositions, numpy.array(allIndexes, dtype=int), numpy.ones(len(allPositions)) ) )



def load_meshes(layer: Image, file_path: pathlib.Path):
    """
        Loads the provide mesh file and scales the meshes to be
        displayed with the provided image layer.

        If the provided image layer is none, then the meshes will
        not be scaled.
    """
    if file_path.is_dir():
        msg = "Select a file to load image from, %s is a folder."%file_path
        notifications.show_error(msg)
        return
    elif not file_path.exists():
        msg = "The selected file, %s, does not exist"%file_path
        notifications.show_error(msg)
        return
    pbr = progress(total = 100)
    pbr.set_description("loading file.")
    try:
        tracks = bmf.loadMeshTracks(file_path);
    except Exception as e:
        notifications.show_error("Could not meshes from file %s \n %s"%(file_path, e))
        return
    pbr.set_description("meshes loaded, converting ...")
    if layer is None:
        notifications.show_warning("scale information cannot be extracted from layer %s"%layer)
    details = ImageDetails(layer)
    viewer = napari.viewer.current_viewer()
    pbr.update(5)
    step = int(95/len(tracks)) + 1
    for t in tracks:
        surf = trackToSurface(t)
        surf.scale = details.getScale()
        surf.translate = details.getOffset()
        surf.name = t.name
        viewer.add_layer(surf)
        pbr.update(step)
    pbr.close()

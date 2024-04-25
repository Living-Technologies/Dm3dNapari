import napari, skimage, sys, pathlib
from napari_bmf_bridge import load_meshes


if __name__=="__main__":
    viewer = napari.viewer.Viewer(ndisplay=3)
    if len(sys.argv) > 2:
        img = napari.layers.Image(skimage.io.imread(sys.argv[2]))
        l = viewer.add_layer(img)
    else:
        l = None

    load_meshes(l, pathlib.Path(sys.argv[1]))
    napari.run()

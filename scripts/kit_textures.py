"""Kit texture helpers for FIFA 16 -> FIFA 17 conversion.

FIFA 16 exports (CmCli export-kit) one colour atlas per kit in team_<id>_kit_<n>_tex_3.png (1024x512).
The top part of that atlas holds the socks. FIFA 17 has a separate socks_<id>_<n>_0_color texture
(512x256), so the socks must be cut out of the FIFA 16 atlas and resized.

SOCKS_BOX was fitted by brute force against socks made by hand in Photoshop:
  FCSB (fcsb/home-shorts.png -> socks_269_0_0_color.png): box (208, 12, 820, 186), mean error 14/255
  CFR  (cfr/homekit_shorts.png -> socks_271_0_0_color.png): box (244, 0, 784, 150), mean error 5.6/255
The box differs between kit templates, so the default is the FCSB one. Always check the preview and
pass --box x0 y0 x1 y1 when a kit needs a different crop.
"""
import argparse
import os
from PIL import Image

SOCKS_BOX = (208, 12, 820, 186)
SOCKS_SIZE = (512, 256)


def socks_from_f16_atlas(atlas_png, out_png, box=SOCKS_BOX):
    atlas = Image.open(atlas_png).convert("RGBA")
    if atlas.size != (1024, 512):
        raise ValueError(f"{atlas_png}: expected a 1024x512 FIFA 16 atlas, got {atlas.size}")
    socks = atlas.crop(box).resize(SOCKS_SIZE, Image.LANCZOS)
    socks.save(out_png)
    return out_png


def main():
    parser = argparse.ArgumentParser(description="Cut FIFA 17 socks out of a FIFA 16 kit atlas (tex_3 png)")
    parser.add_argument("atlas_png")
    parser.add_argument("out_png")
    parser.add_argument("--box", nargs=4, type=int, default=SOCKS_BOX, metavar=("X0", "Y0", "X1", "Y1"))
    args = parser.parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(args.out_png)), exist_ok=True)
    print(socks_from_f16_atlas(args.atlas_png, args.out_png, tuple(args.box)))


if __name__ == "__main__":
    main()

"""Build a 3D league logo mesh in the FBX structure Frosty expects, from a flat logo PNG.

    python scripts/league_logo_mesh.py <template_ascii.fbx> <logo.png> <out.fbx> <palette_out.png> [options]

How it looks: like the original league logos (flat extruded shapes + a tiny colour-palette `_color` texture) instead
of one blurry textured slab. The logo is split into a few flat colours (PALETTE). A white base slab follows the alpha
silhouette; every other colour is extruded as a thin raised layer on top of it. Edges are real geometry, so they stay
sharp at any zoom. Every vertex uses a UV that points at the centre of its colour cell in the palette texture
(`palette_out.png`, 64x64, 4x4 cells of 16x16 px; this is the new `leaguelogo_<id>_color`).

<template_ascii.fbx> is an ASCII FBX exported from the original league logo mesh with FrostyMeshCli
(export-mesh <ebx> <out.fbx> - 2013 Centimeters ascii). Node names, LOD/model structure and material name are kept;
only the geometry arrays are replaced.

Needs: numpy, pillow, opencv-python-headless, mapbox-earcut (only for this tool, not in requirements.txt).
"""
import argparse
import re

import cv2
import mapbox_earcut as earcut
import numpy as np
from PIL import Image

# dominant colours of Liga_I_logo.png (k-means), index 0 is the base colour
PALETTE = [(254, 254, 254), (248, 90, 3), (101, 102, 99), (218, 213, 205), (29, 32, 31), (164, 167, 169), (160, 53, 1), (249, 149, 92)]
CELL, TEX = 16, 64


def label_map(png, scale, sigma):
    """Per-class smooth label map at `scale` x the PNG size; -1 = transparent."""
    img = np.asarray(Image.open(png).convert("RGBA"))
    h, w = img.shape[:2]
    rgb = img[..., :3].astype(np.float32)
    opaque = img[..., 3] >= 128
    dist = np.stack([np.linalg.norm(rgb - np.array(c, np.float32), axis=2) for c in PALETTE], axis=2)
    lab = np.where(opaque, dist.argmin(axis=2), -1)
    classes = list(range(len(PALETTE))) + [-1]
    soft = []
    for k in classes:
        m = (lab == k).astype(np.float32)
        m = cv2.resize(m, (w * scale, h * scale), interpolation=cv2.INTER_LINEAR)
        soft.append(cv2.GaussianBlur(m, (0, 0), sigma))
    best = np.argmax(np.stack(soft, axis=2), axis=2)
    out = np.array(classes)[best]
    return out, (w, h)


def rings_of(mask):
    """[(outer ring, [hole rings])] as float arrays of pixel coordinates (scaled image space)."""
    found, hier = cv2.findContours(mask.astype(np.uint8) * 255, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    if hier is None:
        return []
    res = {}
    for i, c in enumerate(found):
        ring = cv2.approxPolyDP(c, 1.0, True).reshape(-1, 2).astype(np.float64)
        if len(ring) < 3 or abs(cv2.contourArea(ring.astype(np.float32))) < 6:
            continue
        parent = hier[0][i][3]
        if parent == -1:
            res.setdefault(i, [ring, []])
        elif parent in res:
            res[parent][1].append(ring)
    return [(o, hs) for o, hs in res.values()]


class Mesh:
    def __init__(self):
        self.pos, self.nrm, self.tan, self.bin, self.uv, self.tris = [], [], [], [], [], []

    def v(self, p, n, t, b, uv):
        self.pos.append(p); self.nrm.append(n); self.tan.append(t); self.bin.append(b); self.uv.append(uv)
        return len(self.pos) - 1

    def tri(self, a, b, c, want):
        """Add a triangle whose geometric normal points along `want`."""
        g = np.cross(np.subtract(self.pos[b], self.pos[a]), np.subtract(self.pos[c], self.pos[a]))
        self.tris.append((a, b, c) if np.dot(g, want) >= 0 else (a, c, b))


def signed_area(r):
    x, y = r[:, 0], r[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)


def add_prism(mesh, outer, holes, z0, z1, uv, back):
    """Extrude one polygon (with holes) between z0 (bottom) and z1 (top): top face, side walls, optional bottom face."""
    rings = [outer] + holes
    flat = np.vstack(rings)
    ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
    tri = earcut.triangulate_float64(flat, ends).reshape(-1, 3)
    top = [mesh.v((p[0], p[1], z1), (0, 0, 1), (1, 0, 0), (0, 1, 0), uv) for p in flat]
    for a, b, c in tri:
        mesh.tri(top[a], top[b], top[c], (0, 0, 1))
    if back:
        bot = [mesh.v((p[0], p[1], z0), (0, 0, -1), (-1, 0, 0), (0, 1, 0), uv) for p in flat]
        for a, b, c in tri:
            mesh.tri(bot[a], bot[b], bot[c], (0, 0, -1))
    start = 0
    for ri, ring in enumerate(rings):
        n = len(ring)
        ccw = signed_area(ring) > 0
        for k in range(n):
            p0, p1 = ring[k], ring[(k + 1) % n]
            d = p1 - p0
            ln = float(np.hypot(*d))
            if ln < 1e-9:
                continue
            right = (d[1] / ln, -d[0] / ln)
            outward = right if ccw else (-right[0], -right[1])
            if ri > 0:  # holes: the solid is outside the ring, so the wall faces into the hole
                outward = (-outward[0], -outward[1])
            nn = (outward[0], outward[1], 0.0)
            tt = (d[0] / ln, d[1] / ln, 0.0)
            q = [mesh.v((p0[0], p0[1], z1), nn, tt, (0, 0, 1), uv), mesh.v((p1[0], p1[1], z1), nn, tt, (0, 0, 1), uv),
                 mesh.v((p1[0], p1[1], z0), nn, tt, (0, 0, 1), uv), mesh.v((p0[0], p0[1], z0), nn, tt, (0, 0, 1), uv)]
            mesh.tri(q[0], q[1], q[2], nn)
            mesh.tri(q[0], q[2], q[3], nn)
        start += n


def build(png, width_m, half_depth, raise_m, scale, sigma):
    labels, (w, h) = label_map(png, scale, sigma)
    height_m = width_m * h / w
    W, H = w * scale, h * scale

    def to_xy(r):
        out = np.empty_like(r)
        out[:, 0] = (r[:, 0] / W - 0.5) * width_m
        out[:, 1] = (0.5 - r[:, 1] / H) * height_m
        return out

    def cell_uv(k):
        cx, cy = (k % 4) * CELL + CELL / 2, (k // 4) * CELL + CELL / 2
        return (cx / TEX, 1.0 - cy / TEX)

    mesh = Mesh()
    # base slab: whole silhouette, base colour, with a back face
    for outer, holes in rings_of(labels != -1):
        add_prism(mesh, to_xy(outer), [to_xy(x) for x in holes], -half_depth, half_depth, cell_uv(0), back=True)
    # raised colour layers
    for k in range(1, len(PALETTE)):
        for outer, holes in rings_of(labels == k):
            add_prism(mesh, to_xy(outer), [to_xy(x) for x in holes], half_depth, half_depth + raise_m, cell_uv(k), back=False)
    return mesh, (width_m, height_m)


def palette_png(path):
    img = Image.new("RGB", (TEX, TEX), PALETTE[0])
    for k, c in enumerate(PALETTE):
        x0, y0 = (k % 4) * CELL, (k // 4) * CELL
        img.paste(c, (x0, y0, x0 + CELL, y0 + CELL))
    img.save(path)


def fmt(values, per_line=24):
    flat = [("%.9g" % v) for v in np.asarray(values).reshape(-1)]
    return ",\n".join(",".join(flat[i:i + per_line]) for i in range(0, len(flat), per_line))


def replace_array(text, name, values, count):
    pat = re.compile(r"(\b" + name + r": )\*\d+( \{\s*a: )(.*?)(\s*\})", re.S)
    assert pat.search(text), name
    return pat.sub(lambda m: f"{m.group(1)}*{count}{m.group(2)}{fmt(values)}{m.group(4)}", text, count=1)


def remove_block(text, header):
    i = text.index(header)
    depth, k = 0, text.index("{", i)
    while True:
        depth += (text[k] == "{") - (text[k] == "}")
        if depth == 0:
            break
        k += 1
    line_start = text.rfind("\n", 0, i) + 1
    return text[:line_start] + text[k + 1:].lstrip(" \t").lstrip("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template"); ap.add_argument("logo"); ap.add_argument("out"); ap.add_argument("palette_out")
    ap.add_argument("--width", type=float, default=0.94)
    ap.add_argument("--half-depth", type=float, default=0.02)
    ap.add_argument("--raise", dest="raise_m", type=float, default=0.012, help="height of the colour layers above the base")
    ap.add_argument("--scale", type=int, default=8)
    ap.add_argument("--sigma", type=float, default=6.0)
    a = ap.parse_args()

    mesh, size = build(a.logo, a.width, a.half_depth, a.raise_m, a.scale, a.sigma)
    pos, nrm, tan, bin_, uv = (np.array(x) for x in (mesh.pos, mesh.nrm, mesh.tan, mesh.bin, mesh.uv))
    tris = np.array(mesh.tris, dtype=np.int64)
    n, t = len(pos), len(tris)
    print(f"vertices {n}, triangles {t}, size {size[0]:.3f} x {size[1]:.3f} x {2 * a.half_depth + a.raise_m:.3f}")
    if n > 65000:
        raise SystemExit("too many vertices for 16-bit indices")

    text = open(a.template, encoding="latin-1").read()
    text = replace_array(text, "Vertices", pos, n * 3)
    poly = tris.copy()
    poly[:, 2] = -poly[:, 2] - 1
    text = replace_array(text, "PolygonVertexIndex", poly, t * 3)
    text = replace_array(text, "Normals", nrm, n * 3)
    text = replace_array(text, "Binormals", bin_, n * 3)
    text = replace_array(text, "Tangents", tan, n * 3)
    text = replace_array(text, "UV", uv, n * 2)
    text = remove_block(text, "\t\tEdges: *")
    text = remove_block(text, "\t\tLayerElementSmoothing: 0 {")
    text = re.sub(r"\t\t\tLayerElement:\s*\{\s*Type: \"LayerElementSmoothing\"\s*TypedIndex: 0\s*\}\s*", "", text)
    open(a.out, "w", encoding="latin-1", newline="\n").write(text)
    palette_png(a.palette_out)
    print("wrote", a.out, "and", a.palette_out)


if __name__ == "__main__":
    main()

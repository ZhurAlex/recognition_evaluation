# Annotation Quality Assessment (IoU)

The script compares an image annotation (`annotated/`) against the ground truth (`ground_truth/`). For each object it reports the match percentage as IoU: the intersection area divided by the union area. For the whole image it computes a total score, Σ intersections / Σ unions, so an error on a large object weighs more than an error on a small one.

## Running

Requires Python 3.10+ (the code uses `match`). Tested on 3.13.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

The result is printed to the console and saved to `report.txt`.

### Input data

The data is not included in the repository (`.gitignore`). The script expects the following structure:

```
ground_truth/
  road.jpg.json
  road.jpg.images/00001/<nm>.png   # ground truth polygon masks
annotated/
  road.jpg.json
```

If the data is not available, the ready result is in [`report.txt`](report.txt).

## Result

```
GT(nm)   Annotated(nm)   Type                                    GT px  Ann px      IoU
---------------------------------------------------------------------------------------
0.1      0.3             car                                      1841    2032    85.6%
0.6      0.6             road sign                                  81      80    80.9%
0.2      0.9             car                                       503     428    75.3%
0.3      0.2             car                                       440     631    69.7%
0.7      0.8             road_barrier                             2377    4609    49.3%
0.8      0.1             road_barrier                             3568    7793    39.8%
0.5      0.7             road sign                                 783    1564    39.7%
0.4      -               car (missed)                               94       -     0.0%
-        0.5             road sign (false positive)                  -     143     0.0%

Total IoU: 49.3% (8904 / 18063 px)
```

The total of about 49% is driven by the barriers: in the annotation they are outlined roughly twice as large as in the ground truth. The missed object and the false positive are both small, so they barely affect the total.

## How it works

1. **Loading** (`loader.py`). Object metadata and geometry are stored in different parts of the JSON; they are merged by `nm`.
2. **Masks** (`picture_object.py`). Each object is converted into a boolean mask the size of the frame, and IoU is computed pixel by pixel. The way a mask is built depends on the data:
   - a polygon with vertices (`path`, annotation) is rasterized with Pillow;
   - a polygon without vertices (ground truth) is read from the PNG mask by palette index;
   - a bBox is built using the annotation tool's rule: coordinates are rounded down, and the right and bottom edges are excluded. The rule was verified pixel-exact against the ground truth PNG masks.
3. **Matching** (`matching.py`). `nm` values in the ground truth and the annotation do not correspond, so objects are matched by geometry:
   - intersection and union matrices are computed for all pairs;
   - pairs are chosen greedily in descending order of IoU, and each object takes part in at most one pair;
   - the object type does not affect matching; a type mismatch is marked as `mismatch` in the report;
   - there is no threshold: any intersection with IoU > 0 counts as a pair.
4. **Total.** Objects without a pair get 0%. Missed ground truth objects and false positives from the annotation add their area to Σ unions.
5. **Report** (`report.py`). The same table is printed to the console and written to the file.

## Verification

- The ground truth compared with itself gives 100% for every object.
- bBox masks built from coordinates match the ground truth PNG masks pixel-exact.
- A separate cross-check with the Hungarian algorithm (`scipy`, not part of the code) produced the same pairs and the same total as the greedy one on this data.

## AI usage

[`AI_USAGE.md`](AI_USAGE.md) covers the key points: how AI was used, which decisions were made and by whom, verification and limitations. The chat log is in `docs/ai_chat_log.md`.

## Limitations

- The image name (`road.jpg`) and the frame number (`00001`) are hardcoded in `main.py` and `loader.py`.
- Only the first contour of `path` is used. In the current data there is always exactly one.
- Annotation polygons are rasterized by Pillow, which includes boundary pixels. There may be a one-pixel offset relative to the rule used to produce the ground truth masks. This cannot be verified: the ground truth has no polygon vertices.

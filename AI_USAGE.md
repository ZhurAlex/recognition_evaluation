# AI Usage in the Project

Assistant: Claude Code (Claude Opus 5.5).
Chat log: `docs/ai_chat_log.md`.

## How AI was used

- AI analyzed the input data format and proposed a step-by-step solution plan with options for each step. The developer made the decision at every step (see the decisions table).
- Work was done in assistant mode: AI proposed options, explained, verified results on the data and reviewed code.
- The developer wrote the code responsible for the logic personally, in order to fully understand how it works: merging the JSON, the `PictureObject` class with building masks from polygons and PNGs, computing intersections and unions, matching candidates and the total score, the report structure and `main`.
- The developer delegated to AI mostly mechanical tasks without complex algorithms, whose code is easy to verify and maintain if needed. The exception is `greedy_matching`: the developer worked out the algorithm (iteration order, sets of used indices), and AI wrote the code from that description.
- Fragments written by AI at the developer's explicit request:
  - the bBox branch in `generate_mask` (rasterization rule, decision 11);
  - splitting `generate_mask` into a dispatcher and three `_mask_from_*` methods (decision 12);
  - `greedy_matching` (from the algorithm worked out by the developer);
  - mechanically moving the code into modules (decision 15): the logic did not change, the output was compared with the previous one;
  - the `match_objects` orchestrator and the updated `main`;
  - `build_message` in `report.py` (table format, decision 18); the developer designed the structure of `report.py`, separating text building from console and file output;
  - fixing the column widths in the table header, and `requirements.txt` (`pip freeze`);
  - `README.md`.
- This document was filled in during development to record the developer's decisions and the use of AI.

## Data specifics

- Polygons are stored differently. In `annotated`, a polygon has vertices in the `path` field. In `ground_truth` there are no vertices; the shape is given by a full-frame PNG mask: `road.jpg.images/00001/<nm>.png`, 1000×667, 1-bit.
- Object ids (`nm`) in the ground truth and the annotation do not correspond. For example, car `0.1` in the ground truth is `0.3` in the annotation, and the annotation contains id `0.9`, which does not exist in the ground truth: it is the car corresponding to ground truth `0.2` (IoU 75.3%). Therefore objects are matched by geometry, not by `nm`.
- The annotation contains errors: a missed object (car `0.4`) and a false positive (sign `0.5`).
- Attributes also differ (`weather`, `oncoming`), but they do not affect IoU.

## Decisions

| # | Decision | Rationale | Decided by |
|---|----------|-----------|------------|
| 1 | Total score = Σ intersections / Σ unions | An error on a large object should weigh more | Task statement |
| 2 | All shapes are converted to masks; IoU is computed by rasterization (pixel by pixel) | The ground truth has only masks, and a vector approach would require reconstructing contours from masks with a loss of precision; one method for both bBoxes and polygons | Proposed by AI, accepted by the developer after discussion |
| 3 | Environment: `.venv` + `requirements.txt`, no poetry | A small project without complex dependencies | Developer |
| 4 | Objects are matched by geometry (maximum IoU), not by `nm` | `nm` values in the ground truth and the annotation do not correspond | Developer |
| 5 | Type is not taken into account in matching; a type mismatch is marked in the report | Correct boundaries with a wrong type give more information than two unrecognized objects | Developer; question raised by AI |
| 6 | No threshold: any intersection with IoU > 0 counts as a pair | A reasonable threshold depends on how the results will be used, and raw values are more informative | Developer |
| 7 | Pairs are chosen greedily in descending order of IoU; the result is cross-checked with the Hungarian algorithm | The greedy algorithm is simpler and more transparent. The cross-check showed that the pairs coincide on this data, so the greedy algorithm was kept in the code | Developer; options proposed by AI, cross-check performed by AI at the developer's request |
| 8 | The folder structure of the ground truth and the annotation is assumed to be the same; paths are built from the folder name | To avoid unnecessary complexity in the code | Developer; AI pointed out that `.images` exists only in the ground truth |
| 9 | Image attributes (`weather`) are not compared | The task concerns objects only | Developer |
| 10 | The frame size is stored in each object as an immutable tuple | No need to pass a separate entity through the code; a tuple prevents accidental modification of shared data | Developer |
| 11 | A bBox mask is built using the annotation tool's rule: coordinates are rounded down, the right and bottom edges are excluded; `ImageDraw.rectangle` is not used | Pillow includes the boundary pixel, and the mask built from ground truth coordinates matched the ground truth's own PNG by only 81–93%. After the fix the match is pixel-exact | Discrepancy found by AI during verification; the developer decided to fix it, AI wrote the code |
| 12 | `generate_mask` is split into a dispatcher and three methods: `_mask_from_path`, `_mask_from_png`, `_mask_from_bbox` | Choosing the method is separated from the implementations; each method can be tested separately and receives only its own arguments | Idea to split: developer; structure proposed and written by AI |
| 13 | The ground truth mask is read by palette index (`np.array(img) > 0`) | `convert("1")` compares brightness with a threshold and zeroes out dark colors: the mask of the red barrier becomes empty. Comparing by `color` works but depends on an extra field | Proposed by AI |
| 14 | Two matrices, intersections and unions, are stored for all pairs; IoU is obtained by dividing them | The total score is Σ intersections / Σ unions, and areas cannot be recovered from a single IoU matrix | Developer; keeping both matrices proposed by AI |
| 15 | The code is split into modules: `picture_object.py`, `loader.py`, `matching.py`, `report.py`, `main.py` | The modules have different responsibilities; dependencies go in one direction, and `matching` knows nothing about JSON or files | Structure: developer; module names proposed by AI |
| 16 | The result is printed to the console and written to a file; the report text is built by a single function | The data is excluded from the repository, and the file makes the result visible without running the script; a shared text keeps the console and the file from diverging | Developer; shared text proposed by AI |
| 17 | The matching result is returned as a dict, not a dataclass | The structure is used only once | Developer |
| 18 | The report shows object areas and pixel sums in the total line | It shows why the total is weighted rather than an average of percentages; a reviewer can recompute the total | Proposed by AI, accepted by the developer |

## Result

- 7 pairs, 1 missed object (ground truth `0.4`, car), 1 false positive (annotation `0.5`, sign). The type matches in all pairs.
- Total score: 8904 / 18063 ≈ **49.3%**.
- Without the missed object and the false positive the total would be 49.9%. Both objects are small and have little effect, while the total is driven by the large barriers with IoU 0.40 and 0.49. This is the area weighting the task requires.
- The main annotation error: both barriers are outlined roughly twice as large as in the ground truth (4609 px vs 2377, 7793 vs 3568). They are what pulls the total down.
- Full report: `report.txt`.

## Verification

- Missed objects and false positives are identified correctly: they match those found during the initial data analysis (missed: ground truth `0.4`; false positive: annotation `0.5`).
- The ground truth compared with itself gives 100% for every object and in total; every object was matched with itself:

| GT (nm) | Annotated (nm) | Type | GT px | Ann px | IoU |
|---------|----------------|------|------:|-------:|----:|
| 0.8 | 0.8 | road_barrier | 3568 | 3568 | 100.0% |
| 0.7 | 0.7 | road_barrier | 2377 | 2377 | 100.0% |
| 0.6 | 0.6 | road sign | 81 | 81 | 100.0% |
| 0.5 | 0.5 | road sign | 783 | 783 | 100.0% |
| 0.4 | 0.4 | car | 94 | 94 | 100.0% |
| 0.3 | 0.3 | car | 440 | 440 | 100.0% |
| 0.2 | 0.2 | car | 503 | 503 | 100.0% |
| 0.1 | 0.1 | car | 1841 | 1841 | 100.0% |

- A cross-check performed by AI with the Hungarian algorithm (`scipy.optimize.linear_sum_assignment`) produced the same pairs and the same total (49.29%) as the greedy algorithm. Therefore the greedy algorithm was kept in the code (decision 7).

## Limitations and possible improvements

- Only the first contour of `path` is used (`path[0]`). In the current data every polygon has exactly one contour. What multiple contours would mean (separate parts of an object or holes) is not described in the format.
- Annotation polygons are rasterized with `ImageDraw.polygon`, which includes boundary pixels. They most likely have the same one-pixel offset that bBoxes had. This cannot be verified: the ground truth has no polygon vertices. Small objects are affected the most.
- Neither the greedy nor the Hungarian algorithm optimizes the total metric. The Hungarian algorithm maximizes the sum of IoU, where all pairs weigh the same, while the total is Σ intersections / Σ unions, where pairs are weighted by area. In dense scenes, where the algorithms diverge, the choice of algorithm should be checked on specific objects.
- The image name (`road.jpg`) and the frame number in the mask path (`00001`) are hardcoded. The script processes a single image with a single frame.
- The data (`annotated/`, `ground_truth/`) is not included in the repository. Without it the script will not run; the result can be viewed in `report.txt`.

import numpy as np


def overlap_areas(mask1, mask2):
    intersection = (mask1 & mask2).sum()
    union = (mask1 | mask2).sum()
    return intersection, union

def overlap_matrices(ground_truth_objects, annotated_objects):
    n = len(ground_truth_objects)
    m = len(annotated_objects)
    inter_matrix = np.zeros((n, m), dtype=int)
    union_matrix = np.zeros((n, m), dtype=int)

    for i, gt_obj in enumerate(ground_truth_objects):
        for j, ann_obj in enumerate(annotated_objects):
            intersection, union = overlap_areas(gt_obj.mask, ann_obj.mask)
            inter_matrix[i, j] = intersection
            union_matrix[i, j] = union

    return inter_matrix, union_matrix

def candidate_pairs(iou_matrix):
    pairs = []
    for i in range(iou_matrix.shape[0]):
        for j in range(iou_matrix.shape[1]):
            if iou_matrix[i, j] > 0:
                pairs.append((float(iou_matrix[i, j]), i, j))
    return pairs

def greedy_matching(pairs, n, m):
    used_gt = set()
    used_ann = set()
    matches = []

    for iou, i, j in sorted(pairs, reverse=True):
        if i in used_gt or j in used_ann:
            continue
        matches.append((i, j, iou))
        used_gt.add(i)
        used_ann.add(j)

    missed = set(range(n)) - used_gt
    false_positives = set(range(m)) - used_ann
    return matches, missed, false_positives

def calculate_total(i_matrix, u_matrix, ground_truth_objects, annotated_objects, matches, missed, false_positives):
    total_intersection = sum(i_matrix[i, j] for i, j, _ in matches)
    total_union = sum(u_matrix[i, j] for i, j, _ in matches) + sum(ground_truth_objects[i].area for i in missed) + sum(annotated_objects[j].area for j in false_positives)
    total_iou = total_intersection / total_union
    return total_intersection, total_union, total_iou

def match_objects(ground_truth_objects, annotated_objects):
    i_matrix, u_matrix = overlap_matrices(ground_truth_objects, annotated_objects)
    iou_matrix = i_matrix / u_matrix

    pairs = candidate_pairs(iou_matrix)
    matches, missed, false_positives = greedy_matching(pairs, len(ground_truth_objects), len(annotated_objects))

    total_intersection, total_union, total_iou = calculate_total(
        i_matrix, u_matrix, ground_truth_objects, annotated_objects, matches, missed, false_positives
    )

    return {
        "matches": matches,
        "missed": missed,
        "false_positives": false_positives,
        "total_intersection": total_intersection,
        "total_union": total_union,
        "total_iou": total_iou,
    }

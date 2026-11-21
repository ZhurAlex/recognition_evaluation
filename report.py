def build_message(ground_truth, annotated, result):
    header = f"{'GT(nm)':<9}{'Annotated(nm)':<16}{'Type':<37}{'GT px':>8}{'Ann px':>8}{'IoU':>9}"
    lines = [header, "-" * len(header)]

    def row(gt_name, ann_name, obj_type, gt_area, ann_area, iou):
        return f"{gt_name:<9}{ann_name:<16}{obj_type:<37}{gt_area:>8}{ann_area:>8}{iou * 100:>8.1f}%"

    for i, j, iou in result["matches"]:
        gt, ann = ground_truth[i], annotated[j]
        if gt.type == ann.type:
            obj_type = gt.type
        else:
            obj_type = f"{gt.type} / {ann.type} (mismatch)"
        lines.append(row(gt.name, ann.name, obj_type, gt.area, ann.area, iou))

    for i in sorted(result["missed"]):
        gt = ground_truth[i]
        lines.append(row(gt.name, "-", f"{gt.type} (missed)", gt.area, "-", 0))

    for j in sorted(result["false_positives"]):
        ann = annotated[j]
        lines.append(row("-", ann.name, f"{ann.type} (false positive)", "-", ann.area, 0))

    lines.append("")
    lines.append(
        f"Total IoU: {result['total_iou'] * 100:.1f}% "
        f"({result['total_intersection']} / {result['total_union']} px)"
    )
    return "\n".join(lines) + "\n"

def print_to_console(message):
    print(message)

def print_to_file(message, filename):
    with open(filename, 'w') as file:
        file.write(message)

def build_report(ground_truth, annotated, result):
    message = build_message(ground_truth, annotated, result)
    print_to_console(message)
    print_to_file(message, 'report.txt')
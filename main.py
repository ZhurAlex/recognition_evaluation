from loader import get_objects_from_json
from matching import match_objects
from report import build_report


def main():
    ground_truth = get_objects_from_json('ground_truth', 'road.jpg')
    annotated = get_objects_from_json('annotated', 'road.jpg')

    result = match_objects(ground_truth, annotated)

    build_report(ground_truth, annotated, result)

if __name__ == "__main__":
    main()

"""Test cases for from_waymo.py."""
import os
import shutil
from argparse import Namespace

from ..common.parallel import NPROC
from ..unittest.util import get_test_file
from .from_waymo import run
from .io import load
from .utils import compare_results


def test_run() -> None:
    """Test Waymo conversion."""
    filepath = get_test_file("waymo_sample")
    result_filepath = get_test_file("waymo_cam_anns.json")
    result_lidar_filepath = get_test_file("waymo_lidar_anns.json")
    output_dir = "./processed/"
    args = Namespace(
        input=filepath,
        output=output_dir,
        save_images=True,
        use_lidar_labels=False,
        nproc=NPROC,
    )
    run(args)
    result = load(os.path.join(output_dir, "scalabel_anns.json")).frames
    result_compare = load(result_filepath).frames
    compare_results(result, result_compare)
    os.remove(os.path.join(output_dir, "scalabel_anns.json"))
    args.use_lidar_labels = True
    run(args)
    result = load(os.path.join(output_dir, "scalabel_anns.json")).frames
    result_compare = load(result_lidar_filepath).frames
    compare_results(result, result_compare)

    paths = [os.path.join(output_dir, cam) for cam in os.listdir(output_dir)]
    for path in paths:
        if os.path.isdir(path):
            assert len(os.listdir(path)) == 2
    assert len(paths) == 6  # 1 sequence * 5 cameras + 1 label file

    # clean up
    shutil.rmtree(output_dir)

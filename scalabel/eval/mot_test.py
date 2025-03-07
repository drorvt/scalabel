"""Test cases for mot.py."""
import os
import unittest

import numpy as np

from ..label.io import group_and_sort, load, load_label_config
from ..unittest.util import get_test_file
from .mot import acc_single_video_mot, evaluate_track


class TestBDD100KMotEval(unittest.TestCase):
    """Test cases for BDD100K MOT evaluation."""

    cur_dir = os.path.dirname(os.path.abspath(__file__))
    gts = group_and_sort(
        load("{}/testcases/track_sample_anns.json".format(cur_dir)).frames
    )
    preds = group_and_sort(
        load("{}/testcases/track_predictions.json".format(cur_dir)).frames
    )
    config = load_label_config(get_test_file("box_track_configs.toml"))
    result = evaluate_track(acc_single_video_mot, gts, preds, config)

    def test_frame(self) -> None:
        """Test case for the function frame()."""
        data_frame = self.result.pd_frame()
        categories = set(
            [
                "human",
                "vehicle",
                "bike",
                "pedestrian",
                "rider",
                "car",
                "truck",
                "bus",
                "train",
                "motorcycle",
                "bicycle",
                "AVERAGE",
                "OVERALL",
            ]
        )
        self.assertSetEqual(categories, set(data_frame.index.values))

        data_arr = data_frame.to_numpy()
        MOTAs = np.array(  # pylint: disable=invalid-name
            [
                36.12565445,
                43.69747899,
                71.27987664,
                47.69230769,
                0.0,
                -1.0,
                -4.20168067,
                -1.0,
                39.03225806,
                70.14925373,
                -4.20168067,
                24.32420464,
                64.20070762,
            ]
        )
        self.assertTrue(
            np.isclose(np.nan_to_num(data_arr[:, 0], nan=-1.0), MOTAs).all()
        )

        overall_scores = np.array(
            [
                64.20070762,
                87.16143945,
                71.01073676,
                126.0,
                942.0,
                45.0,
                62.0,
                47.0,
                33.0,
                66.0,
            ]
        )
        self.assertTrue(np.isclose(data_arr[-1], overall_scores).all())

    def test_summary(self) -> None:
        """Check evaluation scores' correctness."""
        summary = self.result.summary()
        overall_reference = {
            "IDF1": 71.01073676416142,
            "MOTA": 64.20070762302991,
            "MOTP": 87.16143945073146,
            "FP": 126,
            "FN": 942,
            "IDSw": 45,
            "MT": 62,
            "PT": 47,
            "ML": 33,
            "FM": 66,
            "mIDF1": 32.24781943655838,
            "mMOTA": 24.324204637536685,
            "mMOTP": 50.01285067174096,
        }
        self.assertSetEqual(set(summary.keys()), set(overall_reference.keys()))
        for name, score in overall_reference.items():
            self.assertAlmostEqual(score, summary[name])

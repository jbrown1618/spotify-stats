import unittest
from unittest.mock import patch, sentinel

import pandas as pd

from data.repository import DataRepository
from routes.recommendations import percentile_range_recommendations_payload


class TrackRecommendationsTests(unittest.TestCase):
    def test_filtered_recommendations_do_not_require_sixty_tracks(self):
        for count in (1, 5, 59, 60):
            with self.subTest(count=count):
                filters = {"artists": ["spotify:artist:demo"]}
                tracks = pd.DataFrame(
                    {"track_uri": [f"spotify:track:demo-{i}" for i in range(count)]}
                )
                with (
                    patch("data.repository.filtered_connection") as connection,
                    patch.object(
                        DataRepository, "_read_dataframe_on", return_value=tracks
                    ) as read,
                    patch("routes.recommendations.repository", DataRepository()),
                ):
                    connection.return_value.__enter__.return_value = (
                        sentinel.connection,
                        {},
                    )
                    result = percentile_range_recommendations_payload(filters, 0.9, 1)

                self.assertEqual(result["total"], count)
                self.assertEqual(result["items"], tracks.to_dict(orient="records"))
                connection.assert_called_once_with(filters)
                read.assert_called_once_with(
                    sentinel.connection,
                    "select_track_recommendations_percentile_range",
                    {
                        "low_percentile": 0.9,
                        "high_percentile": 1,
                        "filter_tracks": True,
                    },
                )

    def test_unfiltered_recommendations_keep_global_population(self):
        with (
            patch("data.repository.filtered_connection") as connection,
            patch.object(
                DataRepository, "_read_dataframe_on", return_value=pd.DataFrame()
            ) as read,
        ):
            connection.return_value.__enter__.return_value = (sentinel.connection, {})
            DataRepository().track_recommendations({}, 0.9, 1)

        self.assertFalse(read.call_args.args[2]["filter_tracks"])

    def test_empty_recommendations_return_empty_page(self):
        with patch(
            "routes.recommendations.repository.track_recommendations",
            return_value=pd.DataFrame(),
        ):
            self.assertEqual(
                percentile_range_recommendations_payload(
                    {"artists": ["spotify:artist:missing"]}, 0.9, 1
                ),
                {"items": [], "total": 0},
            )

    def test_small_result_keeps_pagination_and_reversed_range(self):
        tracks = pd.DataFrame({"track_uri": ["first", "second", "third"]})
        filters = {"artists": ["spotify:artist:demo"], "limit": 1, "offset": 1}
        with patch(
            "routes.recommendations.repository.track_recommendations",
            return_value=tracks,
        ) as recommend:
            result = percentile_range_recommendations_payload(filters, 1, 0.9)

        recommend.assert_called_once_with(filters, 0.9, 1)
        self.assertEqual(result, {"items": [{"track_uri": "second"}], "total": 3})


if __name__ == "__main__":
    unittest.main()

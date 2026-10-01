import unittest
from pathlib import Path

from fusion_lab.music_dna.corpus import load_corpus, summarize_corpus


DATA = Path(__file__).resolve().parents[1] / 'data' / 'music_dna' / 'corpus.json'


class CorpusSummaryTests(unittest.TestCase):
    def test_summary_uses_five_observations_per_genre(self):
        summaries = summarize_corpus(load_corpus(DATA))
        self.assertEqual(set(summaries), {'thrash','black_metal','death_metal','doom_metal','punk','glam_metal','progressive_metal'})
        self.assertTrue(all(summary.observation_count == 5 for summary in summaries.values()))

    def test_summary_recovers_distinguishing_genre_shapes(self):
        summaries = summarize_corpus(load_corpus(DATA))
        thrash = summaries['thrash']
        black = summaries['black_metal']
        doom = summaries['doom_metal']
        self.assertGreater(thrash.medians['palm_mute_ratio'], black.medians['palm_mute_ratio'])
        self.assertGreater(black.medians['tremolo_ratio'], thrash.medians['tremolo_ratio'])
        self.assertLess(doom.medians['attack_density'], thrash.medians['attack_density'])

    def test_summary_is_deterministic(self):
        corpus = load_corpus(DATA)
        self.assertEqual(
            {k: v.to_dict() for k, v in summarize_corpus(corpus).items()},
            {k: v.to_dict() for k, v in summarize_corpus(corpus).items()},
        )


if __name__ == '__main__':
    unittest.main()

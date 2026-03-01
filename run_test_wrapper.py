import unittest
import sys

# Add tests directory
with open('test_result.txt', 'w', encoding='utf-8') as f:
    runner = unittest.TextTestRunner(stream=f, verbosity=2)
    suite = unittest.defaultTestLoader.discover('tests', pattern='test_mode_prompts.py')
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())

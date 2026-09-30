"""Regression checks for the notebook; no microscope or Blender required."""
import ast
from contextlib import redirect_stdout
import csv
import io
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / 'notebooks/BrownianMotionAnalysis.ipynb'

def sources():
    return [''.join(c['source']) for c in json.loads(NOTEBOOK.read_text(encoding='utf-8'))['cells'] if c['cell_type']=='code']

def helpers():
    scope = {'np': np, 'math': math, 'csv': csv, 'Path': Path, 'PIXELS_PER_UM':11.66, 'FPS':15.0}
    for source in sources():
        for node in ast.parse(source).body:
            if isinstance(node, ast.FunctionDef):
                exec(compile(ast.Module(body=[node], type_ignores=[]), str(NOTEBOOK), 'exec'), scope)
    return scope

class AnalysisTests(unittest.TestCase):
    def test_speed_conversion(self):
        speed = helpers()['calculate_speed'](np.array([[0.,0.],[3.,4.],[6.,8.]]))
        np.testing.assert_allclose(speed,[0.,75e-6,75e-6])

    def test_stationary_particle_speed(self):
        np.testing.assert_array_equal(helpers()['calculate_speed'](np.ones((3,2))),[0.,0.,0.])

    def test_displacement_averaging(self):
        h=helpers()
        a=np.array([[0.,0.],[1.,0.],[2.,0.]])
        np.testing.assert_allclose(h['calculate_average_displacement']([a,a]),[1.,2.5])

    def test_fit_keeps_intercept_and_correct_time_origin(self):
        source=next(s for s in sources() if 'predicted_values' in s and 'average_displacement_1um' in s and 'r_squared =' in s)
        x=np.arange(1,11)/15
        scope={'np':np,'plt':MagicMock(),'FPS':15.,'average_displacement_1um':3*x+7}
        exec(source,scope)
        np.testing.assert_allclose(scope['x_values'],x)
        np.testing.assert_allclose(scope['predicted_values'],3*x+7)
        self.assertAlmostEqual(scope['r_squared'],1.)

    def test_csv_calibration_and_frame_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'track.csv'
            path.write_text('frame;x;y\n936;11.66;23.32\n937;23.32;34.98\n')
            np.testing.assert_allclose(helpers()['csv_to_matrix'](path),[[1.,2.],[2.,3.]])
            path.write_text('frame;x;y\n1;0;0\n3;1;1\n')
            with self.assertRaisesRegex(ValueError,'consecutive'):
                helpers()['csv_to_matrix'](path)

    def test_run_all_from_root_and_notebooks(self):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        previous=Path.cwd()
        try:
            for directory in [ROOT,ROOT/'notebooks']:
                with self.subTest(directory=str(directory)):
                    os.chdir(directory)
                    scope={}
                    capture=io.StringIO()
                    with redirect_stdout(capture):
                        for source in sources():
                            exec(compile(source,str(NOTEBOOK),'exec'),scope)
                            plt.close('all')
                    self.assertIn('Skipping',capture.getvalue())
                    self.assertIsNone(scope['held_bead_coordinates'])
                    self.assertEqual(len(scope['average_displacement_1um']),1068)
                    self.assertEqual(len(scope['average_displacement_3um']),2178)
        finally:
            os.chdir(previous)

if __name__=='__main__':
    unittest.main()

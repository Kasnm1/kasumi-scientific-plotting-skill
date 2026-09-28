"""Portable roots for the packaged example renderers."""
import os
from pathlib import Path

SKILL_ROOT=Path(__file__).resolve().parents[2]
DATA_ROOT=Path(os.environ.get('FIGURE_DATA_ROOT',str(SKILL_ROOT/'assets'/'personal-examples'/'data')))
OUTPUT_ROOT=Path(os.environ.get('FIGURE_OUTPUT_ROOT',str(Path.cwd()/'outputs')))
OUTPUT_ROOT.mkdir(parents=True,exist_ok=True)
NATURE_SCRIPTS=SKILL_ROOT/'scripts'/'publication'

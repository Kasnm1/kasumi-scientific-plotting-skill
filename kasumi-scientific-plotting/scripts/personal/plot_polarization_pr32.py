"""Explicit model update: 254 nm total-current max/min ratio is 3.2."""
from pathlib import Path
from portable_paths import DATA_ROOT, OUTPUT_ROOT, NATURE_SCRIPTS

template = Path(__file__).with_name('plot_polarization_bars.py')
source = template.read_text(encoding='utf-8')
source = source.replace("OUT=OUTPUT_ROOT/'偏振角度光电流_254与324_模拟_360deg'",
                        "OUT=OUTPUT_ROOT/'偏振角度光电流_254nm_模拟_PR3.2'")
source = source.replace('ratios={254:2.5,324:1.05}', 'ratios={254:3.2,324:1.05}')
source = source.replace('for wl in (254,324):', 'for wl in (254,):')
source = source.replace('Nominal TOTAL-current ratios 254:2.5, 324:1.05; 90 deg maximum.',
                        '254 nm TOTAL-current ratio 3.2; maxima near 90 and 270 degrees.')
source = source.replace('No exact noisy ratio constraint.',
                        'Noisy model affinely rescaled to exact max/min=3.2, max anchored to IV.')
source = source.replace('    assert len(y)==25 and np.all(y>dark)',
    '    y = minimum + (y-y.min())/(y.max()-y.min())*(peak-minimum)\n'
    '    assert abs(y.max()/y.min()-3.2)<1e-12\n'
    '    assert len(y)==25 and np.all(y>dark)')
source = source.replace('Origin_双波长合并.txt', 'Origin_254nm_PR3.2.txt')
source = source.replace('Angle_deg\\t254nm_nA\\t324nm_nA', 'Angle_deg\\t254nm_nA')
exec(compile(source, str(template), 'exec'), {'__name__':'__main__', '__file__':str(template)})

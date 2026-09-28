"""Polarization model bars, not measured angular scans."""
import json
from pathlib import Path
from portable_paths import DATA_ROOT, OUTPUT_ROOT, NATURE_SCRIPTS
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).parent
OUT=OUTPUT_ROOT/'偏振角度光电流_254与324_模拟_360deg'
OUT.mkdir(exist_ok=True)
ROOT=(DATA_ROOT/'电学模拟数据_20260918/04_变光强IV_3V')
angles=np.arange(0,361,15)
colors={254:'#8A80DB',324:'#E797B9'}
ratios={254:2.5,324:1.05}
mpl.rcParams.update({'font.family':'Arial','font.size':40,'axes.linewidth':3,
 'xtick.major.width':3,'ytick.major.width':3,'xtick.major.size':8,'ytick.major.size':8,
 'pdf.fonttype':42,'svg.fonttype':'none'})
report={'type':'SIMULATED_REHEARSAL_NOT_MEASURED','conditions':'3 V; 66 uW/cm2',
 'assumptions':'IV light anchors interpreted as angular maxima; not measured calibration. '
 'Nominal TOTAL-current ratios 254:2.5, 324:1.05; 90 deg maximum. '
 'sin^2 envelope with independent uniform +/-0.8% NET-current modulation and 2 pA Gaussian noise. '
 'No exact noisy ratio constraint. Bars are amplitudes, not pulse time traces.', 'curves':[]}
series=[]
for wl in (254,324):
    path=ROOT/f'变光强IV--{wl}nm_8至350uWcm2_负5至正5V-1.txt'
    cols=path.read_text(encoding='utf-8-sig').splitlines()[0].split()
    table=np.loadtxt(path,skiprows=1)
    row=table[np.isclose(table[:,0],3)][0]
    dark,peak=row[cols.index('Dark')],row[cols.index('66')]
    minimum=peak/ratios[wl]
    ideal=minimum+(peak-minimum)*np.sin(np.deg2rad(angles))**2
    rng=np.random.default_rng(2026092100+wl)
    variation=rng.uniform(-.008,.008,len(angles))
    y=dark+(ideal-dark)*(1+variation)+rng.normal(0,2e-12,len(angles))
    assert len(y)==25 and np.all(y>dark)
    folder=OUT/f'{wl}nm'
    folder.mkdir(exist_ok=True)
    prefix=folder/f'偏振角度光电流--{wl}nm_3V_66uWcm2_0-360deg-1'
    np.savetxt(str(prefix)+'.txt',np.column_stack((angles,y)),fmt=['%d','%.12E'],delimiter='\t',
     header='SIMULATED_REHEARSAL; NOT MEASURED\nAngle_deg\tCurrent_A')
    np.savetxt(folder/'Origin_nA.txt',np.column_stack((angles,y*1e9)),fmt=['%d','%.10f'],delimiter='\t',
     header='SIMULATED_REHEARSAL; NOT MEASURED\nAngle_deg\tCurrent_nA')
    series.append(y*1e9)
    fig=plt.figure(figsize=(30/2.54,30/2.54),facecolor='white')
    ax=fig.add_axes([6/30,7/30,20/30,16/30])
    ax.bar(angles,y*1e9,width=9,color=colors[wl],edgecolor=colors[wl],linewidth=.5)
    upper=5.9 if wl==254 else 11.5
    ax.set(xlim=(-9,369),ylim=(0,upper),xticks=np.arange(0,361,60))
    ax.set_yticks([0,1,2,3,4,5] if wl==254 else [0,2,4,6,8,10])
    ax.set_xticks(angles,minor=True)
    ax.tick_params(direction='in',top=False,right=False,pad=12)
    ax.tick_params(which='minor',direction='in',length=4,width=2)
    ax.text(.5,.97,f'{wl} nm',transform=ax.transAxes,ha='center',va='top',fontsize=30)
    ax.text(1,1.025,'@3 V  66 '+chr(956)+'W/cm'+chr(178),transform=ax.transAxes,
     ha='right',va='bottom',fontsize=30)
    fig.text(16/30,3.8/30,'Polarization angle ('+chr(176)+')',ha='center',va='center',fontsize=40)
    fig.text(1.2/30,15/30,'Photocurrent (nA)',ha='center',va='center',rotation=90,
     rotation_mode='anchor',fontsize=40)
    fig.savefig(str(prefix)+'.pdf')
    fig.savefig(str(prefix)+'.svg')
    fig.savefig(str(prefix)+'.tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'})
    fig.savefig(str(prefix)+'_preview.png',dpi=300)
    plt.close(fig)
    report['curves'].append(dict(wavelength_nm=wl,nominal_ratio=ratios[wl],
     noisy_ratio=float(y.max()/y.min()),max_angle_deg=int(angles[y.argmax()]),
     IV_peak_A=float(peak),current_A=y.tolist(),variation=variation.tolist()))
np.savetxt(OUT/'Origin_双波长合并.txt',np.column_stack((angles,*series)),delimiter='\t',fmt='%.10g',
 header='SIMULATED_REHEARSAL; NOT MEASURED\nAngle_deg\t254nm_nA\t324nm_nA')
(OUT/'参数与来源.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print([(r['wavelength_nm'],r['noisy_ratio'],r['max_angle_deg']) for r in report['curves']])

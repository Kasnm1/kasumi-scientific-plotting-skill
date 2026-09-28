"""Single finite-pulse model; rise/fall labels are model-derived, not measured."""
import ast
import json
from pathlib import Path
from portable_paths import DATA_ROOT, OUTPUT_ROOT, NATURE_SCRIPTS
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).parent
OUT=OUTPUT_ROOT/'RiseFall_254nm_3V_模拟'
OUT.mkdir(exist_ok=True)
PREFIX=OUT/'RiseFall--254nm_66uWcm2_3V_3ms脉冲-1'
TAIL,TAU_TAIL=8e-12,.0018
tree=ast.parse((HERE/'plot_wavelength_it.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'response_definitions','exec'))
src=(DATA_ROOT/'电学模拟数据_20260918/04_变光强IV_3V/变光强IV--254nm_8至350uWcm2_负5至正5V-1.txt')
cols=src.read_text(encoding='utf-8-sig').splitlines()[0].split()
iv=np.loadtxt(src,skiprows=1)
row=iv[np.isclose(iv[:,0],3)][0]
dark,light=row[cols.index('Dark')],row[cols.index('66')]
delta=light-dark
lo,hi=.0001,.001
for _ in range(60):
    mid=(lo+hi)/2
    duration=crossing(.1,delta,mid)-crossing(.9,delta,mid)
    if duration>.000811:
        hi=mid
    else:
        lo=mid
tau=(lo+hi)/2
width=.003
tau_tail_fall=TAU_TAIL*1.05
# Preserve component amplitudes at turn-off while allowing asymmetric kinetics.
af=(delta-TAIL)*(-np.expm1(-width/tau))
at=TAIL*(-np.expm1(-width/TAU_TAIL))
rise10=crossing(.9,delta,tau)
rise90=crossing(.1,delta,tau)
def fall_cross(f, tau_fall):
    lo,hi=0.,.02
    for _ in range(65):
        mid=(lo+hi)/2
        if af*np.exp(-mid/tau_fall)+at*np.exp(-mid/tau_tail_fall)>f*delta:
            lo=mid
        else:
            hi=mid
    return width+(lo+hi)/2
lo,hi=.0001,.001
for _ in range(60):
    mid=(lo+hi)/2
    if fall_cross(.1,mid)-fall_cross(.9,mid)>.000897:
        hi=mid
    else:
        lo=mid
tau_fall=(lo+hi)/2
fall90,fall10=fall_cross(.9,tau_fall),fall_cross(.1,tau_fall)
end=.0041
t=np.arange(-30,411)*1e-5
signal=np.zeros_like(t)
on=(t>=0)&(t<width)
signal[on]=delta-remaining(t[on],delta,tau)
off=t>=width
age=t[off]-width
signal[off]=af*np.exp(-age/tau_fall)+at*np.exp(-age/tau_tail_fall)
fraction=np.clip(signal/delta,0,1)
rng=np.random.default_rng(202609210254)
# Sparse fine ripple: knots are 0.04 ms apart, then linearly connected.
# The illuminated fluctuation is kept within +/-0.5% of the signal.
knot_step=4
knot_index=np.arange(0,len(t),knot_step)
if knot_index[-1] != len(t)-1:
    knot_index=np.append(knot_index,len(t)-1)
knot_noise=np.clip(rng.normal(0,.0022,size=len(knot_index)),-.005,.005)
ripple=np.interp(np.arange(len(t)),knot_index,knot_noise)
dark_noise=rng.normal(0,.5e-12,size=len(t))
noise=signal*ripple+dark_noise
current=dark+signal+noise
tr,tf=(rise90-rise10)*1e6,(fall10-fall90)*1e6
assert abs(tr-811)<.01 and abs(tf-897)<.01
np.savetxt(OUT/'Origin_RiseFall.txt',np.column_stack((t*1e3,current,(current-dark)/delta,signal/delta)),
 delimiter='\t',fmt='%.12g',header='SIMULATED_REHEARSAL; NOT MEASURED\nSingle 3 ms pulse; rise 811 us; fall 897 us; sampling 10 us plus exact recovery endpoint\nTime_ms\tCurrent_A\tNormalized_current\tNoiseless_normalized_current')
mpl.rcParams.update({'font.family':'Arial','font.size':40,'axes.linewidth':3,
 'xtick.major.width':3,'ytick.major.width':3,'xtick.major.size':8,'ytick.major.size':8,
 'svg.fonttype':'none','pdf.fonttype':42})
fig=plt.figure(figsize=(30/2.54,30/2.54),facecolor='white')
ax=fig.add_axes([6/30,7/30,20/30,16/30])
for a,b in ((rise10,rise90),(fall90,fall10)):
    ax.axvspan(a*1e3,b*1e3,facecolor='#D8C7E3',alpha=.62,zorder=0)
ax.axhline(.1,color='#444444',linestyle='--',linewidth=1.6)
ax.axhline(.9,color='#444444',linestyle='--',linewidth=1.6)
ax.plot(t*1e3,(current-dark)/delta,color='#8A80DB',linewidth=3,label='254 nm',zorder=3)
ax.set(xlim=(t[0]*1e3,end*1e3),ylim=(-.04,1.15),xticks=[0,1,2,3,4],yticks=[])
ax.tick_params(axis='y',which='both',left=False,right=False,labelleft=False)
ax.tick_params(direction='in',top=False,right=False,pad=12)
ax.legend(loc='upper right',frameon=False,fontsize=30,handlelength=1.5)
ax.text(1.2,.53,f'Rise\n{tr:.0f} '+chr(956)+'s',fontsize=30,ha='left',va='center')
ax.text(3.08,.53,f'Fall\n{tf:.0f} '+chr(956)+'s',fontsize=30,ha='left',va='center')
ax.text(1,1.025,'@3 V  66 '+chr(956)+'W/cm'+chr(178),transform=ax.transAxes,ha='right',va='bottom',fontsize=30)
fig.text(16/30,3.8/30,'Time (ms)',ha='center',va='center',fontsize=40)
fig.savefig(str(PREFIX)+'.pdf')
fig.savefig(str(PREFIX)+'.svg')
fig.savefig(str(PREFIX)+'.tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'})
fig.savefig(str(PREFIX)+'_preview.png',dpi=300)
plt.close(fig)
report=dict(type='SIMULATED_REHEARSAL_NOT_MEASURED',dark_A=dark,light_A=light,
 rise_us=tr,fall_us=tf,thresholds='10-90% of steady net response; noiseless model crossings',
 pulse_width_s=width,tail_step_amplitude_A=TAIL,rise_tail_tau_s=TAU_TAIL,fall_tail_tau_s=tau_tail_fall,
 rise_fast_tau_s=tau,fall_fast_tau_s=tau_fall,end_s=end,
 finite_pulse_tail_at_turnoff_A=at,sampling_s=1e-5,
 noise_model='0.04 ms correlated knots; light ripple sigma 0.22%, clipped to +/-0.5%; dark white noise 0.5 pA RMS',
 normalization='(I-Idark)/(Ilight-Idark)',view='Hard stop at 4.1 ms; no additional dark plateau')
(OUT/'参数与校验.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))

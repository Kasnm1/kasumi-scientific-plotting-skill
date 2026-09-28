"""Generate explicitly simulated I-t data anchored to the current I-V tables."""
from pathlib import Path
from portable_paths import DATA_ROOT, OUTPUT_ROOT, NATURE_SCRIPTS
import json
import hashlib
import sys
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch, Rectangle
from matplotlib.legend_handler import HandlerBase

ROOT = DATA_ROOT
IV = ROOT / '电学模拟数据_20260918/04_变光强IV_3V'
OUT = OUTPUT_ROOT / '变波长IT_最新IV_模拟_周期波动2pct'
OUT.mkdir(exist_ok=True)
PREFIX = OUT / '变波长IT--254与324nm_66uWcm2_3V_0.05Hz-1'
TAIL = 8e-12
TAU_TAIL = 0.0018
SD, SL = 0.5e-12, 2e-12
SKILLS = NATURE_SCRIPTS
sys.path.insert(0, str(SKILLS))
from audit_panel_alignment import require_matplotlib_panel_alignment


def remaining(t, delta, tau):
    return (delta - TAIL)*np.exp(-t/tau) + TAIL*np.exp(-t/TAU_TAIL)


def crossing(fraction, delta, tau):
    lo, hi = 0., .05
    for _ in range(60):
        mid = (lo + hi)/2
        if remaining(mid, delta, tau)/delta > fraction:
            lo = mid
        else:
            hi = mid
    return (lo + hi)/2


def calibrate(delta):
    lo, hi = .0001, .001
    for _ in range(60):
        mid = (lo + hi)/2
        dt = crossing(.1, delta, mid) - crossing(.9, delta, mid)
        if dt > .0008:
            hi = mid
        else:
            lo = mid
    return (lo + hi)/2


ticks = set(range(0, 20010001, 10000))
for edge in range(10, 201, 10):
    ticks.update(range(edge*100000 - 200, edge*100000 + 1201))
t = np.array(sorted(ticks))/100000
curves, report = {}, {}
for wl in (254, 324):
    src = IV / f'变光强IV--{wl}nm_8至350uWcm2_负5至正5V-1.txt'
    cols = src.read_text(encoding='utf-8-sig').splitlines()[0].split()
    iv = np.loadtxt(src, skiprows=1)
    anchor = iv[np.isclose(iv[:, 0], 3)][0]
    dark, light = anchor[cols.index('Dark')], anchor[cols.index('66')]
    delta = light-dark
    tau = calibrate(delta)
    cycle_rng = np.random.default_rng(2026091900+wl)
    cycle_factors = cycle_rng.uniform(.98, 1.02, 10)
    cycle_deltas = delta*cycle_factors
    cycle_taus = np.array([calibrate(d) for d in cycle_deltas])
    cycle_durations = np.array([crossing(.1,d,tt)-crossing(.9,d,tt)
                               for d,tt in zip(cycle_deltas,cycle_taus)])
    assert np.all(np.abs(cycle_durations-.0008) < 1e-10)
    assert np.all(np.abs(cycle_factors-1) <= .02)
    half = np.floor(t/10).astype(int)
    age = t-half*10
    # Falling edges retain the amplitude of the preceding light pulse.
    cycle_index = np.clip((half-1)//2, 0, 9)
    local_delta = cycle_deltas[cycle_index]
    rem = remaining(age, local_delta, cycle_taus[cycle_index])
    base = np.where(half % 2, dark+local_delta-rem, dark+rem)
    base[t < 10] = dark
    fraction = np.clip((base-dark)/local_delta, 0, 1)
    rng = np.random.default_rng(2026091800+wl)
    noise = rng.normal(size=len(t))*(SD+(SL-SD)*fraction)
    y = base+noise
    steady = age > .02
    dm, lm = steady & (half % 2 == 0), steady & (half % 2 == 1)
    duration = crossing(.1, delta, tau)-crossing(.9, delta, tau)
    assert abs(duration-.0008) < 1e-10
    assert np.all(np.diff(t) > 0) and np.all(np.diff(y) != 0)
    file = OUT / f'变波长IT--{wl}nm_66uWcm2_3V_0.05Hz-1.txt'
    np.savetxt(file, np.column_stack((t,y)), fmt=['%.8f','%.12E'], delimiter='\t',
               header='SIMULATED_REHEARSAL; NOT MEASURED\n3 V; 66 uW/cm2; 0.05 Hz; 10 cycles; dark first\nCycle net-current factors uniform in [0.98,1.02]; independent per wavelength\ntime_s\tcurrent_A')
    curves[wl] = y*1e9
    report[wl] = dict(source=str(src), source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
                      dark_A=float(dark), light_A=float(light), on_off=float(light/dark),
                      tau_fast_s=tau, rise_10_90_s=duration, fall_90_10_s=duration,
                      tail_A=TAIL, tail_tau_s=TAU_TAIL,
                      cycle_net_factors=cycle_factors.tolist(),
                      cycle_plateau_A=(dark+cycle_deltas).tolist(),
                      cycle_tau_fast_s=cycle_taus.tolist(),
                      cycle_rise_fall_s=cycle_durations.tolist(),
                      dark_rms_pA=float(np.sqrt(np.mean(noise[dm]**2))*1e12),
                      light_rms_pA=float(np.sqrt(np.mean(noise[lm]**2))*1e12),
                      recovery_to_dark_sigma_s=crossing(SD/delta,delta,tau), points=len(t))

np.savetxt(OUT/'Origin_合并数据.txt', np.column_stack((t, curves[254], curves[324])),
           delimiter='\t', fmt='%.12g', header='SIMULATED_REHEARSAL; NOT MEASURED\nTime_s\t254nm_nA\t324nm_nA')

mpl.rcParams.update({'font.family':'Arial','font.size':40,'axes.linewidth':3,
    'lines.linewidth':3,'xtick.major.width':3,'ytick.major.width':3,
    'xtick.major.size':8,'ytick.major.size':8,'svg.fonttype':'none','pdf.fonttype':42})
fig = plt.figure(figsize=(30/2.54,30/2.54), facecolor='white')
ax = fig.add_axes([6/30,7/30,20/30,16/30])
colors = {254:'#8A80DB',324:'#E797B9'}

# Disjoint fill bands keep the lower trace's hue from mixing with the upper one.
for wl in (324,254):
    y = curves[wl]
    bottom = curves[254] if wl == 324 else np.zeros_like(t)
    clip = ax.fill_between(t,bottom,y,color='none',linewidth=0)
    rgba = np.zeros((256,1,4))
    rgba[:,:,:3] = to_rgb(colors[wl])
    rgba[:,:,3] = np.linspace(.025,.35,256)[:,None]
    im = ax.imshow(rgba,extent=[t[0],t[-1],0,float(y.max())],
                   origin='lower',aspect='auto',interpolation='bicubic',zorder=1)
    im.set_clip_path(clip.get_paths()[0],ax.transData)
for wl in (324,254):
    ax.plot(t,curves[wl],color=colors[wl],zorder=3)


class GradientLegend(HandlerBase):
    def create_artists(self, legend, orig_handle, xd, yd, w, h, fs, trans):
        rgb = orig_handle.get_edgecolor()[:3]
        artists=[]
        for i in range(24):
            artists.append(Rectangle((-xd,-yd+h*i/24),w,h/24,
                transform=trans,facecolor=(*rgb,.025+.325*i/23),edgecolor='none'))
        artists.append(Rectangle((-xd,-yd),w,h,transform=trans,
                                 facecolor='none',edgecolor=rgb,linewidth=1.5))
        return artists


ax.set_xlim(0,109)
ax.set_ylim(-.15,11.8)
ax.set_xticks([0,20,40,60,80,100])
ax.set_yticks([0,2,4,6,8,10])
ax.tick_params(direction='in',top=False,right=False,pad=12)
legend=ax.legend(handles=[Patch(edgecolor=colors[w],facecolor='none',label=f'{w} nm') for w in (254,324)],
    loc='upper center',bbox_to_anchor=(.5,.982),ncol=2,fontsize=30,frameon=False,
    handlelength=1.7,handleheight=.8,columnspacing=1.6,handletextpad=.35,
    handler_map={Patch:GradientLegend()},borderaxespad=0)
condition=ax.text(1,1.025,'@3 V  0.05 Hz  66 '+chr(956)+'W/cm'+chr(178),
                  transform=ax.transAxes,ha='right',va='bottom',fontsize=30)
fig.text(16/30,3.8/30,'Time (s)',ha='center',va='center',fontsize=40)
fig.text(1.2/30,15/30,'Current (nA)',ha='center',va='center',rotation=90,
         rotation_mode='anchor',fontsize=40)
fig.canvas.draw()
renderer=fig.canvas.get_renderer()
legend_box=legend.get_window_extent(renderer)
peak_pixel=ax.transData.transform((0,max(v.max() for v in curves.values())))[1]
assert legend_box.y0-peak_pixel > 15
require_matplotlib_panel_alignment(fig,json_out=str(PREFIX)+'.alignment.json',strict=True)
fig.savefig(str(PREFIX)+'.pdf')
fig.savefig(str(PREFIX)+'.svg')
fig.savefig(str(PREFIX)+'.tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'})
fig.savefig(str(PREFIX)+'_preview.png',dpi=300)
plt.close(fig)
report['notes'] = ['SIMULATED_REHEARSAL; NOT MEASURED',
    'Latest signed IV +3 V, 66 uW/cm2 anchors. No experimental data changed.',
    'Independent Gaussian noise: dark 0.5 pA, light 2 pA RMS; assumed, not measured.',
    'No instrument bandwidth or noise PSD is inferred. No drift was added.',
    'Adaptive grid: plateaus 0.1 s; edges -2 to +12 ms sampled at 10 us.',
    '10 cycles retained in TXT; plot window 0-109 s shows first 5 cycles and dark recovery. A to nA conversion only.',
    'Each cycle net photocurrent uses an independent uniform factor in [0.98,1.02]; not 2% pointwise noise or SD.',
    'Gradient fills show current, not confidence intervals; no simulated replicates implied.',
    'Upper fill starts at lower trace to preserve color separation.',
    '800 us refers to noiseless 10-90%/90-10% model transitions.']
(OUT/'参数与校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))

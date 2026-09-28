"""254 nm simulated frequency series; physical edge times stay fixed."""
import ast
import json
from pathlib import Path
from portable_paths import DATA_ROOT, OUTPUT_ROOT, NATURE_SCRIPTS
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch, Rectangle
from matplotlib.legend_handler import HandlerBase

HERE=Path(__file__).parent
OUT=OUTPUT_ROOT/'变频率IT_254nm_模拟'
OUT.mkdir(exist_ok=True)
TAIL,TAU_TAIL=8e-12,.0018
SD,SL=.5e-12,2e-12
tree=ast.parse((HERE/'plot_wavelength_it.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))],type_ignores=[]),'shared_it','exec'))
src=(DATA_ROOT/'电学模拟数据_20260918/04_变光强IV_3V/变光强IV--254nm_8至350uWcm2_负5至正5V-1.txt')
cols=src.read_text(encoding='utf-8-sig').splitlines()[0].split()
iv=np.loadtxt(src,skiprows=1)
row=iv[np.isclose(iv[:,0],3)][0]
dark,light=row[cols.index('Dark')],row[cols.index('66')]
mpl.rcParams.update({'font.family':'Arial','font.size':40,'axes.linewidth':3,
 'lines.linewidth':3,'xtick.major.width':3,'ytick.major.width':3,
 'xtick.major.size':8,'ytick.major.size':8,'svg.fonttype':'none','pdf.fonttype':42})
report={'type':'SIMULATED_REHEARSAL_NOT_MEASURED','source':str(src),
 'dark_A':float(dark),'light_A':float(light),'voltage_V':3,'power_uW_cm2':66,
 'tail_A':TAIL,'tail_tau_s':TAU_TAIL,'noise_rms_A':[SD,SL],
 'notes':'10 cycles saved; first five displayed. 50% duty, dark first. '
 'All frequencies assume 800 us 10-90/90-10 response; no measured frequency dependence. '
 'Adaptive sampling: at most period/200 or 0.1 s on plateaus; 10 us at edges. '
 'Cycle amplitudes uniform within +/-0.8%; not pointwise 0.8% noise.', 'frequencies':[]}
for f in (.1,.5,1.):
    period=1/f
    half_ticks=round(period/2*100000)
    end=20*half_ticks+1200
    step=min(10000,round(period/200*100000))
    ticks=set(range(0,end+1,step))
    for k in range(1,21):
        ticks.update(range(k*half_ticks-200,k*half_ticks+1201))
    ticks=np.array(sorted(ticks))
    t=ticks/100000
    half=ticks//half_ticks
    age=(ticks%half_ticks)/100000
    ci=np.clip((half-1)//2,0,9)
    rng=np.random.default_rng(2026092000+round(f*100))
    factors=rng.uniform(.992,1.008,10)
    ds=(light-dark)*factors
    taus=np.array([calibrate(d) for d in ds])
    durations=np.array([crossing(.1,d,tau)-crossing(.9,d,tau) for d,tau in zip(ds,taus)])
    assert np.allclose(durations,.0008,atol=1e-10,rtol=0)
    rem=remaining(age,ds[ci],taus[ci])
    base=np.where(half%2,dark+ds[ci]-rem,dark+rem)
    base[half==0]=dark
    frac=np.clip((base-dark)/ds[ci],0,1)
    noise=rng.normal(size=len(t))*(SD+(SL-SD)*frac)
    y=base+noise
    assert np.all(np.diff(t)>0) and np.all(np.diff(y)!=0)
    folder=OUT/f'{f:g}Hz'
    folder.mkdir(exist_ok=True)
    prefix=folder/f'变频率IT--254nm_66uWcm2_3V_{f:g}Hz-1'
    np.savetxt(str(prefix)+'.txt',np.column_stack((t,y)),delimiter='\t',fmt=['%.8f','%.12E'],
     header=f'SIMULATED_REHEARSAL; NOT MEASURED\n254 nm; 3 V; 66 uW/cm2; {f:g} Hz\ntime_s\tcurrent_A')
    np.savetxt(folder/'Origin_nA.txt',np.column_stack((t,y*1e9)),delimiter='\t',fmt='%.12g',
     header='SIMULATED_REHEARSAL; NOT MEASURED\nTime_s\tCurrent_nA')
    fig=plt.figure(figsize=(30/2.54,30/2.54),facecolor='white')
    ax=fig.add_axes([6/30,7/30,20/30,16/30])
    color='#8A80DB'
    clip=ax.fill_between(t,0,y*1e9,color='none',linewidth=0)
    rgba=np.zeros((256,1,4)); rgba[:,:,:3]=to_rgb(color)
    rgba[:,:,3]=np.linspace(.025,.35,256)[:,None]
    im=ax.imshow(rgba,extent=[t[0],t[-1],0,float(y.max()*1e9)],origin='lower',aspect='auto',zorder=1)
    im.set_clip_path(clip.get_paths()[0],ax.transData)
    ax.plot(t,y*1e9,color=color,zorder=3)
    ax.set(xlim=(0,5.45*period),ylim=(-.08,6.1),xticks=np.arange(6)*period,yticks=[0,1,2,3,4,5,6])
    ax.tick_params(direction='in',top=False,right=False,pad=12)
    leg=ax.legend(handles=[Patch(edgecolor=color,facecolor='none',label=f'{f:g} Hz')],
     loc='upper center',bbox_to_anchor=(.5,.98),fontsize=30,frameon=False,
     handlelength=1.6,handleheight=.8,handler_map={Patch:GradientLegend()},borderaxespad=0)
    ax.text(1,1.025,'@254 nm  3 V  66 '+chr(956)+'W/cm'+chr(178),transform=ax.transAxes,
     ha='right',va='bottom',fontsize=30)
    fig.text(16/30,3.8/30,'Time (s)',ha='center',va='center',fontsize=40)
    fig.text(1.2/30,15/30,'Current (nA)',ha='center',va='center',rotation=90,rotation_mode='anchor',fontsize=40)
    fig.canvas.draw()
    assert leg.get_window_extent(fig.canvas.get_renderer()).y0-ax.transData.transform((0,y.max()*1e9))[1]>15
    fig.savefig(str(prefix)+'.pdf')
    fig.savefig(str(prefix)+'.svg')
    fig.savefig(str(prefix)+'.tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'})
    fig.savefig(str(prefix)+'_preview.png',dpi=300)
    plt.close(fig)
    report['frequencies'].append(dict(frequency_Hz=f,display_end_s=5.45*period,points=len(t),
      cycle_factors=factors.tolist(),rise_fall_s=durations.tolist()))
(OUT/'参数与校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Generated 0.1, 0.5, 1 Hz; 3 V; 66 uW/cm2; all response and time-grid checks passed.')

"""Simulated bias-dependent I-t; reuse the established response and legend model."""
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
ROOT=DATA_ROOT
OUT=OUTPUT_ROOT/'变偏压IT_254与324_模拟'
OUT.mkdir(exist_ok=True)
TAIL,TAU_TAIL=8e-12,.0018
SD,SL=.5e-12,2e-12
# Load only pure definitions, without running the wavelength data generator.
tree=ast.parse((HERE/'plot_wavelength_it.py').read_text(encoding='utf-8'))
definitions=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
exec(compile(ast.Module(body=definitions,type_ignores=[]),'shared_it_definitions','exec'))
ticks=set(range(0,20010001,10000))
for edge in range(10,201,10):
    ticks.update(range(edge*100000-200,edge*100000+1201))
t=np.array(sorted(ticks))/100000
half=np.floor(t/10).astype(int)
age=t-half*10
ci=np.clip((half-1)//2,0,9)
mpl.rcParams.update({'font.family':'Arial','font.size':40,'axes.linewidth':3,
 'lines.linewidth':3,'xtick.major.width':3,'ytick.major.width':3,
 'xtick.major.size':8,'ytick.major.size':8,'svg.fonttype':'none','pdf.fonttype':42})
colors={1:'#81BFB1',3:'#E797B9',5:'#8A80DB'}
report={'type':'SIMULATED_REHEARSAL_NOT_MEASURED','conditions':
 '66 uW/cm2; 0.05 Hz; 10 cycles in TXT, first five shown at 0-109 s; '
 '800 us noiseless 10-90/90-10 times at all biases (assumption); '
 '8 pA tail, tau 1.8 ms; dark/light noise 0.5/2 pA RMS; independent +/-0.8% cycle factors.',
 'curves':[]}
for wl in (254,324):
    folder=OUT/f'{wl}nm'
    folder.mkdir(exist_ok=True)
    src=ROOT/'电学模拟数据_20260918/04_变光强IV_3V'/f'变光强IV--{wl}nm_8至350uWcm2_负5至正5V-1.txt'
    cols=src.read_text(encoding='utf-8-sig').splitlines()[0].split()
    iv=np.loadtxt(src,skiprows=1)
    curves={}
    for voltage in (1,3,5):
        row=iv[np.isclose(iv[:,0],voltage)][0]
        dark,light=row[cols.index('Dark')],row[cols.index('66')]
        delta=light-dark
        # Stable seeds preserve the cycle ordering when adjusting variation.
        offset=0 if voltage==3 else voltage*10000
        factors=np.random.default_rng(2026091900+wl+offset).uniform(.992,1.008,10)
        assert np.all(np.abs(factors-1) <= .008+1e-12)
        ds=delta*factors
        taus=np.array([calibrate(d) for d in ds])
        durations=np.array([crossing(.1,d,tau)-crossing(.9,d,tau) for d,tau in zip(ds,taus)])
        assert np.allclose(durations,.0008,rtol=0,atol=1e-10)
        rem=remaining(age,ds[ci],taus[ci])
        base=np.where(half%2,dark+ds[ci]-rem,dark+rem)
        base[t<10]=dark
        fraction=np.clip((base-dark)/ds[ci],0,1)
        noise=np.random.default_rng(2026091800+wl+offset).normal(size=len(t))*(SD+(SL-SD)*fraction)
        y=base+noise
        assert np.all(np.diff(t)>0) and np.all(np.diff(y)!=0)
        curves[voltage]=y*1e9
        np.savetxt(folder/f'变偏压IT--{wl}nm_66uWcm2_{voltage}V_0.05Hz-1.txt',
          np.column_stack((t,y)),delimiter='\t',fmt=['%.8f','%.12E'],
          header=f'SIMULATED_REHEARSAL; NOT MEASURED\n{wl} nm; {voltage} V; 66 uW/cm2; 0.05 Hz\ntime_s\tcurrent_A')
        report['curves'].append(dict(wavelength_nm=wl,voltage_V=voltage,
         source=str(src),dark_A=float(dark),light_A=float(light),cycle_factors=factors.tolist(),
         rise_fall_s=durations.tolist(),points=len(t)))
    np.savetxt(folder/'Origin_合并数据.txt',np.column_stack((t,*curves.values())),
     delimiter='\t',fmt='%.12g',header='SIMULATED_REHEARSAL; NOT MEASURED\nTime_s\t1V_nA\t3V_nA\t5V_nA')
    fig=plt.figure(figsize=(30/2.54,30/2.54),facecolor='white')
    ax=fig.add_axes([6/30,7/30,20/30,16/30])
    for v in (5,3,1):
        y=curves[v]
        bottom=curves[v-2] if v>1 else np.zeros_like(t)
        clip=ax.fill_between(t,bottom,y,color='none',linewidth=0)
        rgba=np.zeros((256,1,4)); rgba[:,:,:3]=to_rgb(colors[v])
        rgba[:,:,3]=np.linspace(.025,.35,256)[:,None]
        im=ax.imshow(rgba,extent=[t[0],t[-1],0,float(y.max())],origin='lower',aspect='auto',zorder=1)
        im.set_clip_path(clip.get_paths()[0],ax.transData)
    for v in (5,3,1):
        ax.plot(t,curves[v],color=colors[v],zorder=3)
    ymax=10.4 if wl==254 else 20.8
    ax.set(xlim=(0,109),ylim=(-ymax*.012,ymax),xticks=[0,20,40,60,80,100])
    ax.set_yticks([0,2,4,6,8,10] if wl==254 else [0,4,8,12,16,20])
    ax.tick_params(direction='in',top=False,right=False,pad=12)
    leg=ax.legend(handles=[Patch(edgecolor=colors[v],facecolor='none',label=f'{v} V') for v in (1,3,5)],
     loc='upper center',bbox_to_anchor=(.5,.98),ncol=3,fontsize=30,frameon=False,
     handlelength=1.6,handleheight=.8,handletextpad=.35,columnspacing=1.0,
     handler_map={Patch:GradientLegend()},borderaxespad=0)
    ax.text(1,1.025,f'@{wl} nm  0.05 Hz  66 '+chr(956)+'W/cm'+chr(178),
      transform=ax.transAxes,ha='right',va='bottom',fontsize=30)
    fig.text(16/30,3.8/30,'Time (s)',ha='center',va='center',fontsize=40)
    fig.text(1.2/30,15/30,'Current (nA)',ha='center',va='center',rotation=90,rotation_mode='anchor',fontsize=40)
    fig.canvas.draw()
    assert leg.get_window_extent(fig.canvas.get_renderer()).y0-ax.transData.transform((0,max(y.max() for y in curves.values())))[1]>15
    prefix=folder/f'变偏压IT--{wl}nm_1-3-5V_66uWcm2_0.05Hz-1'
    fig.savefig(str(prefix)+'.pdf')
    fig.savefig(str(prefix)+'.svg')
    fig.savefig(str(prefix)+'.tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'})
    fig.savefig(str(prefix)+'_preview.png',dpi=300)
    plt.close(fig)
(OUT/'参数与校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for r in report['curves']:
    print(r['wavelength_nm'],r['voltage_V'],r['light_A']*1e9)

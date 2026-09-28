"""Model spectrum anchored to latest IV; not a new spectral measurement."""
import json
from pathlib import Path
from portable_paths import DATA_ROOT, OUTPUT_ROOT, NATURE_SCRIPTS
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

ROOT=DATA_ROOT
OUT=OUTPUT_ROOT/'光电流光谱_3V_210_模型'
OUT.mkdir(exist_ok=True)
PREFIX=OUT/'光电流光谱--3V_210uWcm2-1'
source=ROOT/'guangxiangy_optimized.txt'
x,old=np.loadtxt(source,unpack=True)
assert np.all(np.diff(x)>0)
old_dark=7.25e-11
ivdir=ROOT/'电学模拟数据_20260918/04_变光强IV_3V'
anchors={}
for wl in (254,324):
    path=ivdir/f'变光强IV--{wl}nm_8至350uWcm2_负5至正5V-1.txt'
    columns=path.read_text(encoding='utf-8-sig').splitlines()[0].split()
    table=np.loadtxt(path,skiprows=1)
    row=table[np.isclose(table[:,0],3)][0]
    anchors[wl]=(float(row[columns.index('Dark')]),float(row[columns.index('210')]))
dark,peak=anchors[324]
net=old-old_dark
scale=(peak-dark)/np.interp(324,x,net)
current=dark+scale*net
# Smooth, compact short-wave correction; the main peak region >=290 nm
# retains one constant scale and its original wavelength coordinates.
target254=anchors[254][1]
correction=target254-np.interp(254,x,current)
u=np.clip((x-254)/(290-254),0,1)
weight=np.where(x<=254,net/np.interp(254,x,net),1-3*u*u+2*u*u*u)
current+=correction*weight
assert np.isclose(np.interp(254,x,current),target254,rtol=1e-10,atol=0)
assert np.isclose(np.interp(324,x,current),peak,rtol=1e-10,atol=0)
imax=int(np.argmax(current))
level=dark+(current[imax]-dark)/2
crossings=[]
for i in range(len(x)-1):
    if (current[i]-level)*(current[i+1]-level)<0:
        crossings.append(float(x[i]+(level-current[i])*(x[i+1]-x[i])/(current[i+1]-current[i])))
left=max(v for v in crossings if v<x[imax])
right=min(v for v in crossings if v>x[imax])
fwhm=right-left
np.savetxt(OUT/'Origin_光电流光谱.txt',np.column_stack((x,current*1e9)),
           delimiter='\t',fmt=['%.6f','%.10g'],
           header='MODEL_DERIVED; NOT MEASURED; 3 V; 210 uW/cm2\nWavelength_nm\tIlluminated_current_nA')
mpl.rcParams.update({'font.family':'Arial','font.size':40,'axes.linewidth':3,
    'xtick.major.width':3,'ytick.major.width':3,'xtick.major.size':8,'ytick.major.size':8,
    'pdf.fonttype':42,'svg.fonttype':'none'})
fig=plt.figure(figsize=(30/2.54,30/2.54),facecolor='white')
ax=fig.add_axes([6/30,7/30,20/30,16/30])
color='#9287E3'
# Layered circular markers retain a light centre and lavender rim at print size.
ax.plot(x,current*1e9,'-',color='#8075E6',linewidth=2.0,zorder=2)
ax.plot(x,current*1e9,'o',linestyle='None',markersize=8.0,
        markerfacecolor='#AAA3F5',markeredgecolor='#AAA3F5',zorder=3)
ax.plot(x,current*1e9,'o',linestyle='None',markersize=4.4,
        markerfacecolor='#F1EEFF',markeredgecolor='#F1EEFF',zorder=4)
ax.set_xlim(200,600)
ax.set_ylim(-.45,35.8)
ax.set_xticks([200,300,400,500,600])
ax.set_yticks([0,10,20,30])
ax.tick_params(direction='in',top=False,right=False,pad=12)
for wl in (254,324):
    val=np.interp(wl,x,current)*1e9
    ax.vlines(wl,0,val,color='#555555',linestyle=':',linewidth=1.5)
ax.text(217,19.4,'254 nm',fontsize=25,ha='left')
ax.text(345,30.0,f'Peak\n{x[imax]:g} nm',fontsize=25,ha='left',va='center')
ax.text(378,17.0,f'FWHM\n{fwhm:.1f} nm',fontsize=25,ha='left',va='center')
ax.text(1,1.025,'@3 V  210 '+chr(956)+'W/cm'+chr(178),transform=ax.transAxes,
        ha='right',va='bottom',fontsize=30)
fig.text(16/30,3.8/30,'Wavelength (nm)',ha='center',va='center',fontsize=40)
fig.text(1.2/30,15/30,'Photocurrent (nA)',ha='center',va='center',rotation=90,
        rotation_mode='anchor',fontsize=40)
fig.savefig(str(PREFIX)+'.pdf')
fig.savefig(str(PREFIX)+'.svg')
fig.savefig(str(PREFIX)+'.tiff',dpi=600,pil_kwargs={'compression':'tiff_lzw'})
fig.savefig(str(PREFIX)+'_preview.png',dpi=300)
plt.close(fig)
report=dict(type='MODEL_DERIVED_NOT_MEASURED',source=str(source),
    current_definition='Illuminated total current, following reference; dark offset ~0.00667 nA.',
    anchors=anchors,peak_nm=float(x[imax]),fwhm_nm=fwhm,half_crossings_nm=[left,right],
    notes=['Prior adjusted spectrum is model input, not raw measured evidence.',
           'Main region >=290 nm uses constant net-current scaling to latest 324 nm IV.',
           'Below 290 nm compact smooth correction enforces latest 254 nm anchor.',
           'FWHM uses half height above dark baseline, nearest crossings around global peak.',
           'All input rows retained; no noise added. Exported TXT current units nA.'])
(OUT/'参数与来源.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True,indent=2))

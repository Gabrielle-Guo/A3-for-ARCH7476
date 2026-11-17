"""A3 Window C reproducible, OSM-anchored *exploratory* prototype.

Actual OSM: park northeast/east-boundary nodes and node links. All Window C
placement parameters, edge-as-flow proxies, thresholds are researcher assumptions.
These outputs do not establish observed walking activity or actual comfort.
"""
from pathlib import Path
import json, sys, platform
import numpy as np, pandas as pd, geopandas as gpd
from pyproj import Transformer
from shapely.geometry import Point, Polygon, LineString
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPolygon, Patch
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parent.parent
IN=ROOT/'inputs'; OUT=ROOT/'outputs'
IN.mkdir(exist_ok=True,parents=True); OUT.mkdir(exist_ok=True,parents=True)
CONFIG={
 'crs':'EPSG:2326', 'window_size_m':6.0,
 'c_window_start_south_of_osm_ne_m':5.0,
 'seat_length_m':2.0, 'seat_width_m':1.0,
 'positions_m':[2.2,3.2,4.3],
 'w_values_m':[.75,1.0,1.5], 'base_w_m':1.0,
 'c1_m':.30, 'c2_m':1.50, 'band_threshold_s_pct':60.0,
 'flow_proxy_edges':['east_garden_boundary','north_assumed_window_edge'],
 'source':'OpenStreetMap (OSM) way 27059126; tagged garden perimeter nodes; accessed 2026-11-13',
 'warning':'EAST EDGE IS A GARDEN BOUNDARY, NOT VERIFIED FOOTWAY; NORTH EDGE CONSTRUCTED. NO MEASURED WALKING FLOW.'
}
# The following are read from individual public OpenStreetMap node pages;
# IDs and coordinates retained for traceability. The northwestern node remains unverified.
NODES=[
 ('8308187127','W boundary',22.2803521,114.1750059),
 ('296894101','SW',22.2801692,114.1750221),
 ('12270766150','S-mid',22.2802022,114.1754572),
 ('296894102','SE',22.2802402,114.1759591),
 ('296894103','NE',22.2806549,114.1759247),
]
proj=Transformer.from_crs('EPSG:4326','EPSG:2326',always_xy=True)
node_data=[]
for osm_id,label,lat,lon in NODES:
 x,y=proj.transform(lon,lat)
 node_data.append({'osm_id':osm_id,'label':label,'lat':lat,'lon':lon,
       'url':f'https://www.openstreetmap.org/node/{osm_id}','geometry':Point(x,y)})
node_gdf=gpd.GeoDataFrame(node_data,crs=CONFIG['crs'])
node_gdf.to_file(IN/'osm_garden_nodes_verified.geojson',driver='GeoJSON')
NE=np.array(node_gdf.loc[node_gdf.label=='NE','geometry'].iloc[0].coords[0])
SE=np.array(node_gdf.loc[node_gdf.label=='SE','geometry'].iloc[0].coords[0])
t=(SE-NE)/np.linalg.norm(SE-NE)  # unit vector along east garden boundary toward south
n=np.array([t[1],-t[0]]) # inward (west) normal
assert n[0]<0
O=NE+CONFIG['c_window_start_south_of_osm_ne_m']*t

def xy(u,v): return tuple(O+float(u)*n+float(v)*t)
def local_poly(coords):return Polygon([xy(u,v) for u,v in coords])
W=CONFIG['window_size_m']
window=local_poly([(0,0),(W,0),(W,W),(0,W)])
edge_east=LineString([tuple(NE),tuple(SE)])
edge_north=LineString([xy(0,0),xy(W,0)])
window_gdf=gpd.GeoDataFrame([{'id':'C','source':'RESEARCHER-DEFINED 6x6m, OSM-east-boundary-anchored','geometry':window}],crs=CONFIG['crs'])
window_gdf.to_file(IN/'window_C_osm_anchored_ASSUMED.geojson',driver='GeoJSON')
edge_gdf=gpd.GeoDataFrame([
 {'name':'east_garden_boundary','source':'OSM WAY 27059126 - garden boundary, pedestrian flow UNVERIFIED','geometry':edge_east},
 {'name':'north_assumed_window_edge','source':'RESEARCHER-CONSTRUCTED - not a mapped path or observed flow','geometry':edge_north},
],crs=CONFIG['crs'])
edge_gdf.to_file(IN/'flow_edge_proxies_NOT_PATHS.geojson',driver='GeoJSON')
rows=[]
for i,location in enumerate(['Near','Centre','Far']):
 for orientation in ['parallel','perpendicular']:
  vid=f'S{2*i+(1 if orientation=="parallel" else 2)}'
  rows.append({'variant':vid,'position':location,'distance_from_flow_edge_m':CONFIG['positions_m'][i],
               'orientation':orientation,'seat_L_m':2.0,'seat_W_m':1.0,'value_status':'RESEARCHER ASSUMPTION'})
variants=pd.DataFrame(rows)
variants.to_csv(IN/'variants.csv',index=False)

def seat_polygon(distance,ori,edge):
 if edge=='east_garden_boundary':
  uc,vc=distance,3.0
  du,dv=(.5,1.0) if ori=='parallel' else (1.0,.5)
 else:
  uc,vc=3.0,distance
  du,dv=(1.0,.5) if ori=='parallel' else (.5,1.0)
 return local_poly([(uc-du,vc-dv),(uc+du,vc-dv),(uc+du,vc+dv),(uc-du,vc+dv)])

allresults=[]
for edge in CONFIG['flow_proxy_edges']:
 line=edge_east if edge=='east_garden_boundary' else edge_north
 for w in CONFIG['w_values_m']:
  corridor=line.buffer(w,cap_style='flat')
  comfort=line.buffer(w+CONFIG['c2_m'],cap_style='flat').difference(
    line.buffer(w+CONFIG['c1_m'],cap_style='flat')).intersection(window)
  for v in rows:
   seat=seat_polygon(v['distance_from_flow_edge_m'],v['orientation'],edge)
   ov=seat.intersection(corridor).area
   band=seat.intersection(comfort).area
   status='Conflict' if ov>1e-8 else 'Clear under assumed geometry'
   allresults.append({'variant':v['variant'],'position':v['position'],'orientation':v['orientation'],
     'flow_proxy':edge,'w_m':w,'corridor_overlap_m2':round(ov,5),
     'comfort_band_share_pct':round(band*100/seat.area,3),'seat_area_m2':round(seat.area,5),
     'inside_window':window.covers(seat),'geom_status':status,
     'band_threshold_pass':bool(ov < 1e-8 and 100*band/seat.area >= CONFIG['band_threshold_s_pct']),
     'data_status':'OSM-ANCHORED LOCATION; WINDOW, FLOW, THRESHOLD ASSUMED'})
res=pd.DataFrame(allresults)
assert len(res)==36 and res.inside_window.all() and np.allclose(res.seat_area_m2,2.0)
res.to_csv(OUT/'a3_results_osm_anchored.csv',index=False)
base=res[(res.flow_proxy=='east_garden_boundary')&(res.w_m==1.)].copy().sort_values('variant')
base.to_csv(OUT/'a3_base_comparison.csv',index=False)
known=base.loc[base.variant=='S1','comfort_band_share_pct'].iloc[0]
assert np.isclose(known,80.0)
# source layer coordinates checks
edgelen=edge_east.length
assert 40 < edgelen < 55
checks=pd.DataFrame([
 ('East OSM boundary length','40 to 55m',f'{edgelen:.2f} m','PASS, based on cited OSM node coords'),
 ('36 scenario output rows','36',str(len(res)),'PASS'),
 ('Seat area after rotation','2.00 m2',f"{res.seat_area_m2.min():.2f} to {res.seat_area_m2.max():.2f} m2",'PASS'),
 ('Known case S1 band share east/w=1','80.0% by hand','%.1f%%'%known,'PASS'),
 ('All seats in assumed Window C','True',str(bool(res.inside_window.all())),'PASS'),
 ('Footway/observed flow at NE garden edge','OSM footway/field verification','OSM garden boundary only','PENDING'),
 ('Window C true extent','surveyed C polygon','6x6m assumption','PENDING'),
 ('Comfort threshold validation','observational/literature evidence','c1/c2/s assumed','PENDING'),
],columns=['check','expected','observed','status'])
checks.to_csv(OUT/'a3_verification_log.csv',index=False)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
GREEN='#236456'; SAGE='#b7d0c7'; MUSTARD='#c6ac67'; ORANGE='#ac6042'; DARK='#283b38'
# site footprint figure based on OSM nodes; missing NW not connected
fig,ax=plt.subplots(figsize=(9,5.4))
node_order=['W boundary','SW','S-mid','SE','NE']
polypts=[node_gdf.loc[node_gdf.label==name,'geometry'].iloc[0].coords[0] for name in node_order]
ax.plot([p[0] for p in polypts],[p[1] for p in polypts],color=GREEN,lw=2.5,label='Verified garden perimeter segments')
for row in node_gdf.itertuples():
 ax.scatter(row.geometry.x,row.geometry.y,s=30,color=GREEN)
 ax.text(row.geometry.x+1,row.geometry.y+1,row.label,fontsize=9)
wx,wy=window.exterior.xy
ax.fill(wx,wy,color=MUSTARD,alpha=.50,ec=ORANGE,lw=2,label='Window C (6×6m assumed)')
ax.plot(*edge_east.xy,color=ORANGE,linewidth=4,label='OSM garden east edge (not footway)')
ax.annotate('Window C',xy=window.centroid.coords[0],xytext=(NE[0]-40,NE[1]-3),arrowprops=dict(arrowstyle='->',color=ORANGE),fontsize=11,color=ORANGE)
ax.set_aspect('equal');ax.set_xlabel('Hong Kong Grid Easting (m)');ax.set_ylabel('Northing (m)')
ax.set_title('OSM-sourced garden geometry + researcher-defined Window C',weight='bold')
ax.legend(fontsize=8,loc='lower left',frameon=False)
ax.grid(alpha=.12); fig.text(.02,.008,'OSM way 27059126 | 5 individually sourced nodes; NW node not retrieved | C size and flow unverified',color=ORANGE,fontsize=8)
fig.tight_layout(rect=[0,.035,1,1]);fig.savefig(OUT/'osm_context.png',dpi=180);plt.close(fig)
# plan in local window coords (east edge u=0; inward u positive)
fig,ax=plt.subplots(figsize=(8.9,6))
ax.add_patch(MPolygon(np.array([(0,0),(W,0),(W,W),(0,W)]),closed=True,facecolor='#eff5f0',edgecolor=GREEN,lw=2))
w=1.;c1=CONFIG['c1_m'];c2=CONFIG['c2_m']
ax.axvspan(0,w,color=SAGE,alpha=.80,label='Route corridor *proxy*')
ax.axvspan(w+c1,w+c2,color=MUSTARD,alpha=.48,label='Assumed comfort band')
for bound,color,ls in [(w,GREEN,'--'),(w+c1,ORANGE,':'),(w+c2,ORANGE,':')]:ax.axvline(bound,color=color,lw=1.5,ls=ls)
for v in rows:
 seat=seat_polygon(v['distance_from_flow_edge_m'],v['orientation'],'east_garden_boundary')
 # convert points back to local (u,v) for plotting
 uv=[(float(np.dot(np.array(p)-O,n)),float(np.dot(np.array(p)-O,t))) for p in seat.exterior.coords]
 chosen=v['variant']=='S1'
 ax.add_patch(MPolygon(np.array(uv),closed=True,facecolor=GREEN if chosen else 'white',edgecolor=GREEN if chosen else ORANGE,lw=1.7,alpha=.92))
 ucenter=v['distance_from_flow_edge_m']; vcenter=3
 ax.text(ucenter,vcenter,v['variant'],fontsize=10,color='white' if chosen else DARK,ha='center',va='center',fontweight='bold')
ax.text(.10,5.75,'OSM EAST GARDEN BOUNDARY',color=GREEN,fontsize=9,weight='bold',rotation=90,va='top')
ax.set_aspect('equal');ax.set_xlim(-.3,6.35);ax.set_ylim(-.35,6.45)
ax.set_xlabel('Distance inward from east garden edge (m)');ax.set_ylabel('Distance south along edge (m)')
ax.set_title('Window C  |  6 assumed seat placements',fontweight='bold')
ax.legend(loc='upper right',frameon=False,fontsize=9)
fig.text(.02,.009,'OSM-anchored, NOT observed pedestrian flow; Window C = researcher-defined 6×6m; thresholds provisional',color=ORANGE,fontsize=8)
fig.tight_layout(rect=[0,.035,1,1]);fig.savefig(OUT/'a3_plan_osm.png',dpi=180);plt.close(fig)
# decision chart
fig,ax=plt.subplots(figsize=(9.5,4.4))
colors=[GREEN if r.band_threshold_pass else '#b9c4bd' for r in base.itertuples()]
ax.bar(base.variant,base.comfort_band_share_pct,color=colors,edgecolor=GREEN,width=.65)
ax.axhline(CONFIG['band_threshold_s_pct'],color=ORANGE,lw=2,ls='--')
ax.text(5.55,CONFIG['band_threshold_s_pct']+2,'s = 60% (ASSUMED)',color=ORANGE,fontsize=9,ha='right')
for i,r in enumerate(base.itertuples()):ax.text(i,r.comfort_band_share_pct+2,f'{r.comfort_band_share_pct:.0f}%',ha='center',fontsize=10)
ax.set_ylim(0,110);ax.set_ylabel('Comfort-band share (%)');ax.set_title('Conditional comparison | east garden-edge proxy, w = 1.0 m',fontweight='bold')
ax.spines[['top','right']].set_visible(False)
fig.text(.02,.008,'OSM-ANCHORED EXPLORATION • C window / edge-flow / c1 c2 s remain assumed; no behavioural conclusion',color=ORANGE,fontsize=8)
fig.tight_layout(rect=[0,.035,1,1]);fig.savefig(OUT/'a3_threshold_chart.png',dpi=180);plt.close(fig)
# flip chart
fig,ax=plt.subplots(figsize=(9.5,4.4))
for v in ['S1','S2','S3','S4','S5','S6']:
 part=res[(res.variant==v)&(res.flow_proxy=='east_garden_boundary')].sort_values('w_m')
 ax.plot(part.w_m,part.comfort_band_share_pct,marker='o',label=v,alpha=1 if v=='S1' else .65,lw=2.5 if v=='S1' else 1.25)
ax.axhline(CONFIG['band_threshold_s_pct'],color=ORANGE,lw=2,ls='--',label='s = 60% assumed')
ax.set_xticks(CONFIG['w_values_m']);ax.set_ylim(-3,105);ax.set_xlim(.7,1.55)
ax.set_xlabel('Corridor half-width w (m; assumed)');ax.set_ylabel('Comfort-band share (%)')
ax.set_title('Threshold sensitivity | east garden-edge proxy',fontweight='bold')
ax.grid(alpha=.15);ax.legend(ncol=4,frameon=False,fontsize=9)
fig.text(.02,.008,'S1 crosses s=60% between tested w=.75 and w=1.0 • scenario dependence, not measured comfort',color=ORANGE,fontsize=8)
fig.tight_layout(rect=[0,.035,1,1]);fig.savefig(OUT/'a3_flip_chart.png',dpi=180);plt.close(fig)
summary={'status':'OSM-ANCHORED GEOMETRY / ALL FLOW AND BEHAVIOR ASSUMPTIONS UNVALIDATED',
 'osm_garden_way':'https://www.openstreetmap.org/way/27059126','osm_ne_node':'296894103',
 'osm_se_node':'296894102','osm_east_boundary_length_m':round(edgelen,2),
 'window_C':'researcher-defined 6x6m patch along east garden edge 5m south of OSM NE node',
 'base_east_proxy_w1_band_share_pct':dict(zip(base.variant,base.comfort_band_share_pct)),
 'base_best_conditional':base.sort_values('comfort_band_share_pct',ascending=False).iloc[0].variant,
 'source_caveat':'OSM east garden boundary is not tagged as footway. North flow edge is an assumed window-side segment.',
 'assumption_note':'c1=.3m, c2=1.5m, s=60% researcher-defined; no measured pedestrian routes or stop counts.'}
(OUT/'a3_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
(IN/'osm_provenance.json').write_text(json.dumps({'access_date':'2026-11-13','garden_way':'https://www.openstreetmap.org/way/27059126','nodes':[{k:v for k,v in item.items() if k!='geometry'} for item in node_data],'status':'Only 5 of 6 unique garden boundary nodes retrieved as verifiable HTML; northeast and east side complete.'},indent=2),encoding='utf8')
(OUT/'versions.txt').write_text('\n'.join(['python '+platform.python_version(),'geopandas '+gpd.__version__,'shapely '+__import__('shapely').__version__,'matplotlib '+matplotlib.__version__,'pyproj '+__import__('pyproj').__version__,'pandas '+pd.__version__]),encoding='utf8')
print(json.dumps(summary,indent=2))

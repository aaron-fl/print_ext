from .printer_test import _printer
from print_ext.printer import Printer
from print_ext.table import Table
import cProfile, re, pstats, sys

print = Printer(color=True, width=500)
hard = {'apiVersion': 'networking.k8s.io/v1', 'kind': 'Ingress', 'metadata': {'name': 'toss-ingress', 'namespace': 'toss', 'annotations': {'kubernetes.io/ingress.global-static-ip-name': 'toss-ip', 'nginx.ingress.kubernetes.io/proxy-read-timeout': '120'}}, 'spec': {'tls': [{'secretName': 'toss-online-com-certbot'}], 'rules': [{'host': 'm-test.tos-land.net', 'http': {'paths': [{'path': '/', 'pathType': 'Prefix', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}]}}, {'host': 'tos-land.net', 'http': {'paths': [{'path': '/', 'pathType': 'Prefix', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}]}}, {'host': 'www.tos-land.net', 'http': {'paths': [{'path': '/', 'pathType': 'Prefix', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}]}}, {'host': 'm.tos-land.net', 'http': {'paths': [{'path': '/', 'pathType': 'Prefix', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}]}}, {'host': 'test-video.toss-online.com', 'http': {'paths': [{'path': '/', 'pathType': 'Prefix', 'backend': {'service': {'name': 'test-frontend-service', 'port': {'number': 9104}}}}, {'path': '/vkey', 'pathType': 'Prefix', 'backend': {'service': {'name': 'test-api-service', 'port': {'number': 9100}}}}, {'path': '/api', 'pathType': 'Exact', 'backend': {'service': {'name': 'test-api-service', 'port': {'number': 9100}}}}, {'path': '/apitest', 'pathType': 'Exact', 'backend': {'service': {'name': 'test-api-service', 'port': {'number': 9100}}}}, {'path': '/download', 'pathType': 'Prefix', 'backend': {'service': {'name': 'test-api-service', 'port': {'number': 9100}}}}, {'path': '/vinfo', 'pathType': 'Prefix', 'backend': {'service': {'name': 'test-api-service', 'port': {'number': 9100}}}}]}}, {'host': 'video.toss-online.com', 'http': {'paths': [{'path': '/', 'pathType': 'Prefix', 'backend': {'service': {'name': 'prod-frontend-service', 'port': {'number': 9004}}}}, {'path': '/vkey', 'pathType': 'Prefix', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}, {'path': '/api', 'pathType': 'Exact', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}, {'path': '/apitest', 'pathType': 'Exact', 'backend': {'service': {'name': 'test-api-service', 'port': {'number': 9100}}}}, {'path': '/download', 'pathType': 'Prefix', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}, {'path': '/vinfo', 'pathType': 'Prefix', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}]}}, {'host': 'api.toss-online.com', 'http': {'paths': [{'path': '/apitest', 'pathType': 'Exact', 'backend': {'service': {'name': 'test-api-service', 'port': {'number': 9100}}}}, {'path': '/testpayjp', 'pathType': 'Exact', 'backend': {'service': {'name': 'test-api-service', 'port': {'number': 9100}}}}, {'path': '/testworkplace', 'pathType': 'Exact', 'backend': {'service': {'name': 'test-api-service', 'port': {'number': 9100}}}}, {'path': '/api', 'pathType': 'Exact', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}, {'path': '/payjp', 'pathType': 'Exact', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}, {'path': '/workplace', 'pathType': 'Exact', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}]}}, {'host': 'papi.toss-online.com', 'http': {'paths': [{'path': '/api', 'pathType': 'Exact', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}]}}]}}

simple = {'apiVersion': 'networking.k8s.io/v1  the is the longest line of them all, twoa three foru five six seven eight nine ten ', 'kind': 'Ingress', 'metadata': {'name': 'toss-ingress', 'namespace': 'toss', 'annotations': {'kubernetes.io/ingress.global-static-ip-name': 'toss-ip', 'nginx.ingress.kubernetes.io/proxy-read-timeout': '120'}}, 'spec': {'tls': [{'secretName': 'toss-online-com-certbot'}], 'rules': [{'host': 'm-test.tos-land.net', 'http': {'paths': [{'path': '/', 'pathType': 'Prefix', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}]}}, {'host': 'tos-land.net', 'http': {'paths': [{'path': '/', 'pathType': 'Prefix', 'backend': {'service': {'name': 'prod-api-service', 'port': {'number': 9000}}}}]}} ]}}

def make_profile(x):    
    print.pretty(x)

    

def show(f1, f2):

    p1 = pstats.Stats(f1)
    p1.strip_dirs()
    p2 = pstats.Stats(f2)
    p2.strip_dirs()
    
    t = Table(1,1,1,1,1,1,1,1)
    t.cell('c0',just='>') # Calls
    t.cell('c1',border='m:0', style='dem') # /Recursive
    t.cell('C5',just='>',style='1') #Filename
    t.cell('C6',border='m:0', style='dem') #lineno
    t.cell('C7',style='2') # Function
    t('Calls\t','\bdem /Recursive\t', 'Delta\t', 'TotTime\tCumTime\tFile\t','\bdem :lno','\tFunction\t')

    def _pct(chg):
        chg *= 100
        chgs = f'{chg:.1f}'
        return ('\br$' if chg < -1 else '\b;$' if chg < 3 else '\bg;$' if chg < 10 else '\bg!$', f'+{chgs}' if chg >= 0 else chgs) if chgs != '0.0' else (' ',)

    for k,v in sorted(p1.stats.items(), key=lambda x: x[1][3]):#x[1][3] / x[1][0]):
        v2 = p2.stats[k] if k in p2.stats else v
        t(v[0],'\t')
        if v[1]!=v[0]: t('/', v[1]) 
        t(*_pct((v2[1] - v[1])/v[1]), '\t')
        t(' ' , '\t')#t('\br$' if chg < -1 else '' if chg < 3 else '\by;$' if chg < 10 else '\bg!$', f'{chg:.1f}', '\t')
        #  time
        v2p = int(v[2]*1000//v[1])
        if v[2] >= 0.05:
            t(f'{v[2]:.1f}', f'\bdem  {v2p or ""}')
            t(*_pct((v2[2]-v[2])/v[2]), '\t')
        else:
            t(' \t')
        # Cumulative time 
        v3p = int(v[3]*1000//v[0])
        if v[3] >= 0.05:
            t(f'{v[3]:.1f}', f'\bdem  {v3p or ""}')
            t(*_pct((v2[3]-v[3])/v[3]), '\t')
        else:
            t(' \t')
        # Filename
        t(k[0], '\t', ':',k[1],'\t') if k[1] else t(' \t \t')
        # Function
        t(k[2],)
        for k in v[4]:
            t(' \b3$ ',k[0],':',k[1])
        t('\t')
        
    print(t)
    print(p1.total_tt, ' -> ', p2.total_tt,  '  ', *_pct((p2.total_tt-p1.total_tt)/p1.total_tt))




if __name__=='__main__':        
    if sys.argv[1] in 'hs':
        if len(sys.argv) > 2:
            cProfile.run('make_profile('+('hard' if sys.argv[1]=='h' else 'simple')+')', sys.argv[2])
        else:
            make_profile(hard if sys.argv[1]=='h' else simple)
        sys.exit(0)
    f1 = sys.argv[1]
    f2 = f1 if len(sys.argv) == 2 else sys.argv[2]
    show(f1,f2)

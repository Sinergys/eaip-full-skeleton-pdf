import py_compile
import pathlib
base=pathlib.Path('C:/eaip/eaip_full_skeleton/services/ingest/tests')
files=list(base.glob('*.py'))
ok=[]
err=[]
for f in files:
    try:
        py_compile.compile(str(f), doraise=True)
        ok.append(f.name)
    except Exception as e:
        err.append((f.name,str(e)))
print('COMPILED_OK:', len(ok))
for n in ok:
    print('  ',n)
print('\nCOMPILE_ERRORS:', len(err))
for n,e in err:
    print('  ',n,'->',e)

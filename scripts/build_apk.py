"""Build a debug-signed APK with official Android SDK tools and JDK 17+.
ANDROID_SDK_ROOT must contain platforms/android-35 and build-tools/35.0.0.
No Gradle dependencies. The generated key is for local testing, not production.
"""
import os
import pathlib
import shutil
import subprocess
import zipfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
SDK=pathlib.Path(os.environ['ANDROID_SDK_ROOT'])
TOOLS=SDK/'build-tools/35.0.0'
JAR=SDK/'platforms/android-35/android.jar'
OUT=ROOT/'android/build'
OUT.mkdir(parents=True,exist_ok=True)

def run(*args):
    subprocess.run([str(a) for a in args],check=True,cwd=ROOT)

assets=OUT/'assets'
if assets.exists():shutil.rmtree(assets)
assets.mkdir()
for name in ('index.html','src','public','docs'):
    source=ROOT/name
    if source.is_dir():shutil.copytree(source,assets/name)
    else:shutil.copy2(source,assets/name)
# APK assets are local: skip PWA registration and installation prompt.
p=assets/'index.html'
s=p.read_text().replace('<script type="module" src="/src/pwa.js"></script>','').replace('<link rel="manifest" href="/manifest.webmanifest">','')
p.write_text(s)
run(TOOLS/'aapt2','compile','--dir',ROOT/'android/res','-o',OUT/'resources.zip')
run(TOOLS/'aapt2','link','-o',OUT/'unsigned.apk','--manifest',ROOT/'android/AndroidManifest.xml','-I',JAR,'-A',assets,OUT/'resources.zip')
classes=OUT/'classes'
classes.mkdir(exist_ok=True)
compiler=['java','-jar',os.environ['ECJ_JAR']] if os.environ.get('ECJ_JAR') else ['javac']
run(*compiler,'-source','8','-target','8','-classpath',JAR,'-d',classes,*sorted((ROOT/'android/src').rglob('*.java')))
run(TOOLS/'d8','--lib',JAR,'--min-api','26','--output',OUT,*sorted(classes.rglob('*.class')))
with zipfile.ZipFile(OUT/'unsigned.apk','a',zipfile.ZIP_DEFLATED) as apk:apk.write(OUT/'classes.dex','classes.dex')
run(TOOLS/'zipalign','-f','4',OUT/'unsigned.apk',OUT/'aligned.apk')
key=OUT/'debug.keystore'
if not key.exists():
    run('keytool','-genkeypair','-keystore',key,'-storepass','android','-keypass','android','-alias','androiddebugkey','-dname','CN=Android Debug,O=Lobos Espaciales,C=MX','-keyalg','RSA','-keysize','2048','-validity','10000')
(ROOT/'downloads').mkdir(exist_ok=True)
output=ROOT/'downloads/LobosMarte-debug.apk'
run(TOOLS/'apksigner','sign','--ks',key,'--ks-key-alias','androiddebugkey','--ks-pass','pass:android','--key-pass','pass:android','--out',output,OUT/'aligned.apk')
run(TOOLS/'apksigner','verify','--verbose',output)
print('APK:',output)

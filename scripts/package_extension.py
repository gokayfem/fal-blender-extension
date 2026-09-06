"""Build a wheel-bundled extension ZIP for one Blender Python/platform target."""
import argparse
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

PLATFORMS = {'windows-x64': 'win_amd64', 'windows-arm64': 'win_arm64',
             'linux-x64': 'manylinux_2_28_x86_64', 'macos-arm64': 'macosx_11_0_arm64',
             'macos-x64': 'macosx_11_0_x86_64'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--platform', choices=PLATFORMS, required=True)
    parser.add_argument('--python-version', choices=['3.11', '3.13'], required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    dist = root / 'dist'; dist.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='package-', dir=dist) as temp:
        wheels = Path(temp) / 'wheels'; wheels.mkdir()
        subprocess.run([sys.executable, '-m', 'pip', 'download', '--only-binary=:all:',
                        '--platform', PLATFORMS[args.platform], '--python-version', args.python_version,
                        '--implementation', 'cp', '--abi', 'cp' + args.python_version.replace('.', ''),
                        '--dest', str(wheels), '-r', str(root / 'requirements.txt')], check=True)
        manifest = (root / 'blender_manifest.toml.template').read_text(encoding='utf-8')
        manifest = re.sub(r'^platforms = .*$', f'platforms = ["{args.platform}"]', manifest, flags=re.M)
        entries = ',\n'.join(f'    "./wheels/{p.name}"' for p in sorted(wheels.glob('*.whl')))
        manifest = re.sub(r'^wheels = \[.*?\]', 'wheels = [\n' + entries + '\n]', manifest, flags=re.M|re.S)
        version = re.search(r'^version = "([^"]+)"', manifest, re.M).group(1)
        archive = dist / f'fal_ai-{version}-{args.platform}-py{args.python_version}.zip'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('blender_manifest.toml', manifest)
            for file in sorted(root.glob('*.py')):
                z.write(file, file.name)
            z.write(root / 'LICENSE', 'LICENSE')
            for directory in ('controllers', 'models', 'assets'):
                for file in sorted((root / directory).rglob('*')):
                    relative = file.relative_to(root)
                    if not file.is_file() or '__pycache__' in relative.parts or relative.parts[:2] == ('assets','demo'):
                        continue
                    if file.suffix in {'.py', '.png', '.jpg', '.jpeg', '.svg', '.json', '.ttf', '.otf'}:
                        z.write(file, relative.as_posix())
            for file in sorted(wheels.glob('*.whl')):
                z.write(file, 'wheels/' + file.name)
        print(f'Built {archive.name} ({archive.stat().st_size / 1024**2:.1f} MiB)')


if __name__ == '__main__':
    main()

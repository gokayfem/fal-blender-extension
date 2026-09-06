"""Generate and freeze four object-free Krea 2 Turbo style references."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.request

MODEL = 'fal-ai/krea-2/turbo'
COMMON = ('A full-frame completely nonrepresentational color, light and material field. '
    'One continuous edge-to-edge abstract texture at an unrecognizable scale, without any subject or discrete silhouette. '
    'Pure aesthetic reference: palette, lighting quality, surface roughness and photographic response only. '
    'No identifiable objects, vehicles, people, structures, scenery, horizon, products, spheres, cubes, panels, '
    'swatch grids, text, symbols, labels, borders or frames. ')
STYLES = (
    ('expedition', 'EXPEDITION / REAL', 'Deep navy blue and ocean teal blending into warm ivory highlights. Natural broad daylight, soft silvery specular reflections, smooth satin enamel-like response, subtle liquid microtexture. Restrained realistic photographic color, generous calm areas, continuous gently curved tonal transitions. '),
    ('storm', 'NORTH SEA / STORM', 'Cold charcoal, slate gray and desaturated deep blue. Diffuse silver light blooms across dark wet-looking microtexture, subtle diagonal mist-like grain and smooth atmospheric gradients. Cinematic low-key exposure, soft highlights and rich readable shadows. An abstract moody cool material field. '),
    ('orbital', 'ORBITAL / SCI-FI', 'Luminous pearl white, pale lavender, deep indigo and restrained electric cyan. Smooth ceramic-like sheen, soft metallic iridescence, flowing cyan reflections through continuous violet gradients. Futuristic cinematic light with elegant negative space, gentle glossy curvature, no hard polygon boundaries. '),
    ('miniature', 'WORKSHOP / MINIATURE', 'Warm cream, soft ochre, muted navy and desaturated teal. Fine hand-painted matte pigment grain, very subtle tactile surface variation, warm diffuse softbox-like light and shallow-focus creamy transitions. A quiet handcrafted photographic material field, softly imperfect and intimate. '),
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--env')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    key = os.environ.get('FAL_KEY', '')
    if args.env:
        for line in Path(args.env).read_text(encoding='utf-8-sig').splitlines():
            if line.strip().startswith('FAL_KEY='):
                key = line.split('=', 1)[1].strip().strip('\"\'')
                break
    if not key:
        raise RuntimeError('FAL_KEY is required')
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out/'manifest.json').exists():
        raise RuntimeError('Style references already exist; choose a new output directory to create a new set')

    def generate(item):
        index, (name, label, treatment) = item
        prompt = COMMON + treatment
        payload = dict(prompt=prompt, seed=91040+index, image_size=dict(width=1024,height=576),
            num_images=1, acceleration='none', enable_prompt_expansion=False,
            enable_safety_checker=True, sync_mode=False, output_format='jpeg')
        started = time.perf_counter()
        request = urllib.request.Request('https://fal.run/'+MODEL, data=json.dumps(payload).encode(),
            headers={'Authorization':'Key '+key, 'Content-Type':'application/json'})
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.load(response)
        if any(result.get('has_nsfw_concepts', [])):
            raise RuntimeError('Style image was flagged; generation stopped')
        url = result['images'][0]['url']
        if not url.startswith('https://'):
            raise RuntimeError('Expected an HTTPS image URL')
        with urllib.request.urlopen(url, timeout=60) as response:
            image = response.read()
        path = out/(name+'.jpg')
        path.write_bytes(image)
        return dict(id=name,label=label,file=path.name,sha256=hashlib.sha256(image).hexdigest(),
            seed=result.get('seed', payload['seed']),prompt=prompt,source_url=url,
            seconds=time.perf_counter()-started,provider_timings=result.get('timings'))

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        images = list(pool.map(generate, enumerate(STYLES)))
    manifest = dict(version=1,model=MODEL,verified_schema='2026-09-06',
        schema_url='https://fal.ai/models/fal-ai/krea-2/turbo/llms.txt',
        purpose='Object-free fixed style references; geometry comes from the current viewport',styles=images)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(dict(manifest=str(out/'manifest.json'),images=[dict(style=i['label'],seconds=i['seconds']) for i in images]),indent=2))


if __name__ == '__main__':
    main()

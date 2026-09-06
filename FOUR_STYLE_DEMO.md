# Four-style Blender live build

Measured September 6, 2026 in Blender 5.1.2 on Windows. A continuous screen
recording captured seven actual scripted geometry stages beside four generated
Movie Clip Editor panes. Each stage sent the same 512×290 gray JPEG to four
concurrent H3 Max reference-to-video calls, producing 28 distinct five-second
480P clips. There were no supplied output clips, cuts, or time compression.

| Measured interval | Minimum | Median | Maximum |
|---|---:|---:|---:|
| Capture start to all four visible | 4.87s | 5.83s | 11.99s |
| Settled geometry edit to all four visible | 5.77s | 6.74s | 12.89s |
| Reported GPU inference per clip | 1.13s | 1.14s | 1.17s |

Treatments: expedition realism, North Sea storm, cinematic science fiction, and
physical miniature. Prompts limit style to surfaces, light and water. Geometry
descriptions specify
only currently modeled components, and plain surfaces must remain plain. Earlier
semantic ship prompts invented extra structures; the revised four-style bare-hull
probe preserved the simple slab in every style. Reference conditioning remains
approximate, with possible silhouette, scale, camera, and temporal drift. This is
an asynchronous live art-direction prototype, not a geometry-exact
real-time renderer. Parallelism gives four alternatives per refresh; it does not
remove API, transfer, decode, or edit-to-visible latency.

The first single-view attempt discarded valid responses because dependency-graph
invalidations were treated as edits. Content-based geometry comparison fixed it.
The test suite checks that invalidation alone does not change the geometry digest,
vertex edits do, four calls run concurrently from one capture, and out-of-order
responses reach the correct panes. Thirteen headless checks pass.

Local artifacts: `../outputs/minimal-four-style-build/gray-live-build.blend`,
`build-status.json`, `summary.json`, `final-screen.png`, and `recordings/*.mp4`.
The video retains real wait times. Scripted construction is explicitly labeled.

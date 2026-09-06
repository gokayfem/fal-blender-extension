# Four media, one current assembly

The four views are Cartoon, Claymation, Realistic, and Stylized Gouache. `PER_STYLE_TEXT` retains the fixed-camera geometry conditioning: repeated full frame; full frame/normals/visible mask; full frame; full frame/detail sheet. It deliberately excludes style-image URLs even if a manifest is configured. Abstract style swatches were visibly copied into the sea/background by reference-to-video in tests.

`surface_prompts.py` defines one persistent medium and an already-styled current assembly, with no reveals, transformations or lighting changes. Water must use the same medium as the vessel. `stage_prompts.py` describes only existing assemblies, gives finish detail for that stage, and places the current inventory last. An earlier phrase, "already finished ship," caused the model to invent a complete boat during early hull construction; that wording was removed.

The new reference swatches remain in assets/h3-look-references as art-direction samples. They were generated using fal-ai/krea-2/turbo and are not sent to H3 in this mode. Native 768P was tested for finer surface detail. Do not reuse the previous 480P inference-speed claims for these requests.

Tests include eight completed-ship text-style clips (four styles, two seeds), sampled across seven times and scanned frame-by-frame for color continuity, plus eight bare-hull stage-priority checks. These are limited observations, not a guarantee of no transitions or exact geometry. One clay bare-hull sample reframed, and realistic renders can add small fittings. The live detail demo is the actual verification artifact; preserve the full recording and API timing metadata.

The simple demo supports --start-stage N and an output/stop-build.flag to stop scheduling without closing Blender. --start-stage 4 builds the initial hull, enclosures and roof before recording and records three subsequent geometry edits. Requests already submitted may finish after stopping.

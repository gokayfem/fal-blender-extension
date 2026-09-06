# Consistency findings

These are bounded ship-fixture observations, not guaranteed camera/style locking.

## Rendered-frame references: 56 clips

48 fresh image-only clips compare text-only appearance, a fixed early-render anchor, and the previous rendered frame over two edits, four styles and two seeds. Eight follow-ups repeat the current geometry and explicitly list new fittings. All outputs use 768P / five seconds. The second rolling update uses the first experiment's output.

| Method | Observed tradeoff |
| --- | --- |
| Text only | Adopts new geometry better in several cases; appearance varies. |
| Fixed early render | Six of sixteen clips visibly revert to the simpler old ship during sampled playback. |
| Previous render | Carries appearance, but can suppress fenders or propagate extra mast equipment. |
| Previous + repeated geometry + explicit edit | Improves some additions; several clips still introduce fittings after time zero. |

Frames were inspected at 0, 1, 2, 3 and 4.8 seconds. Median API-plus-download times: text 9.27s, fixed 9.61s, rolling 9.85s. These exclude capture/display and do not describe four-pane latency. RGB palette metrics were insufficient: colors can remain stable while a crane disappears.

## Current demo

The fresh build uses text-defined looks and image-only camera guidance. It plays later moving excerpts, not stills. Beginning/middle/end samples of 32 excerpts showed no scene/style transitions in those samples. Short loops may have seams, and full clips can transition outside the retained range.

Open problems: reliable component acceptance, long-chain appearance stability, arbitrary-scene detail crops, transition-free full clips, and latency distributions across many live builds.

Earlier notes: [camera](../CAMERA_ALIGNMENT.md), [style](../STYLE_CONTINUITY.md), [transport](../TRANSPORT_BENCHMARK.md). Those reflect earlier settings and style sets; [DEMO.md](DEMO.md) describes the current configuration.

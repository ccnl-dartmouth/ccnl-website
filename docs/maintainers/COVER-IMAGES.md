# Journal cover images

The PI prefers the journal's cover (of the issue the paper appeared in) over a custom graphical abstract. Where a
journal has no per-issue covers, the journal logo or generic cover is used instead.

How an image is attached: upload it to `content/images/` and put its file name in the paper's `image = {...}` line.
Papers in the same issue share one file (for example both J Neurosci 44(2) papers use `cover-j-neurosci-v44-n2.jpg`).
Names used so far: `cover-<journal>-v<volume>-n<issue>.<ext>` for issue covers, `logo-<journal>.<ext>` for logos.

## Done (25 papers, downloaded automatically)

| Journal | Source | Papers |
|---|---|---|
| Journal of Neuroscience | issue cover from jneurosci.org (`/sites/default/files/highwire/jneuro/<vol>/<issue>.cover*`) | 9 |
| Nature Neuroscience, Nature Human Behaviour, Nature Reviews Neuroscience, Neuropsychopharmacology, Cognitive, Affective, & Behavioral Neuroscience | issue cover from `media.springernature.com/w440/springer-static/cover-hires/journal/<id>/<vol>/<issue>` | 6 |
| Nature Communications | generic journal cover (the journal has no issues) | 6 |
| Frontiers in Psychology / Psychiatry | journal banner image from frontiersin.org (no issue covers) | 3 |
| PLOS ONE | logo from Wikimedia Commons (no issue covers) | 1 |

## Added by hand (17 papers)

The PNAS, Neuron, Elsevier, Cerebral Cortex, J Cognitive Neuroscience and Memory covers were downloaded by hand. Notes:
several Elsevier covers are small GIFs (about 150 x 200 px), which the build copies unchanged, so they look soft;
J Cognitive Neuroscience only has a generic cover (`cover-j-cognitive-neuroscience.png`, shared by both papers).

## Still missing: journal logos (12 papers)

Journals with no per-issue covers. Save the logo as `logo-<journal>.<ext>` in `content/images/` and put the name in each
paper's `image = {...}` line.

| File name | Papers |
|---|---|
| `logo-plos-computational-biology` | 2012-soltani-range, 2017-khorsand, 2018-farashahi-dynamic, 2019-spitmaan-combinations |
| `logo-behavioral-neuroscience` | 2021-harris |
| `logo-entropy` | 2025-woo-information |
| `logo-oxford-open-neuroscience` | 2026-aguirre |
| `logo-biorxiv` | 2024-yazdanpanah, 2026-shahamati |
| `logo-ssrn` | 2025-benistant, 2026-benistant |
| `logo-ccn` | 2023-jung (the 2023 site's logo is white text, so it needs a dark-background version) |

Not yet checked: how the covers look in the Publications cards (the site was not built after adding them).

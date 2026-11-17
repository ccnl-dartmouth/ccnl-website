# Papers cited on the Research page without a link

Some citations in `content/research/*.md` are written `[@~name]`. They show a number but no link, because the paper has
no page on the site: it is in preparation, or nothing about it is posted online. **These should be filled in as the
papers appear.** Searched for online copies on 17 Nov 2026 (bioRxiv, arXiv, OSF/PsyArXiv, SSRN, Research Square, HAL):
only the first row below turned up, and it stays off the site for now.

| Theme file | Name used | Number in the text now | Paper (from the PI's CV, Oct 2026) | Status |
|---|---|---|---|---|
| `uncertainty-and-change` | `~lisitsyn-in-prep` | 4 | Lisitsyn D, Taleb F, Farashahi S, Dahaqani MR, Soltani A. Circuit mechanisms for improving the adaptability-precision tradeoff | in preparation |
| `uncertainty-and-change` | `~nong-in-prep` | 13 | Nong T, Li Y, Qu C, Woo JH, ..., Soltani A, Dreher JC. Computational modeling of the ability to read changes of cooperative vs competitive intentions in children | under review. A HAL preprint exists (`hal-04288677`, "Computational mechanisms underlying the emergence of theory of mind in children"); it was deliberately left off the site |
| `uncertainty-and-change` | `~spitmaan-in-prep` | 18 | Spitmaan M, Donahue CH, Lee D, Soltani A. Effects of volatility on timescales of neural response across cortex | in preparation (not in the CV list) |
| `uncertainty-and-change` | `~duggins-in-prep` | 21 | Duggins P, Soltani A. Generalized information integration through weighted prediction error | under revision (PNAS format); not posted |
| `attention-bias-decision-making` | `~lewis-in-prep` | 4 | Lewis CA, Chong MC, Farashahi S, Salholz-Hillel M, Soltani A. Dynamic adjustments of valuation and decision making to variability and uncertainty in the reward environment | in preparation |
| `attention-bias-decision-making` | `~yazdanpanah-in-prep` | 5 | Yazdanpanah A, Ort E, Froböse MI, Kurtenbach H, Jocham G, Soltani A. Common computational mechanisms link perception to attribute processing in value-based choice | in preparation |
| `attention-bias-decision-making` | `~cochran-in-prep` | 6 | Cochran K, Hosseinzadeh F, Saghafi F, Soltani A. Anxiety disorders impair flexibility in choice under uncertainty | in preparation |
| `attention-bias-decision-making` | `~woo-in-prep` | 7 | Woo JH, Wang MC, Bartolo R, Averbeck BB, Soltani A. Reward reshapes neural geometry according to internal beliefs | in preparation. It is the only citation for the "population-level mechanisms" sentence in theme 3 |

The numbers are counted by the build in order of first appearance, so they change if the text is edited; the names are
the stable key. A test checks that every `~name` in the research files is listed here.

## How to turn one into a link

1. When the paper is posted (bioRxiv, SSRN, journal), add its `.bib` file (see
   [Add or fix a paper](../guides/ADD-A-PAPER.md); for a preprint add `status = {preprint}` and the link).
2. In the theme file, replace `[@~name]` by `[@file-name-of-the-bib]`, without `.bib`.
3. Add the theme's tag (the theme file's name) to the new paper's `keywords`. A test fails if a paper cited in a theme
   is not tagged with it, so the "N related papers" count stays equal to the citations.
4. Delete the row above.

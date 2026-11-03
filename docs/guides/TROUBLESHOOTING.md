# When something goes wrong

After you commit, if the **Actions** tab (https://github.com/ccnl-dartmouth/ccnl-website/actions) shows a red cross, click the failed run and open the **Build the site** step. The message
names the file and says what to fix. Fix that file and commit again. The website keeps showing the last good version
in the meantime. A GitHub issue titled "The website build failed" is also opened and closes itself when it's fixed.

| The message says | What to do |
|---|---|
| `the file name must use only lowercase letters, digits and hyphens` | rename the file, for example `jane-doe.md` |
| `unknown field 'rol' (did you mean 'roles'?)` | fix the spelling of the line |
| `missing required field 'roles'` | add the line shown in the message, for example `roles: [grad]` |
| `roles: unknown tag '...'` | use one of the tags listed in the message |
| `roles needs at least one of ...` | `alumni` goes next to a role, for example `roles: [grad, alumni]` |
| `` `end:` is set but `alumni` is not in `roles` `` | add `alumni` to `roles`, or delete the `end:` line while you are still in the lab |
| `author 'Doe, J' could be Jane Doe (People page)...` | in the paper's `author` line, write the first name in full: `Doe, Jane` if it is her, or the other person's first name if it is someone else |
| `... is not valid YAML` | a value with a colon in it needs quotes, for example `current_position: "Lab: Example"` |
| `rename the image to 'jane-doe.jpg'` | the picture name must be lowercase and match your page name (or the paper's `.bib` name) |
| `images do not go in this folder` | a picture was uploaded next to the text files: move it to `content/images/` |
| `this image doesn't match any person, paper or research theme` | a warning: the picture's name doesn't match any page or paper, so it isn't shown; rename it |
| `the name '...' belongs to both a person and a ...` | two kinds of file share a name, so the picture can't be paired; rename one of the files |
| `there are two images named '...'` | `jane-doe.jpg` and `jane-doe.png` both exist: delete one |
| `contains GPS location data` | remove the location from the original photo and upload it again (see [Update your profile](UPDATE-PROFILE.md)) |
| `no valid BibTeX entry found` | the `.bib` file is empty or has unbalanced `{ }` braces or a missing comma |
| `contains 2 entries` | put each paper in its own `.bib` file |
| `entry '...' is missing: year` | add `year = {2026},` |
| `BibTeX key '...' is also used in ...` | change the word after `@article{` so it's unique |
| `` `month` must be a number from 1 to 12 `` | write `month = {3}` or `month = {mar}` |
| `` `pmid` must be just the number `` | write only the digits, for example `pmid = {12345678}` |
| `` `cofirst` (or `corresponding`, `senior`) lists ..., who is not among the authors `` | use last names exactly as they appear in the author list |

Warnings (yellow lines in the same step) don't stop the build, for example "an alumnus needs both `start:` and `end:` years". Fix them when you can.

Still stuck? Ask the lab's website maintainer and send them the error text.

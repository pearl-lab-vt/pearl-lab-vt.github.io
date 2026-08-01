# Sponsor logos — where to get the official files

Drop each file into this folder using the exact filename in the table. The site
reads `data/sponsors.json`, and any entry whose file is missing renders as the
sponsor's name in type instead, so a missing logo never breaks the page.

**Do not** recreate, redraw, recolour, or trace these marks, and do not pull them
from logo-aggregator sites such as freelogovectors, 1000logos, seeklogo, or
logo.dev. Those files are frequently outdated or wrong, and using them breaches
the owners' brand rules. Download from the official source in every case.

| Filename | Organization | Official source |
|---|---|---|
| `nsf.png` | U.S. National Science Foundation | NSF Brand Identity Portal — <https://mediahub.nsf.gov> (linked from <https://www.nsf.gov/policies/brand>) |
| `doe-awardee.png` | U.S. Department of Energy | DOE Awardee Logo and Branding Guidelines — <https://www.energy.gov/doe-awardee-logo-and-branding-guidelines> |
| `sony.png` | Sony | Request from your Sony program contact; see the Sony Group Visual Identity guidelines |
| `amazon.png` | Amazon | Request from your Amazon program contact |
| `vt-engineering.png` | Virginia Tech College of Engineering | VT Brand Center unit lockups — <https://brand.vt.edu/identity/lockups.html> (requires VT login) |

Prefer SVG when the source offers it; change the extension in
`data/sponsors.json` to match whatever you actually download. PNG at roughly
600 px wide is plenty for the strip.

Logos are shown at a uniform height on a white plate, unmodified, at full
colour, in both light and dark mode. That is deliberate: nearly every brand
policy here forbids recolouring, adding effects, or placing the mark on a
background that compromises contrast.

## Permission status, in brief

**NSF.** The clearest case. NSF's brand policy states the logo "may only be used
with authorized permission from the agency," and that permission is built into
the award terms for recipients acknowledging support on websites and
publications. It may not be used to imply endorsement of a product or service,
or to imply employment by or affiliation with NSF.

**DOE.** DOE publishes a logo specifically for this purpose. Its awardee
guidelines say the identifiers are "meant to be used by small businesses, other
companies, universities, consortia, and other funding recipients to
self-identify themselves as official DOE Awardees." Use that awardee logo, not
the official DOE seal — the seal is separately regulated under 10 CFR Part 1002.

**Virginia Tech.** The Brand Center permits downloads by "authorized employees,"
which covers you, but the College of Engineering lockup sits behind VT login,
so nobody else can retrieve it for you.

**Sony and Amazon.** Both are private companies whose trademark guidelines
require written approval for third-party use of their marks. Amazon's brand
usage policy states that "other uses of the Amazon brand require review and
written approval by Amazon." A research award does not by itself grant logo
rights. Ask your program contact at each company for the approved logo file and
written confirmation that you may display it as a sponsor. Until that comes
back, listing the sponsor by name in text carries no such restriction and is
what the site does when the file is absent.

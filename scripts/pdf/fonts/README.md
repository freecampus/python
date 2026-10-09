# Embedded Unicode glyph subsets

The main book fonts are the DejaVu family supplied by the build environment.
These two small, renamed TrueType subsets supply the CJK characters and emoji
used by the Foundations examples. They are embedded in the PDF so readers do not
need those fonts installed. Their source notices and licenses are retained here
and reproduced in the book.

- `freecampus-unicode.ttf`: Noto Sans JP, regular instance of
  `Sans/Variable/TTF/Subset/NotoSansJP-VF.ttf`, from
  https://github.com/notofonts/noto-cjk at
  `f8d157532fbfaeda587e826d4cd5b21a49186f7c`.
- `freecampus-symbols.ttf`: regular instance of
  `ofl/notoemoji/NotoEmoji[wght].ttf`, from https://github.com/google/fonts at
  `2eb0b48d5f760f62e286216f0859a8c540dbc1bd`.

Both were instanced at weight 400 with fontTools, then subset to the characters
present in the course. Family, unique, full, and PostScript names were renamed
to FreeCampus Unicode Subset / FreeCampus Symbols Subset. Original copyright and
license metadata remain intact. No generated PDF is tracked here.

When new examples introduce characters outside the embedded fonts, the book
build fails with the missing Unicode code point. Update the appropriate subset
from the same upstream font with fontTools instead of replacing the text or
allowing a missing-glyph box. The automated font-coverage test checks the
complete Foundations source corpus.

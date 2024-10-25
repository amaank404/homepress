0.1.0

- Initital Release

  0.1.1

- Command Line Interface (CLI) added
- Fixed Right to Left, separation for midpage binding pdf algorithm

  0.3.0

- Added multi stacks midpage binding algorithm
- Added a parameter input_page_range to single stack midpage algorithm
- renamed cli to "homepress" from "homepress_cli"

  0.3.1

- Fixed an error where input_page_range is None for single stack midpage.

  2.0.0

Project was rewritten completely

- Project now uses `Renderer` in `homepress/renderer`
  - `MultiRenderer` - To combine multiple renderers
  - `MuPDFRenderer` - Use MuPDF Renderer as the backend to render a few document formats
  - `PageRangeRenderer` - Render only the subset pages of a given child renderer
  - `PILRenderer` - Use PIL (Pillow) to render input files
  - `Renderer` - The abstract class for renderers
- class `Press` provides the methods to perform operations on given `Renderer` or input files.
  - Midpage Binding Algorithm
  - Multi-stack Midpage Binding Algorithm
  - Images (render pages as imgages)
  - Merge (render pages as images and then save them in a single pdf)
  - Text (extract text from documents supporting it)
- cli rewritten and can be called from `homepress.cli.app()`
- `bindermath.py` - Removed single sided algorithm
- `Progress` (`homepress/progress.py`) now contains generalised progress tracking mechanism to track progress from a function in real time.
- `homepress.layout.pages` - Contains common page sizes (w/h ratio and width)
  - A4
  - Letter
  - Ledger
  - Legal
- Rewrote the documentation and readme.md
- Added artwork under logos
- Added .pre-commit to repository
- Dependencies boiled down to "pymupdf" and "pillow"

# 2.0.1

- Fix behaviour for file not found errors

# 2.0.2

- Fix a render preview bug

# 2.1.0

- Added integration and unit tests
- Added minimum resolution checks
- Added lazy loading to pymupdf renderer
- Files retrieved from directories or recursive sub directories are sorted by a new algorithm named name-number sort that looks for numerical and string parts separately
- Fix multi page renderer to not exceed page range than what's available
- Add saftey check for stack size

The Wax Linter extension provides powerful linting capabilities for HTML, JavaScript, TypeScript, JSX, TSX, Astro, PHP, Svelte and Vue files. It helps developers identify and fix issues related to accessibility, code quality, and best practices.

### Screenshots

Linter picks up on accessibility errors in html code and lists them.

For example:
![Linting in Action](https://assets2.wallyax.com/common/sublime-linter.png)

## Requirements

You need an API key to start using the WAX Linter. You can get a free API key from [WallyAX Developer Portal](https://developer.wallyax.com)

Installation
------------

   * Get files from the [package archive](https://github.com/wallyax/wax-sublime-text-plugin/archive/main.zip)
   * unzip to Packages/WAXLint directory (use "2" or "3" depending on which version you have):
      * Linux: ~/.config/sublime-text-2/Packages/WAXLint
      * Mac: ~/Library/Application Support/Sublime Text 2/Packages/WAXLint
      * Windows: %APPDATA%/Sublime Text 2/Packages/WAXLint

Usage
-----
 - Bring up the Command Palette (```Command+Shift+P``` on OS X, ```Control+Shift+P``` on Linux/Windows), then type ```Open WAX Lint Settings```  and then add the generated api key.   
  - Restart the Sublime Text to start linting.
 - Wax Linter plugin automatically lints on any file open or save events of the respective file.


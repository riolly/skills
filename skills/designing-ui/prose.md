# Prose

The branch of [`designing-ui`](SKILL.md) for long-form text and rendered markdown: articles, docs pages, chat messages.

Done when the content is driven by the three controls, holds its measure, and stays stable while streaming.

- **Three controls**: size, leading, and flow, the space between blocks. Heading sizes, list indents and the gaps around headings and rules derive from these three.
- **A preset per context**, such as chat, docs or reading. Each preset sets the three controls.
- **Prose may size itself from its container**, so the same content fits a chat bubble and an article. This is the one place interface text leaves the fixed scale.
- **Measure**: 45 to 75 characters a line, set as a max-width on the wrapper. Leading rises with line length, up to about 2.
- **Streaming-safe**: each block carries its own spacing above it and is styled from its own selector, so an appended block leaves every earlier block unchanged. Layout rules that depend on what follows, such as last-child and has(), fail this.
- **Alignment**: left-aligned by default. Justified text is hyphenated. Titles use balanced wrapping.

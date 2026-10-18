---
description: Literary Ghostwriter - Write in the style of seven literary masters
agent: build
---

Load the literary-ghostwriter skill and create a work in the specified author's style.

## Supported Authors

| Command | Author | Style Highlights |
|---------|--------|-----------------|
| `/literary shakespeare` | William Shakespeare | Poetic language, dramatic conflict, soliloquy |
| `/literary zweig` | Stefan Zweig | Psychological depth, elegant narrative, fate |
| `/literary calvino` | Italo Calvino | Lightness & exactitude, fantastic fables, experimental |
| `/literary luxun` | Lu Xun | Concise & sharp, critical, plain sketch |
| `/literary laoshe` | Lao She | Beijing dialect, humorous, colloquial |
| `/literary jinyong` | Jin Yong | Classical-modern blend, chapter format, chivalry |
| `/literary gulong` | Gu Long | Minimalist, poetic, short sentences, suspense |

## Usage Examples

```bash
/literary luxun Write a story about a witness to injustice
/literary laoshe Write a story set in old Beijing
/literary jinyong Write about a young swordsman entering the martial arts world
/literary gulong Write about a lonely blade warrior
```

## Style Transfer

Re-voice existing text into another author's style. Only the language changes; plot, characters and scene stay the same.

| Command | Description |
|---------|-------------|
| `/literary transfer <src->target> <text>` | Specify source and target author, e.g. `gulong->laoshe` |
| `/literary transfer <target> <text>` | Omit source; the system detects and states it |
| `/literary transfer verify <text> <target>` | Line-by-line compare against the source, score fidelity |
| `/literary transfer matrix` | Show the inter-author transfer matrix |

```bash
/literary transfer gulong->laoshe "The cold wind cut like a blade."
/literary transfer laoshe->luxun src.md
/literary transfer luxun "He said it without any expression on his face."
```

The four-layer re-voicing method and reproducible samples live in `rules/style-transfer.md`.

## Writing Requirements

1. **Authentic Style**: Accurately capture the author's characteristic style
2. **Native Language**: Both Chinese and English at native level
3. **Theme Alignment**: Flexibly apply style to the given topic
4. **Complete Work**: Full story or article with proper ending

$ARGUMENTS
[English](./README.md) | [简体中文](./README-zh.md)

# lucide-icons-compose-skill

`lucide-icons-compose-skill` is the implementation repository for `lucide-icons-compose-skill`. It is responsible for exactly two things:

- Searching Lucide icons and obtaining the correct SVG
- Calling Valkyrie CLI to generate Jetpack Compose `ImageVector`

## Structure

```text
.
├── SKILL.md
├── references/
│   └── backend-contract.md
├── agents/
│   └── openai.yaml
└── engine/
    ├── __init__.py
    ├── cli.py
    ├── lucide_index.py
    ├── update_lucide_index.py
    ├── scripts/
    │   ├── resolve_backend.py
    │   └── run_skill_backend.py
    ├── data/
    │   └── lucide-index.json
    └── valkyrie-cli/
```

Key files:

- [SKILL.md](./SKILL.md): skill entry documentation
- [references/backend-contract.md](./references/backend-contract.md): backend contract
- [engine/scripts/run_skill_backend.py](./engine/scripts/run_skill_backend.py): backend bootstrap and execution entry
- [engine/cli.py](./engine/cli.py): main backend CLI implementation
- [engine/lucide_index.py](./engine/lucide_index.py): Lucide index, search, and SVG fetching
- [engine/data/lucide-index.json](./engine/data/lucide-index.json): local Lucide metadata index

## Usage

Via the skill backend entrypoint:

```bash
python engine/scripts/run_skill_backend.py search arrow left
python engine/scripts/run_skill_backend.py generate arrow-left --config /path/to/config.json
```

This helper prevents its own `__pycache__` from being written back into the repository. Bytecode and temporary files produced by the actual backend run are written under the current project's `.cache/` subtree.

Debug the backend directly:

```bash
python -X pycache_prefix=.cache/pycache -m engine.cli search arrow left
python -X pycache_prefix=.cache/pycache -m engine.cli generate arrow-left --config /path/to/config.json
```

## Configuration

The `generate` command requires the caller to provide a config file explicitly, or to point to one with the `LUCIDE_ICONS_COMPOSE_CONFIG` environment variable.

Recommended filename at the caller project root:

- `lucide-icons-compose.config.json`

Config fields:

- `target_dir`: Kotlin source output root; supports either an absolute path or a path relative to the config file location
- `package`: output package name
- `object_class_extension`: optional carrier object filename, for example `Icons.kt`

When `object_class_extension` is non-empty, the workflow validates or creates a minimal carrier `object` file in the target package directory, then generates the `ImageVector` as an extension property.

Minimal config example:

```json
{
  "target_dir": "D:\\Code\\Demo\\src\\commonMain\\kotlin",
  "package": "io.github.lucide.icons",
  "object_class_extension": "Icons.kt"
}
```

If the config file is already in the project root, a relative path also works:

```json
{
  "target_dir": "src\\commonMain\\kotlin",
  "package": "io.github.lucide.icons",
  "object_class_extension": "Icons.kt"
}
```

## Project-side AGENTS.md

If this skill is used through Codex inside an application repository, it is recommended to place a minimal `AGENTS.md` at the project root so the caller knows where to read config from and what constraints the generated output must satisfy.

Example:

```md
# Project Instructions

- Use `$lucide-icons-compose-skill` when generating Lucide Compose icons
- Read `lucide-icons-compose.config.json` from the project root before generation
- The output directory must be `target_dir + package path`
- If `object_class_extension` is non-empty, first ensure the corresponding Kotlin carrier file exists in the target package directory
- If `object_class_extension = Icons.kt`, the generated result must be `val Icons.IconName: ImageVector`
- If search results are not unique, do not guess silently; an explicit selection is required
```

The minimal Kotlin carrier file can be:

```kt
package io.github.lucide.icons

object Icons
```

The generated result should look like:

```kt
package io.github.lucide.icons

import androidx.compose.ui.graphics.vector.ImageVector

val Icons.ArrowLeft: ImageVector
    get() = TODO()
```

## Lucide Index

This repository uses [engine/data/lucide-index.json](./engine/data/lucide-index.json) to provide local Lucide search capability.

Refresh the index:

```bash
python -m engine.update_lucide_index
```

## Cache

When used through the skill, all caches, temporary files, and Python bytecode are written into the caller project's `.cache/` subtree, including:

- Python `pycache`
- Temporary SVG files
- Lucide SVG cache
- Other intermediate artifacts

If the backend is seeded into the caller project's `.cache/lics/backend`, the backend's own temporary directory still stays inside that cached copy's `.cache/`, for example `.cache/lics/backend/.cache/pycache`.
When multiple processes try to seed or refresh the same backend cache at the same time, the helper serializes that step with a sibling `backend.lock`.

## Runtime Dependencies

- Python 3.10+
- Java 21+
- Official `engine/valkyrie-cli/` release runtime

Notes:

- `engine/valkyrie-cli/` is not automatically provided by the Git remote
- If `generate` is executed from a remote clone or a backend cached inside another project, make sure `engine/valkyrie-cli/` is already present in that backend root
- Alternatively, reseed the cache with `--backend-path` using a local backend that already includes the runtime

## Upstream References

- [lucide-icons-mcp-server](https://github.com/matracey/lucide-icons-mcp-server)
- [Valkyrie](https://github.com/ComposeGears/Valkyrie)

# Optional companion skills

| Source | Installed peer folder | Dependency |
|---|---|---|
| Repository root | `freecad-mcp-parametric-cad` | Existing FreeCAD/MCP runtime |
| [blockfolk-figure-design](blockfolk-figure-design/README.md) | `blockfolk-figure-design` | General FreeCAD skill |

Source nesting is not runtime discovery. Use the root `install_skills.py` with `core`, `blockfolk` or `all` and an explicitly resolved skill root. The core stays useful on its own and its installer payload excludes this directory.

Blockfolk v1.0.0 is imported from verified completed bytes. The [publication record](blockfolk-figure-design/PUBLICATION.md) lists privacy-related packaging changes. Mechanical helper code and nominal engineering knowledge are preserved. Do not copy the general CAD implementation into a companion or promote a configuration-specific physical result into a universal guarantee.

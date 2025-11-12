# Entity Relationship Diagrams (ERD) - Setup Guide

This directory contains the Entity Relationship Diagrams for FinCloud's database schema.

## Quick Start

### Option 1: Automated Generation (Recommended)

Run the provided script to generate all ERD diagrams as PNG files:

```bash
# From the FinCloud root directory
./docs/architecture/generate-erd.sh
```

This will create:
- `erd-budget-service.png` - Budget Service database schema
- `erd-portfolio-service.png` - Portfolio Service database schema
- `erd-system-overview.png` - Complete system overview
- `erd.png` - Symbolic link to system overview

### Option 2: Manual Generation with Mermaid CLI

```bash
# Install Mermaid CLI globally
npm install -g @mermaid-js/mermaid-cli

# Navigate to architecture docs
cd docs/architecture

# Generate each diagram
mmdc -i budget-service.mmd -o erd-budget-service.png -b transparent
mmdc -i portfolio-service.mmd -o erd-portfolio-service.png -b transparent
mmdc -i system-overview.mmd -o erd-system-overview.png -b transparent
```

### Option 3: Online Visualization

1. Visit [Mermaid Live Editor](https://mermaid.live/)
2. Copy the content from any `.mmd` file
3. View the diagram in real-time
4. Export as PNG/SVG

### Option 4: GitHub/GitLab Markdown

The Mermaid diagrams in `erd-diagram.md` will render automatically in:
- GitHub README and markdown files
- GitLab documentation
- Many modern markdown viewers

### Option 5: Visual Studio Code

1. Install the "Markdown Preview Mermaid Support" extension
2. Open `erd-diagram.md`
3. Use the markdown preview pane
4. Export or screenshot as needed

### Option 6: draw.io Manual Creation

For maximum customization:

1. Visit [draw.io](https://app.diagrams.net/)
2. Use File → New → Create New Diagram
3. Select "Entity Relation" template
4. Refer to `database-schema.md` for complete table definitions
5. Export as PNG with transparent background

**Recommended settings:**
- Format: PNG
- Background: Transparent
- Border width: 10px
- Quality: High (300 DPI for print)

## Files in This Directory

| File | Description |
|------|-------------|
| `database-schema.md` | Complete database schema documentation (source of truth) |
| `erd-diagram.md` | Mermaid ER diagrams in markdown format |
| `budget-service.mmd` | Budget Service ERD (Mermaid source) |
| `portfolio-service.mmd` | Portfolio Service ERD (Mermaid source) |
| `system-overview.mmd` | System overview ERD (Mermaid source) |
| `generate-erd.sh` | Automated generation script |
| `ERD-README.md` | This file |
| `erd.png` | Main ERD diagram (to be generated) |
| `erd-budget-service.png` | Budget Service ERD (to be generated) |
| `erd-portfolio-service.png` | Portfolio Service ERD (to be generated) |
| `erd-system-overview.png` | System overview ERD (to be generated) |

## Viewing the Schema

### Text-Based (No Tools Required)

The complete schema is documented in `database-schema.md` with:
- All table definitions
- All column types and constraints
- All relationships and foreign keys
- Indexes and performance optimizations
- Validation rules

### Diagram-Based

Choose any of the methods above to generate visual diagrams.

## Troubleshooting

### Mermaid CLI Issues

If you encounter issues with Mermaid CLI:

**Puppeteer/Chromium errors:**
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install -y chromium-browser

# Set Puppeteer to use system Chromium
export PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
```

**Permission errors:**
```bash
# Use npx instead of global install
npx -p @mermaid-js/mermaid-cli mmdc -i input.mmd -o output.png
```

**Memory issues:**
```bash
# Increase Node memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
```

### Alternative: Use Docker

```bash
# Run Mermaid CLI in Docker
docker run --rm -v $(pwd):/data minlag/mermaid-cli \
  -i /data/budget-service.mmd \
  -o /data/erd-budget-service.png \
  -b transparent
```

## Schema Maintenance

When updating the database schema:

1. Update `database-schema.md` (source of truth)
2. Update corresponding `.mmd` files
3. Regenerate PNG files using the script
4. Commit all changes including both source and generated files
5. Update the `Last Updated` date in documentation

## Integration with Documentation Site

The generated ERD diagrams are automatically included in:
- MkDocs documentation site
- README files
- Architecture documentation
- API documentation

To rebuild the documentation site with updated ERDs:

```bash
# From FinCloud root
mkdocs build
```

## Need Help?

- **Database Schema Questions**: See `database-schema.md`
- **Mermaid Syntax**: https://mermaid.js.org/syntax/entityRelationshipDiagram.html
- **Diagram Issues**: Try the online Mermaid Live Editor first
- **General Questions**: Open an issue on GitHub

---

**Last Updated**: 2025-11-12

#!/bin/bash
# Script to generate ERD diagrams from Mermaid files

set -e

echo "FinCloud ERD Generator"
echo "====================="
echo ""

# Check if we're in the right directory
if [ ! -d "docs/architecture" ]; then
    echo "Error: Please run this script from the FinCloud root directory"
    exit 1
fi

cd docs/architecture

echo "Installing Mermaid CLI (if not already installed)..."
npm install -g @mermaid-js/mermaid-cli || {
    echo "Note: Global install failed. Trying with npx..."
    USE_NPX=true
}

echo ""
echo "Generating ERD diagrams..."
echo ""

# Function to generate diagram
generate_diagram() {
    local input=$1
    local output=$2
    local name=$3

    echo "Generating $name..."

    if [ "$USE_NPX" = true ]; then
        npx -p @mermaid-js/mermaid-cli mmdc -i "$input" -o "$output" -b transparent -t neutral
    else
        mmdc -i "$input" -o "$output" -b transparent -t neutral
    fi

    if [ -f "$output" ]; then
        echo "✓ Created: $output"
    else
        echo "✗ Failed to create: $output"
    fi
}

# Generate all diagrams
generate_diagram "budget-service.mmd" "erd-budget-service.png" "Budget Service ERD"
generate_diagram "portfolio-service.mmd" "erd-portfolio-service.png" "Portfolio Service ERD"
generate_diagram "system-overview.mmd" "erd-system-overview.png" "System Overview ERD"

echo ""
echo "Creating combined erd.png (symlink to system overview)..."
ln -sf erd-system-overview.png erd.png
echo "✓ Created: erd.png"

echo ""
echo "Done! ERD diagrams generated successfully."
echo ""
echo "Generated files:"
echo "  - erd-budget-service.png"
echo "  - erd-portfolio-service.png"
echo "  - erd-system-overview.png"
echo "  - erd.png (link to system overview)"
echo ""

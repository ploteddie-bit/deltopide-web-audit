#!/bin/bash
set -euo pipefail

# =============================================================================
# Deltopide Web Audit — Script de build complet
# Compile le moteur Rust/WASM, prepare l'extension Chrome, genere le zip
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUST_DIR="$SCRIPT_DIR/audit-engine-rs"
EXT_DIR="$SCRIPT_DIR/extension"
DIST_DIR="$SCRIPT_DIR/dist"
WASM_PKG="$RUST_DIR/pkg"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; exit 1; }

# =============================================================================
# 1. Verification des prerequis
# =============================================================================
info "Verification des prerequis..."

command -v cargo    >/dev/null 2>&1 || fail "cargo non trouve. Installer Rust : https://rustup.rs"
command -v wasm-pack >/dev/null 2>&1 || fail "wasm-pack non trouve. Installer : cargo install wasm-pack"
command -v node     >/dev/null 2>&1 || fail "node non trouve. Installer Node.js"

CARGO_V=$(cargo --version)
WASM_PACK_V=$(wasm-pack --version)
NODE_V=$(node --version)

ok "cargo       : $CARGO_V"
ok "wasm-pack   : $WASM_PACK_V"
ok "node        : $NODE_V"

TERSER_AVAILABLE=false
if command -v terser >/dev/null 2>&1; then
    TERSER_V=$(terser --version 2>/dev/null || echo "?")
    ok "terser      : $TERSER_V"
    TERSER_AVAILABLE=true
else
    warn "terser non trouve — minification JS desactivee (npm i -g terser)"
fi

# =============================================================================
# 2. Lecture de la version depuis manifest.json
# =============================================================================
VERSION=$(node -e "console.log(JSON.parse(require('fs').readFileSync('$EXT_DIR/manifest.json','utf8')).version)")
info "Version extension : $VERSION"

# =============================================================================
# 3. Compilation Rust -> WASM
# =============================================================================
info "Compilation Rust -> WASM (release)..."
cd "$RUST_DIR"
wasm-pack build --target web --release --out-dir "$WASM_PKG"
cd "$SCRIPT_DIR"

if [ ! -f "$WASM_PKG/audit_engine_bg.wasm" ]; then
    fail "Fichier WASM non genere dans $WASM_PKG/"
fi
ok "Compilation WASM terminee"

# =============================================================================
# 4. Copie des fichiers WASM dans extension/
# =============================================================================
info "Copie des fichiers WASM dans extension/..."
cp "$WASM_PKG/audit_engine_bg.wasm" "$EXT_DIR/audit_engine_bg.wasm"
cp "$WASM_PKG/audit_engine.js"      "$EXT_DIR/audit_engine.js"
ok "Fichiers WASM copies dans extension/"

# =============================================================================
# 5. Minification JS (optionnelle, sauf background.js qui importe WASM)
# =============================================================================
MINIFIED_COUNT=0
if [ "$TERSER_AVAILABLE" = true ]; then
    info "Minification JS avec terser..."
    for jsfile in "$EXT_DIR"/*.js; do
        basename=$(basename "$jsfile")
        # Ne pas minifier background.js (import WASM dynamique)
        # Ne pas minifier audit_engine.js (genere par wasm-pack)
        if [ "$basename" = "background.js" ] || [ "$basename" = "audit_engine.js" ]; then
            warn "Skip minification : $basename (import WASM)"
            continue
        fi
        terser "$jsfile" --compress --mangle -o "$jsfile.min" 2>/dev/null
        if [ -f "$jsfile.min" ]; then
            mv "$jsfile.min" "$jsfile"
            MINIFIED_COUNT=$((MINIFIED_COUNT + 1))
        fi
    done
    ok "$MINIFIED_COUNT fichiers JS minifies"
else
    warn "Minification JS sautee (terser absent)"
fi

# =============================================================================
# 6. Creation du zip dans dist/
# =============================================================================
info "Creation du zip..."
mkdir -p "$DIST_DIR"
ZIP_NAME="deltopide-web-audit-v${VERSION}.zip"
ZIP_PATH="$DIST_DIR/$ZIP_NAME"

# Supprimer l'ancien zip de meme version s'il existe
rm -f "$ZIP_PATH"

cd "$EXT_DIR"
zip -r "$ZIP_PATH" . \
    -x "*.map" \
    -x ".DS_Store" \
    -x "*.tmp"
cd "$SCRIPT_DIR"

if [ ! -f "$ZIP_PATH" ]; then
    fail "Zip non genere"
fi
ok "Zip cree : $ZIP_PATH"

# =============================================================================
# 7. Resume du build
# =============================================================================
WASM_SIZE=$(du -h "$EXT_DIR/audit_engine_bg.wasm" | cut -f1)
WASM_SIZE_BYTES=$(stat -c%s "$EXT_DIR/audit_engine_bg.wasm" 2>/dev/null || stat -f%z "$EXT_DIR/audit_engine_bg.wasm" 2>/dev/null)
ZIP_SIZE=$(du -h "$ZIP_PATH" | cut -f1)
FILE_COUNT=$(unzip -l "$ZIP_PATH" | tail -1 | awk '{print $2}')

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  BUILD TERMINE — Deltopide Web Audit${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "  Version      : ${BLUE}${VERSION}${NC}"
echo -e "  WASM         : ${BLUE}${WASM_SIZE}${NC} (${WASM_SIZE_BYTES} bytes)"
echo -e "  Fichiers     : ${BLUE}${FILE_COUNT}${NC} fichiers dans le zip"
echo -e "  JS minifies  : ${BLUE}${MINIFIED_COUNT}${NC}"
echo -e "  Zip          : ${BLUE}${ZIP_PATH}${NC} (${ZIP_SIZE})"
echo ""
echo -e "  ${YELLOW}Prochaine etape :${NC} chrome://extensions → Charger l'extension non empaquetee"
echo ""

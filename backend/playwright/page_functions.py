

def wait_for_dom_change(page):
    # 1. DOM ready
    page.wait_for_load_state("domcontentloaded")
    # 2. Try network idle (don't fully trust it)
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except:
        pass

    page.wait_for_timeout(2000)
    return page.content()



# -------------------------------
# ✅ DOM EXTRACTION
# -------------------------------
def extract_dom_tree(page):
    return page.evaluate("""
    () => {

        const IMPORTANT_TAGS = new Set([
            'INPUT', 'BUTTON', 'A', 'SELECT', 'TEXTAREA',
            'LABEL', 'FORM'
        ]);

        function isVisible(el) {
            const style = window.getComputedStyle(el);
            return style &&
                   style.display !== 'none' &&
                   style.visibility !== 'hidden';
        }

        function getText(el) {
            return el.innerText ? el.innerText.trim().slice(0, 50) : null;
        }

        function cleanProps(obj) {
            return Object.fromEntries(
                Object.entries(obj).filter(([_, v]) => v !== null && v !== undefined && v !== '')
            );
        }

        function isImportant(el) {
            if (IMPORTANT_TAGS.has(el.tagName)) return true;

            // Relaxed condition for containers
            if (['DIV', 'SPAN'].includes(el.tagName)) {
                return (
                    el.id ||
                    el.getAttribute('data-testid') ||
                    el.getAttribute('role') ||
                    getText(el)
                );
            }

            return false;
        }

        function extract(el) {
            if (!el) return null;

            const children = [];

            for (const child of el.children) {
                const extracted = extract(child);
                if (extracted) children.push(extracted);
            }

            const hasChildren = children.length > 0;
            const important = isImportant(el);

            // ⚠️ FIX: don't kill root / structure
            if (!important && !hasChildren && el !== document.body) {
                return null;
            }

            const node = cleanProps({
                tag: el.tagName,
                id: el.id || null,
                name: el.getAttribute('name'),
                dataTestId: el.getAttribute('data-testid'),
                placeholder: el.getAttribute('placeholder'),
                role: el.getAttribute('role'),
                text: getText(el),
                children: hasChildren ? children : null
            });

            return node;
        }

        return extract(document.body);
    }
    """)


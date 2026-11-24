from pathlib import Path


INDEX_PATH = Path("build/web/index.html")
WEB_ZIP_PATH = Path("build/web.zip")


def main() -> None:
    index = INDEX_PATH.read_text(encoding="utf-8")
    replacement = """        canvas.emscripten {
            border: 0px none;
            background-color: transparent;
            width: 768px;
            height: 624px;
            max-width: 100vw;
            max-height: 100vh;
            object-fit: contain;
            image-rendering: pixelated;
            image-rendering: crisp-edges;
            z-index: 5;

            padding: 0;
            margin: auto;

            position: absolute;
            top: 0;
            bottom: 0;
            left: 0;
            right: 0;
        }
"""
    start = index.find("        canvas.emscripten {")
    if start < 0:
        raise RuntimeError("No se encontro la regla CSS del canvas")
    end = index.find("\n        body {", start)
    if end < 0:
        raise RuntimeError("No se encontro el final de la regla CSS del canvas")
    index = index[:start] + replacement + index[end:]
    INDEX_PATH.write_text(index, encoding="utf-8")

    if WEB_ZIP_PATH.exists():
        import zipfile
        replacement_zip = WEB_ZIP_PATH.with_suffix(".tmp.zip")

        with zipfile.ZipFile(WEB_ZIP_PATH, "r") as source:
            with zipfile.ZipFile(replacement_zip, "w", compression=zipfile.ZIP_DEFLATED) as target:
                for entry in source.infolist():
                    data = INDEX_PATH.read_bytes() if entry.filename == "index.html" else source.read(entry.filename)
                    target.writestr(entry, data)

        replacement_zip.replace(WEB_ZIP_PATH)


if __name__ == "__main__":
    main()

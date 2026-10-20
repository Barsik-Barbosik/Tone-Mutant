"""Build the Windows x64 portable folder using the verified local runtime."""
import os
import shutil
import importlib.metadata
import zipfile
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
import PySide6
import PyInstaller.__main__


def build():
    root = Path(__file__).resolve().parents[1]
    release_root = root / "dist" / "1.4-qt6"
    distribution = release_root / "ToneMutant-ES"
    assert distribution.resolve().is_relative_to(root.resolve())
    os.chdir(root)
    qt_translation = Path(PySide6.__file__).parent / "translations" / "qtbase_es.qm"
    PyInstaller.__main__.run([
        "--noconfirm", "--onedir", "--windowed", "--name=ToneMutant-ES",
        "--icon=" + str(root / "resources/note.ico"), "--distpath=" + str(release_root), "--workpath=.runtime/build/cache",
        "--specpath=.runtime/build", "--paths=" + str(root),
        "--add-data=" + str(root / "resources") + os.pathsep + "resources",
        "--add-data=" + str(root / "captures") + os.pathsep + "captures",
        "--add-data=" + str(qt_translation) + os.pathsep + "translations",
        str(root / "main.py"),
    ])
    # Qt uses Windows' ICU API. A host tool (such as Poppler) on PATH can
    # otherwise cause PyInstaller to bundle an incompatible DLL of the same name.
    for filename in ("icuuc.dll", "icudt78.dll"):
        (distribution / "_internal" / filename).unlink(missing_ok=True)
    (distribution / "config.cfg").write_text("[Synthesizer]\nModel = CT-X700/800\n\n[Expert]\nis_expert_mode_enabled = false\n", encoding="utf-8")
    shutil.copy2(root / "LEEME_PORTATIL.txt", distribution / "LEEME.txt")
    shutil.copy2(root / "LICENSE.md", distribution / "LICENSE.md")
    shutil.copytree(root / "licenses", distribution / "licencias", dirs_exist_ok=True)
    # A virtual environment keeps Python's license in its base installation.
    import sys
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.exists():
        shutil.copy2(python_license, distribution / "licencias" / "Python-LICENSE.txt")
    for package in ("PySide6-Essentials", "shiboken6", "python-rtmidi", "pyinstaller"):
        metadata = importlib.metadata.distribution(package)
        target = distribution / "licencias" / package
        target.mkdir(exist_ok=True)
        (target / "METADATA.txt").write_text(metadata.read_text("METADATA") or "", encoding="utf-8")
        for file in metadata.files or []:
            if "license" in file.name.lower() or "copying" in file.name.lower():
                original = metadata.locate_file(file)
                if original.is_file(): shutil.copy2(original, target / file.name)
    for directory, folders, filenames in os.walk(root):
        folders[:] = [name for name in folders if name not in (".git", ".runtime", "dist", "__pycache__", ".venv", "registros")]
        for filename in filenames:
            source = Path(directory) / filename
            if source.is_symlink() or source.name == "config.cfg" or source.suffix == ".pyc":
                continue
            target = distribution / "fuentes" / source.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    # Refuse to publish a package that cannot import Qt or load its resources.
    with tempfile.TemporaryDirectory(prefix="tone-mutant-check-") as directory:
        report = Path(directory) / "arranque.json"
        subprocess.run([str(distribution / "ToneMutant-ES.exe"), "--self-test", str(report)],
                       cwd=directory, timeout=30, check=True)
        if not json.loads(report.read_text(encoding="utf-8")).get("ok"):
            raise RuntimeError("Falló la comprobación de arranque del ejecutable")
    archive = root / "dist" / "ToneMutant-ES-Windows-x64.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as package:
        for file in sorted(distribution.rglob("*")):
            if file.is_file(): package.write(file, file.relative_to(release_root))
    hasher = hashlib.sha256()
    with archive.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    digest = hasher.hexdigest()
    (root / "dist" / "SHA256.txt").write_text(digest + "  " + archive.name + "\n", encoding="ascii")
    print("Portable:", archive)


if __name__ == "__main__":
    build()

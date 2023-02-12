from pathlib import Path
import shutil

root = Path(__file__).parent

if __name__ == "__main__":
    homecloud_dir = root / "src" / "homecloud"
    template_dir = homecloud_dir / "templates"
    files = [
        file
        for file in homecloud_dir.glob("*.py")
        if "__init__" not in file.stem and "homecloud" not in file.stem
    ]
    for file in files:
        shutil.copy(file, (template_dir / file.name).with_suffix(".txt"))
    shutil.copy(
        homecloud_dir / "client_settings.toml", template_dir / "client_settings.toml"
    )

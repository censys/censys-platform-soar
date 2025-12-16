from pathlib import Path
import re


extracted_manifest_path = Path("censys-platform-soar") / "manifest.json"
replacement_manifest_path = Path("censys-platform-soar") / "replacement_manifest.json"

pattern = r"""manylinux[a-zA-Z0-9\-_]+_(aarch64)"""
replacement = "x86_64"


def replace_platform(match):
    return match.group(0).replace("aarch64", replacement)


def process_line(line: str) -> str:
    if line.strip().startswith('"input_file"'):
        return re.sub(pattern, replace_platform, line)

    return line


with (
    open(extracted_manifest_path) as infile,
    open(replacement_manifest_path, "w") as outfile,
):
    for line in infile:
        outfile.write(re.sub(pattern, replace_platform, line))


replacement_manifest_path.rename(extracted_manifest_path)

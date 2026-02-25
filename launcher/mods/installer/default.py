from pathlib import Path
from shutil import copytree
from typing import Dict
import xml.etree.ElementTree as ET

from launcher.common import folder_to_install
from launcher.tempfile import DefaultTempDir
from launcher.mods.installer.base import BaseInstaller


class DefaultInstaller(BaseInstaller):
    "Installer which is used for ModDB provided mods"

    @staticmethod
    def _read_fomod_directives(dir: Path) -> Dict[Path, Path]:
        module_config = dir / 'fomod' / 'ModuleConfig.xml'
        if not module_config.exists():
            return {}

        return {
            dir / i.attrib['source']: Path(i.attrib['destination'])
            for i in filter(lambda x: x.tag == 'folder', ET.parse(module_config).iter())
        }

    def _write_ini_file(self, inifile: Path) -> None:
        inifile.write_text(
            "[General]\n"
            "gameName=stalkeranomaly\n"
            "modid=0\n"
            f'ignoredversion={self.archive.name}\n'
            f'version={self.archive.name}\n'
            f'newestversion={self.archive.name}\n'
            'category="-1,"\n'
            'nexusFileStatus=1\n'
            f'installationFile={self.archive.name}\n'
            'repository=\n'
            'comments=\n'
            'notes=\n'
            'nexusDescription=\n'
            f'url={self.info.iurl or self.info.url}\n'
            'hasCustomURL=true\n'
            'lastNexusQuery=\n'
            'lastNexusUpdate=\n'
            'nexusLastModified=2021-11-09T18:10:18Z\n'
            'converted=false\n'
            'validated=false\n'
            'color=@Variant(\\0\\0\\0\\x43\\0\\xff\\xff\\0\\0\\0\\0\\0\\0\\0\\0)\n'
            'tracked=0\n'
            '\n'
            '[installedFiles]\n'
            '1\\modid=0\n'
            '1\\fileid=0\n'
            'size=1\n'
        )

    def install(self, to: Path) -> None:
        install_dir = to / self.info.name
        install_dir.mkdir(exist_ok=True)

        with DefaultTempDir(lambda x: self.extract(x), prefix="gamma-launcher-modinstall-") as pdir:
            iterator = [pdir] + ([pdir / i for i in self.info.subdirs] if self.info.subdirs else [])
            fdirectives = self._read_fomod_directives(pdir)
            for i in iterator:
                if pdir != i:
                    print(f'    Installing {i.name} -> {install_dir}')

                if not i.exists():
                    print(f'    WARNING: {i.name} does not exist')

                if i in fdirectives.keys():
                    fdir = install_dir / fdirectives[i]
                    print(f'        Appying FOMOD directive to {i} -> {fdir}')
                    fdir.mkdir(exist_ok=True)
                    copytree(i, fdir, dirs_exist_ok=True)
                    continue

                # Well, I guess it's a feature now.
                # Maybe I'm not that lazy after all
                for gamedir in folder_to_install:
                    pgame_dir = i / gamedir

                    if not pgame_dir.exists():
                        continue

                    copytree(pgame_dir, install_dir / gamedir, dirs_exist_ok=True)

        self._write_ini_file(install_dir / 'meta.ini')

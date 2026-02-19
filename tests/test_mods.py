from unittest import TestCase
from typing import Optional, List

from launcher.mods import read_mod_maker, ModSeparator, ModDBInstaller, ModDefault

from common import data_dir


class ReadModMakerTestCase(TestCase):

    @staticmethod
    def _find_by_name(
        name: str, modlist: List[ModSeparator | ModDBInstaller | ModDefault]
    ) -> Optional[ModSeparator | ModDBInstaller | ModDefault]:
        f = list(filter(lambda x: x.info.name == name, modlist))
        return f[0] if f else None

    def _check_mod(
        self, mod, instanceOf,
        author: str = '', title: str = '',
        url: str = '', iurl: str = '',
        subdirs: List = None
    ) -> None:
        self.assertIsInstance(mod, instanceOf)

        self.assertEqual(mod.info.author, author)
        self.assertEqual(mod.info.title, title)
        self.assertEqual(mod.info.url, url)
        self.assertEqual(mod.info.iurl, iurl)
        self.assertEqual(mod.info.subdirs, subdirs)

    def test_parse_modmaker_list(self) -> None:
        o = read_mod_maker(data_dir / 'modpack_test')
        self.assertEqual(len(o), 9)

        mod = self._find_by_name('G.A.M.M.A. End of List_separator', o)
        self._check_mod(mod, ModSeparator)

        mod = self._find_by_name('Alternative Addons & Patches_separator', o)
        self._check_mod(mod, ModSeparator)

        mod = self._find_by_name('282- GAMMA Loading Screens - CS Eden', o)
        self._check_mod(
            mod, ModDefault, author='CS Eden', title='GAMMA Loading Screens',
            url='https://github.com/Grokitach/gamma_loading_screens/archive/refs/heads/main.zip',
            iurl='https://github.com/Grokitach/gamma_loading_screens',
            subdirs=["gamma_loading_screens-main/CS Eden's GAMMA Loading Screens"]
        )

        mod = self._find_by_name('71- Weapons Reanimation and Rebalance - Blindside', o)
        self._check_mod(
            mod, ModDefault, author='Blindside', title='Weapons Reanimation and Rebalance',
            url='https://github.com/Grokitach/blindside_reanimation_legacy/archive/refs/heads/main.zip',
            iurl='https://www.moddb.com/mods/stalker-anomaly/addons/'
                 'blindsides-weapon-reanimation-and-rebalance-military',
            subdirs=[
                'blindside_reanimation_legacy-main/main',
                'blindside_reanimation_legacy-main/[OPTIONALS]/Vanilla Weapon Stats'
            ]
        )

        mod = self._find_by_name('60- Stash Overhaul - Grokitach', o)
        self._check_mod(
            mod, ModDBInstaller, author='Grokitach', title='Stash Overhaul',
            url='https://www.moddb.com/addons/start/200140',
            iurl='https://www.moddb.com/mods/stalker-anomaly/addons/groks-stash-overhaul-redux',
            subdirs=["00. Grok's Stash Overhaul"]
        )

        mod = self._find_by_name('45- Stealth Overhaul - xcvb', o)
        self._check_mod(
            mod, ModDBInstaller, author='xcvb', title='Stealth Overhaul',
            url='https://www.moddb.com/addons/start/207498',
            iurl='https://www.moddb.com/mods/stalker-anomaly/addons/stealth1',
            subdirs=['Stealth_2.0']
        )

        mod = self._find_by_name('23- THAP Rework - IENCE', o)
        self._check_mod(
            mod, ModDBInstaller, author='IENCE', title='THAP Rework',
            url='https://www.moddb.com/addons/start/217507',
            iurl='https://www.moddb.com/mods/stalker-anomaly/addons/thap-rework',
            subdirs=['T.H.A.P. Rework 2.3']
        )

        mod = self._find_by_name('22- Agressor Reshade - Awene', o)
        self._check_mod(
            mod, ModDBInstaller, author='Awene', title='Agressor Reshade',
            url='https://www.moddb.com/addons/start/213337',
            iurl='https://www.moddb.com/mods/stalker-anomaly/addons/agressor-reshade',
        )

        mod = self._find_by_name('18- Ambient Music Pack - Wojach', o)
        self._check_mod(
            mod, ModDBInstaller, author='Wojach', title='Ambient Music Pack',
            url='https://www.moddb.com/addons/start/183808', subdirs=['00 MAIN FILES']
        )

def create_ini_file(path: str, zipfile: str, url: str) -> None:
    with open(path, 'w') as f:
        f.write(f"""[General]
gameName=stalkeranomaly
modid=0
ignoredversion={zipfile}
version={zipfile}
newestversion={zipfile}
category="-1,"
nexusFileStatus=1
installationFile={zipfile}
repository=
comments=
notes=
nexusDescription=
url={url}
hasCustomUrl=true
lastNexusQuery=
lastNexusUpdate=
nexusLastModified=2021-11-09T18:10:18Z
converted=false
validated=false
color=@Variant(\\0\\0\\0\\x43\\0\\xff\\xff\\0\\0\\0\\0\\0\\0\\0\\0\\0)
tracked=0

[installedFiles]
1\\modid=0
1\\fileid=0
size=1
""")


def create_ini_separator_file(filename: str, **kwargs) -> None:
    with open(filename, 'w') as f:
        f.write("""[General]
modid=0
version=
newestVersion=
category=0
installationFile=

[installedFiles]
size=0
""")

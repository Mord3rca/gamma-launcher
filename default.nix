let
  pkgs = import <nixpkgs> { };
in

with pkgs.python313Packages;

let
  python-unrar = buildPythonPackage rec {
    pname = "unrar";
    version = "0.4";

    src = fetchPypi {
      inherit pname version;
      hash = "sha256-skRHpbkwJL5gDvglVmi6I6MPRRF2V3tpFVnqE1n30WQ=";
    };

    propagatedBuildInputs = with pkgs; [
      pkg-config
      unrar
    ];

    pyproject = true;

    build-system = [
      setuptools
      wheel
    ];

  };
in

buildPythonApplication rec {
  name = "gamma-launcher";
  src = ./.;

  pyproject = true;

  build-system = [
    setuptools
    wheel
  ];

  propagatedBuildInputs = [
    beautifulsoup4
    cloudscraper
    gitpython
    platformdirs
    py7zr
    requests
    tenacity
    tqdm
    python-unrar
    #

    pkgs.pkg-config
  ];

  buildInputs = [
    pkgs.unrar
    pkgs.git
  ];

  postFixup = ''
    wrapProgram $out/bin/gamma-launcher --set UNRAR_LIB_PATH ${pkgs.unrar}/lib/libunrar.so
  '';
}

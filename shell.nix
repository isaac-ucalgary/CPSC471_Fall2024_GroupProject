# shell.nix
# Nix shell for running the python environment for the Home_IMS app
let
  pkgs = import <nixpkgs> { };

  package-mysql-connector =
    let
      use-src = "wheel"; # Options: pypi, github, wheel
    in
    {
      lib,
      buildPythonPackage,
      fetchPypi,
      fetchFromGitHub,
      setuptools,
      wheel,
    }:
    buildPythonPackage rec {
      pname = "mysql-connector-python";
      version = "9.1.0";
      format = if use-src == "wheel" then "wheel" else null;

      src =
        if use-src == "pypi" then
          fetchPypi {
            inherit pname version;
            hash = "sha256-NGJhoq63Q6Oc9muoveXkWTHTE7ds4JRqaabRGH7H0nk=";
          }
        else if use-src == "github" then
          fetchFromGitHub {
            inherit pname version;
            owner = "mysql";
            repo = "mysql-connector-python";
            rev = version;
            hash = "sha256-61TiY5Gq0vYWh0ErMNXOeGXOUnvMazoVUyPxXRQ5eRo=";
          }
        else if use-src == "wheel" then
          pkgs.fetchurl {
            url = "https://files.pythonhosted.org/packages/ac/7e/5546cf19c8d0724e962e8be1a5d1e7491f634df550bf9da073fb6c2b93a1/mysql_connector_python-9.1.0-py2.py3-none-any.whl";
            hash = "sha256-2s8aqE3H3YrpCGJsOuUPzpVtAQUTDHRl/SSKTwNdULE=";
          }
        else
          null;

      # do not run tests
      doCheck = false;

      # specific to buildPythonPackage, see its reference
      pyproject = if format != null then null else true;
      build-system = [
        setuptools
        wheel
      ];
    };

  python = pkgs.python312Full.override {
    self = python;
    packageOverrides = pyfinal: pyprev: {
      mysql-connector = pyfinal.callPackage package-mysql-connector { };
    };
  };

in
pkgs.mkShell {
  packages = with pkgs; [
    (python.withPackages (python-pkgs: with python-pkgs; [
      # select Python packages here
      mysql-connector
      numpydoc
      pyqt6
    ]))
    qt6.full
  ];
}

# shell.nix
let
  pkgs = import <nixpkgs> { };

  package-mysql-connector = {
    lib,
    buildPythonPackage,
    fetchPypi,
    setuptools,
    wheel,
    fetchFromGitHub
    }:
    buildPythonPackage rec {
      pname = "mysql-connector-python";
      version = "9.1.0";
      format = "wheel";

      # src = fetchPypi {
      #   inherit pname version;
      #   hash = "sha256-NGJhoq63Q6Oc9muoveXkWTHTE7ds4JRqaabRGH7H0nk=";
      # };
      # src = fetchFromGitHub {
      #   inherit pname version;
      #   owner = "mysql";
      #   repo = "mysql-connector-python";
      #   rev = version;
      #   hash = "sha256-61TiY5Gq0vYWh0ErMNXOeGXOUnvMazoVUyPxXRQ5eRo=";
      # };
      src = pkgs.fetchurl {
        url = "https://files.pythonhosted.org/packages/ac/7e/5546cf19c8d0724e962e8be1a5d1e7491f634df550bf9da073fb6c2b93a1/mysql_connector_python-9.1.0-py2.py3-none-any.whl";
        hash = "sha256-2s8aqE3H3YrpCGJsOuUPzpVtAQUTDHRl/SSKTwNdULE=";
      };

      # pyprojectFile = pkgs.fetchurl {
      #   url = "https://raw.githubusercontent.com/mysql/mysql-connector-python/refs/tags/9.1.0/pyproject.toml";
      #   hash = "sha256-3Lx76Iy/XxxcHh2NRzx9DBQEOWLlr4C6nVctgtRz4Y8=";
      # };

      # do not run tests
      doCheck = false;

      # specific to buildPythonPackage, see its reference
      # pyproject = true;
      build-system = [
        setuptools
        wheel
      ];
    };

  # python = pkgs.python312Full;
  python = pkgs.python312Full.override {
    self = python;
    packageOverrides = pyfinal: pyprev: {
      mysql-connector = pyfinal.callPackage package-mysql-connector { };
    };
  };

in
pkgs.mkShell {
  packages = [
    (python.withPackages (python-pkgs: [
      # select Python packages here
      python-pkgs.pandas
      python-pkgs.requests
      python-pkgs.mysql-connector
    ]))
  ];
}

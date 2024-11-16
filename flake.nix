{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = inputs: 
  let 
    system = "x86_64-linux";
    pkgs = import inputs.nixpkgs { inherit system; };
  in
  {
    devShells.${system} = {
      default = pkgs.mkShell {
        packages = with pkgs; [
          (python3.withPackages (python-pkgs: [
          ]))
          qt6.full
          python312Packages.pyqt6
          python312Packages.mysql-connector
        ];
      };
    };
  };
}

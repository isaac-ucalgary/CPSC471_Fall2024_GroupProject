{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    #poetry2nix.url = "github:nix-community/poetry2nix";
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
          python3
          qt6.full
          python312Packages.pyqt6
        ];
      };
    };
  };
}

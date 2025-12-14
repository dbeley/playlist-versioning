with import <nixpkgs> { };

let
  pythonPackages = python3Packages;
in pkgs.mkShell {
  buildInputs = [
    python3
    pythonPackages.pytest
    prek
  ];

}

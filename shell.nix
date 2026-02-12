{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-25.11") {} }:

pkgs.mkShellNoCC {
  packages = with pkgs; [
    (python3.withPackages (ps: [ 
      ps.fastapi
      ps.uvicorn

      ps.sqlmodel
      ps.beautifulsoup4
      ps.requests
      ps.uuid6
    ]))
    curl
    jq
  ];
}

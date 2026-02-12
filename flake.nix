{
  description = "Papers Please Backend nix development setup";
  
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, flake-utils, nixpkgs, ...}:
    flake-utils.lib.eachDefaultSystem (
      system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          devShells.default = pkgs.mkShell {
            pacakges = [ #Add python pacakges needed here
              pkgs.python314 #install python311
              pkgs.python314Packages.fastapi
              pkgs.python314Packages.uvicorn
            
              pkgs.python314Packages.sqlmodel
            ];
            shellHook = ''
              python --version
            '';
          };
        }

    );

}

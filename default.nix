{ pkgs ? import
    (fetchTarball {
      name = "jpetrucciani-2024-08-27";
      url = "https://github.com/jpetrucciani/nix/archive/20a58e6a4fccb574caef9b764585609b8d4fbd7d.tar.gz";
      sha256 = "0ksjkhcrd0h5zb8a5x6mbpn491gjs0n7rq9mxxvx9k3mnfjfaq5y";
    })
    { }
}:
let
  inherit (pkgs.hax) ifIsLinux ifIsDarwin;

  name = "bucketstore";
  tools = with pkgs; {
    cli = [
      jq
      nixpkgs-fmt
    ];
    python = [
      poetry
      ruff
      (python311.withPackages (p: with p; [
        boto3

        # dev
        moto
        pytest
        pytest-cov
        tox
      ]))
    ];
  };
  paths = pkgs.lib.flatten [ (builtins.attrValues tools) ];
  env = pkgs.buildEnv {
    inherit name paths; buildInputs = paths;
  };
in
env
